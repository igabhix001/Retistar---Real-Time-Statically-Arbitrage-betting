import os
from datetime import datetime, timedelta  # noqa: F401
import requests
from dotenv import load_dotenv
from fastapi import HTTPException
from app.utils.logger import logger  # noqa: F401

# Load .env variables
load_dotenv()

class BetfairAuthManager:
    """Handles Betfair login and session management."""
    session_token = None
    token_expiration = None

    @classmethod
    def login(cls):
        """Perform non-interactive login to Betfair."""
        required_env_vars = ["BETFAIR_CERT_PATH", "BETFAIR_KEY_PATH", "BETFAIR_API_KEY", "BETFAIR_USERNAME", "BETFAIR_PASSWORD"]
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

       
        resp = requests.post(
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
            )
        if resp.status_code == 200:
                resp_json = resp.json()
                print("Login Status:", resp_json['loginStatus'])
                print("Session Token:", resp_json['sessionToken'])
        else:
                print("Request failed.")
