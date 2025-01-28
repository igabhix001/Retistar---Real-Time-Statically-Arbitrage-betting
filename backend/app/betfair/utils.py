from app.betfair.auth import BetfairAuthManager
from app.config import Config
from fastapi import HTTPException
import time
import requests
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()
api_key = os.getenv("BETFAIR_API_KEY")

def get_headers():
    """Generate headers for Betfair API calls."""
    return {
        "X-Authentication": BetfairAuthManager.get_token(),
        "X-Application": api_key,
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }

def handle_api_error(response):
    """Handle errors from Betfair API responses."""
    global RATE_LIMIT_REMAINING, RATE_LIMIT_RESET

    RATE_LIMIT_REMAINING = response.headers.get("X-RateLimit-Remaining")
    RATE_LIMIT_RESET = response.headers.get("X-RateLimit-Reset")

    if response.status_code == 400:
        raise HTTPException(status_code=400, detail="Bad request to Betfair API.")
    elif response.status_code == 401:
        BetfairAuthManager.login()
    elif response.status_code == 403:
        raise HTTPException(status_code=403, detail="Forbidden by Betfair API.")
    elif response.status_code == 429:
        wait_time = int(RATE_LIMIT_RESET) - int(time.time())
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Retry after {wait_time} seconds."
        )
    elif response.status_code == 500:
        raise HTTPException(status_code=500, detail="Internal server error from Betfair API.")
