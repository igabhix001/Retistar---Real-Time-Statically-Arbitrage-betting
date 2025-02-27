import time
import os
import random
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
from fastapi import HTTPException
from app.logger import logger
import asyncio

# Load .env variables
load_dotenv()

class BetfairAuthManager:
    """Handles Betfair login and session management with automatic reconnection."""
    
    session_token = None
    token_expiration = None
    is_running = False  # Prevent multiple background loops
    
    @classmethod
    def login(cls):
        """Perform non-interactive login to Betfair with a retry mechanism."""
        required_env_vars = [
            "BETFAIR_CERT_PATH", 
            "BETFAIR_KEY_PATH", 
            "BETFAIR_API_KEY", 
            "BETFAIR_USERNAME", 
            "BETFAIR_PASSWORD"
        ]
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if missing_vars:
            raise HTTPException(
                status_code=500,
                detail=f"Missing environment variables: {', '.join(missing_vars)}"
            )

        cert_path = os.getenv("BETFAIR_CERT_PATH")
        key_path = os.getenv("BETFAIR_KEY_PATH")
        api_key = os.getenv("BETFAIR_API_KEY")
        username = os.getenv("BETFAIR_USERNAME")
        password = os.getenv("BETFAIR_PASSWORD")

        max_retries = 1  # Try indefinitely with increasing delay
        delay = 2  # Initial delay in seconds

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    "https://identitysso-cert.betfair.com.au/api/certlogin",
                    cert=(cert_path, key_path),
                    headers={
                        "X-Application": api_key,
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                    data={
                        "username": username,
                        "password": password,
                    },
                    timeout=10  # Set timeout for API call
                )

                # Log response for debugging
                logger.info(f"Response status code: {response.status_code}")
                logger.info(f"Response text: {response.text}")

                if response.status_code == 200:
                    data = response.json()
                    if data.get("loginStatus") == "SUCCESS":
                        cls.session_token = data.get("sessionToken")
                        cls.token_expiration = datetime.now() + timedelta(hours=24)
                        logger.info("Betfair login successful.")
                        return  # Successful login, exit retry loop
                    else:
                        logger.error(f"Betfair login failed: {data}")
                else:
                    logger.error(f"HTTP error {response.status_code}: {response.text}")

            except requests.exceptions.RequestException as e:
                logger.error(f"Betfair login error on attempt {attempt + 1}: {e}")

            # Exponential backoff with jitter
            sleep_time = delay * (2 ** attempt) + random.uniform(0, 1)
            logger.info(f"Retrying login in {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)

        raise HTTPException(status_code=500, detail="Betfair login failed after multiple attempts.")

    @classmethod
    def get_token(cls):
        """Get the current session token or log in if expired."""
        if cls.session_token and cls.token_expiration and cls.token_expiration > datetime.now():
            return cls.session_token

        logger.info("Session expired or not available. Logging in again...")
        cls.login()
        return cls.session_token

    @classmethod
    async def monitor_connection(cls):
        """Continuously monitors the connection and attempts reconnection if needed."""
        if cls.is_running:
            return  # Prevent multiple loops from running
        cls.is_running = True

        while True:
            try:
                if not cls.session_token or cls.token_expiration <= datetime.now():
                    logger.warning("Session expired. Attempting to reconnect...")
                    cls.login()
                else:
                    logger.info("Session is active.")
            except Exception as e:
                logger.error(f"Error in connection monitor: {e}")

            await asyncio.sleep(3600)  # Check every 60 seconds
