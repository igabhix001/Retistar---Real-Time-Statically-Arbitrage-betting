import time
import os
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
from fastapi import HTTPException
from app.utils.logger import logger

# Load .env variables
load_dotenv()

class BetfairAuthManager:
    """Handles Betfair login and session management."""
    session_token = None
    token_expiration = None

    @classmethod
    def login(cls):
        """Perform non-interactive login to Betfair."""
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

        retries = 1
        for attempt in range(retries):
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
                )
                # Log and handle the full response for debugging
                logger.info(f"Response status code: {response.status_code}")
                logger.info(f"Response text: {response.text}")

                # Parse the response
                if response.status_code == 200:
                    data = response.json()
                    if data.get("loginStatus") == "SUCCESS":
                        cls.session_token = data.get("sessionToken")
                        cls.token_expiration = datetime.now() + timedelta(hours=24)  # Adjust based on actual token lifetime
                        logger.info("Betfair login successful.")
                        return
                    else:
                        logger.error(f"Betfair login failed: {data}")
                        raise HTTPException(
                            status_code=500,
                            detail=f"Betfair login failed: {data.get('error')}"
                        )
                else:
                    logger.error(f"HTTP error {response.status_code}: {response.text}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"HTTP error: {response.text}"
                    )

            except requests.exceptions.RequestException as e:
                logger.error(f"Betfair login error on attempt {attempt + 1}: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise HTTPException(status_code=500, detail=f"Betfair login failed: {e}")

    @classmethod
    def get_token(cls):
        """Get the current session token or log in if expired."""
        if cls.session_token and cls.token_expiration and cls.token_expiration > datetime.now():
            return cls.session_token

        cls.login()
        return cls.session_token
