from app.betfair.auth import BetfairAuthManager
from app.config import Config
from fastapi import HTTPException
def get_headers():
    """Generate headers for Betfair API calls."""
    return {
        "X-Authentication": BetfairAuthManager.get_token(),
        "X-Application": Config.BETFAIR_API_KEY,
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }

def handle_api_error(response):
    """Handle errors from Betfair API responses."""
    if response.status_code == 400:
        raise HTTPException(status_code=400, detail="Bad request to Betfair API.")
    elif response.status_code == 401:
        BetfairAuthManager.login()
    elif response.status_code == 403:
        raise HTTPException(status_code=403, detail="Forbidden by Betfair API.")
    elif response.status_code == 500:
        raise HTTPException(status_code=500, detail="Internal server error from Betfair API.")
