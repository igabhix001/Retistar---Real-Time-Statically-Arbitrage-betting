import json
import socket
import ssl
import threading
from app.betfair.auth import BetfairAuthManager
from app.logger import logger
from app.betfair.utils import get_headers

class BetfairStream:
    def __init__(self):
        self.host = 'stream-api.betfair.com'
        self.port = 443
        self.buf_size = 8192
        self.running = False
        self.socket = None
        self.ssl_socket = None
        self.connection_id = None
        self.initialClk = None
        self.clk = None

    def create_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ssl_socket = ssl.wrap_socket(self.socket)
        self.ssl_socket.connect((self.host, self.port))

    def authenticate(self):
        headers = get_headers()
        auth_message = {
            "op": "authentication",
            "appKey": headers["X-Application"],
            "session": headers["X-Authentication"]
        }
        self.send_message(auth_message)

    def subscribe_to_markets(self, market_ids):
        subscribe_message = {
            "op": "marketSubscription",
            "id": 1,
            "marketFilter": {"marketIds": market_ids},
            "marketDataFilter": {"fields": ["EX_BEST_OFFERS", "EX_TRADED", "MARKET_STATE"]}
        }
        if self.initialClk and self.clk:
            subscribe_message["initialClk"] = self.initialClk
            subscribe_message["clk"] = self.clk
        self.send_message(subscribe_message)

    def send_message(self, message):
        message_str = json.dumps(message) + '\r\n'
        self.ssl_socket.send(message_str.encode())

    def receive_messages(self):
        while self.running:
            try:
                data = self.ssl_socket.recv(self.buf_size).decode()
                if data:
                    messages = data.split('\r\n')
                    for message in messages:
                        if message:
                            self.handle_message(json.loads(message))
            except Exception as e:
                logger.error(f"Error receiving message: {e}")
                self.reconnect()

    def handle_message(self, message):
        if message.get('op') == 'connection':
            self.connection_id = message.get('connectionId')
            logger.info(f"Connected with ID: {self.connection_id}")
            self.authenticate()
        elif message.get('op') == 'status':
            if message.get('statusCode') == 'SUCCESS':
                logger.info("Successfully authenticated")
            elif message.get('errorCode') == 'INVALID_SESSION_INFORMATION':
                logger.warning("Session expired. Refreshing...")
                BetfairAuthManager.login()
                self.authenticate()
        elif message.get('op') == 'mcm':
            self.initialClk = message.get('initialClk', self.initialClk)
            self.clk = message.get('clk', self.clk)
        elif message.get('ct') == 'HEARTBEAT':
            logger.info("Heartbeat received.")
        else:
            logger.info(f"Market data received: {message}")

    def reconnect(self):
        logger.info("Reconnecting...")
        self.stop()
        self.start()

    def start(self):
        self.running = True
        self.create_socket()
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

    def stop(self):
        self.running = False
        if self.ssl_socket:
            self.ssl_socket.close()
        if hasattr(self, 'receive_thread'):
            self.receive_thread.join()
