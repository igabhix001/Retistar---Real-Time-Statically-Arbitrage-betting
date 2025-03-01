# ------------------------------------------------
#                     Imports
# ------------------------------------------------
from typing import Dict, Any, List
from fastapi import HTTPException
import requests
import os
from dotenv import load_dotenv
from app.logger import logger
from app.betfair.auth import BetfairAuthManager
import asyncio

# ------------------------------------------------
#               Environment Setup
# ------------------------------------------------
# Load environment variables
load_dotenv()
api_key = os.getenv("BETFAIR_API_KEY")
BETFAIR_API_URL = "https://api.betfair.com/exchange/betting/json-rpc/v1"

# ------------------------------------------------
#               Utility Functions
# ------------------------------------------------
def get_headers():
    """ Generate headers for Betfair API calls."""
    session_token = BetfairAuthManager.get_token()
    if not session_token:
        logger.warning("Session token missing, re-authenticating...")
        BetfairAuthManager.login()
        session_token = BetfairAuthManager.get_token()
    return {
        "X-Authentication": session_token,
        "X-Application": api_key,
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
    }

def handle_api_error(response):
    """ Handle API errors from Betfair responses. """
    if response.status_code != 200:
        logger.error(f"Betfair API Error: {response.text}")
        raise HTTPException(status_code=response.status_code, detail="Error in Betfair API response")

# ------------------------------------------------
#               Retry Mechanism
# ------------------------------------------------
async def fetch_with_retry(operation, *args, retries=3, delay=2):
    """
    Execute an operation with exponential backoff retry logic.
    
    Args:
        operation: Function to execute
        *args: Arguments for the operation
        retries (int): Number of retry attempts
        delay (int): Base delay between retries in seconds
        
    Returns:
        Any: Result of the operation if successful
        None: If all retries fail
    """
    for i in range(retries):
        try:
            result = await operation(*args)
            if result:
                return result
            logger.warning(f"Operation returned no result, attempt {i+1}/{retries}")
        except Exception as e:
            logger.warning(f"Retry {i+1}/{retries} failed: {str(e)}")
            if i < retries - 1:  # Don't sleep on the last iteration
                await asyncio.sleep(delay * (2 ** i))  # Exponential backoff
    return None

# ------------------------------------------------
#               Event Retrieval Functions
# ------------------------------------------------
async def list_event_types():
    """ Fetch event type IDs (e.g., Basketball). """
    payload = {
        "jsonrpc": "2.0",
        "method": "SportsAPING/v1.0/listEventTypes",
        "params": {"filter": {}},
        "id": 1
    }
    async def fetch_event_types():
        response = requests.post(BETFAIR_API_URL, headers=get_headers(), json=payload)
        handle_api_error(response)
        return response.json()
    return await fetch_with_retry(fetch_event_types)

async def list_events(event_type_id: int):
    """ Fetch events (NBA games) for a given event type ID. """
    payload = {
        "jsonrpc": "2.0",
        "method": "SportsAPING/v1.0/listEvents",
        "params": {"filter": {"eventTypeIds": [event_type_id]}},
        "id": 1
    }
    async def fetch_events():
        response = requests.post(BETFAIR_API_URL, headers=get_headers(), json=payload)
        handle_api_error(response)
        return response.json()
    return await fetch_with_retry(fetch_events)

# ------------------------------------------------
#               Market Data Functions
# ------------------------------------------------
async def _fetch_market_data_async(market_id: str):
    """
    Fetch market data and format it for betting strategies.
    This function processes the raw market book data into a format
    that's easier to use by the betting strategies.
    """
    try:
        market_book = await list_market_book(market_id)
        if not market_book or "result" not in market_book or not market_book["result"]:
            logger.error("Failed to fetch market book data")
            return {"runners": []}
        
        # Extract runners from the first market
        runners_data = market_book["result"][0].get("runners", [])
        
        # Process runners to extract back and lay odds
        runners = []
        for runner in runners_data:
            selection_id = runner.get("selectionId")
            status = runner.get("status")
            
            if status != "ACTIVE":
                continue
                
            # Extract best back and lay prices
            exchange_data = runner.get("ex", {})
            back_prices = exchange_data.get("availableToBack", [])
            lay_prices = exchange_data.get("availableToLay", [])
            
            back_odds = back_prices[0].get("price") if back_prices else None
            lay_odds = lay_prices[0].get("price") if lay_prices else None
            
            if back_odds or lay_odds:
                runners.append({
                    "selection_id": selection_id,
                    "back_odds": back_odds,
                    "lay_odds": lay_odds
                })
        
        return {
            "market_id": market_id,
            "runners": runners,
            "total_matched": market_book["result"][0].get("totalMatched", 0)
        }
    except Exception as e:
        logger.error(f"Error fetching market data: {str(e)}")
        return {"runners": []}

def fetch_market_data(market_id: str):
    """
    Synchronous version of fetch_market_data.
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_fetch_market_data_async(market_id))
        loop.close()
        return result
    except Exception as e:
        logger.error(f"Error in fetch_market_data: {str(e)}")
        return {
            "market_id": market_id,
            "runners": [],
            "total_matched": 0
        }

async def list_market_catalogue(event_id: str, max_results: int = 10):
    """ Fetch available betting markets for an event. """
    payload = {
        "jsonrpc": "2.0",
        "method": "SportsAPING/v1.0/listMarketCatalogue",
        "params": {
            "filter": {"eventIds": [event_id]},
            "marketProjection": ["COMPETITION", "EVENT", "MARKET_START_TIME"],
            "sort": "FIRST_TO_START",
            "maxResults": max_results
        },
        "id": 1
    }
    async def fetch_market_catalogue():
        response = requests.post(BETFAIR_API_URL, headers=get_headers(), json=payload)
        handle_api_error(response)
        return response.json()
    return await fetch_with_retry(fetch_market_catalogue)

async def list_market_book(market_id: str):
    """ Fetch real-time odds for a given market. """
    payload = {
        "jsonrpc": "2.0",
        "method": "SportsAPING/v1.0/listMarketBook",
        "params": {
            "marketIds": [market_id],
            "priceProjection": {"priceData": ["EX_BEST_OFFERS"]}
        },
        "id": 1
    }
    async def fetch_market_book():
        response = requests.post(BETFAIR_API_URL, headers=get_headers(), json=payload)
        handle_api_error(response)
        return response.json()
    return await fetch_with_retry(fetch_market_book)

# ------------------------------------------------
#               Bet Placement Functions
# ------------------------------------------------
async def place_bet(market_id: str, selection_id: int, side: str, size: float, price: float):
    """
    Place a bet on the Betfair exchange.
    
    Args:
        market_id: Betfair market ID
        selection_id: Selection ID (runner ID)
        side: BACK or LAY
        size: Stake amount
        price: Odds
        
    Returns:
        Dict containing the API response
    """
    if size <= 0:
        raise HTTPException(status_code=400, detail="Stake must be greater than zero.")
    if price <= 1.01:
        raise HTTPException(status_code=400, detail="Odds must be greater than 1.01.")
    payload = {
        "jsonrpc": "2.0",
        "method": "SportsAPING/v1.0/placeOrders",
        "params": {
            "marketId": market_id,
            "instructions": [{
                "selectionId": selection_id,
                "handicap": 0,
                "side": side,
                "orderType": "LIMIT",
                "limitOrder": {
                    "size": size,
                    "price": price,
                    "persistenceType": "LAPSE"
                }
            }],
            "customerRef": "unique_ref"
        },
        "id": 1
    }
    async def place_bet_operation():
        response = requests.post(BETFAIR_API_URL, headers=get_headers(), json=payload)
        handle_api_error(response)
        return response.json()
    return await fetch_with_retry(place_bet_operation)

# ------------------------------------------------
#               Data Classes
# ------------------------------------------------
class Match:
    """
    Represents a betting match with market information.
    
    Attributes:
        market_id (str): Betfair market ID
        matched_amount (float): Amount matched on the market
        time_to_start (int): Minutes until the event starts
        team1_odds (float): Back odds for team 1
        team2_odds (float): Back odds for team 2
        sport (str): Sport name
        is_bettable (bool): Whether the match meets betting criteria
    """
    def __init__(self, market_id: str, matched_amount: float = 0, time_to_start: int = 0, 
                 team1_odds: float = 0, team2_odds: float = 0, sport: str = "Unknown"):
        self.market_id = market_id
        self.matched_amount = matched_amount
        self.time_to_start = time_to_start
        self.team1_odds = team1_odds
        self.team2_odds = team2_odds
        self.sport = sport
        self.is_bettable = False

class Wager:
    """
    Base class for all wager types.
    
    Attributes:
        match (Match): The match to bet on
        result (Dict): The result of the wager execution
    """
    def __init__(self, match: Match):
        self.match = match
        self.result = {}
    
    async def execute(self) -> Dict[str, Any]:
        """Execute the wager. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement execute()")

# ------------------------------------------------
#               Betting Workflow
# ------------------------------------------------
async def execute_betting_workflow(market_id: str, time_to_start: int, matched_amount: float) -> Dict[str, Any]:
    """
    Execute the betting workflow based on market conditions.
    
    This function analyzes market conditions and selects the appropriate
    betting strategy (LayDutch, BackDutch, or Modified LTD).
    
    Args:
        market_id (str): Betfair market ID
        time_to_start (int): Minutes until the event starts
        matched_amount (float): Amount matched on the market
        
    Returns:
        Dict[str, Any]: Result of the betting operation
    """
    from app.betting_wager.laydutch import LayDutchWager
    from app.betting_wager.backdutch import BackDutchWager
    from app.betting_wager.ltdModified import ModifiedLTDWager
    
    logger.info(f"Starting betting workflow for market {market_id}")
    logger.info(f"Time to start: {time_to_start} minutes, Matched amount: ${matched_amount}")
    
    try:
        # Create a Match object
        match = Match(market_id, matched_amount, time_to_start)
        
        # Get market data to populate odds
        market_data = await fetch_market_data(market_id)
        if not market_data:
            logger.error("Failed to fetch market data")
            return {"success": False, "message": "Failed to fetch market data"}
        
        # Extract odds from market data
        runners = []
        for runner in market_data.get('runners', []):
            if 'lay_odds' in runner and 'back_odds' in runner:
                runners.append(runner)
        
        if len(runners) < 2:
            logger.warning("Not enough valid runners found")
            return {"success": False, "message": "Not enough valid runners found"}
        
        # Determine the best strategy based on market conditions
        
        # Check for LayDutch conditions first (generally most profitable)
        lay_wager = LayDutchWager(match)
        if await lay_wager.calculate_available_funds() and await lay_wager.validate_market_conditions():
            logger.info("Market conditions suitable for LayDutch strategy")
            result = await lay_wager.execute()
            if result.get("success", False):
                return result
            logger.warning(f"LayDutch execution failed: {result.get('message', 'Unknown error')}")
        
        # Check for BackDutch conditions
        back_wager = BackDutchWager(match)
        if back_wager.check_preconditions():
            logger.info("Market conditions suitable for BackDutch strategy")
            back_wager.place_back_dutch_bets()
            return {"success": True, "message": "BackDutch strategy executed successfully"}
        
        # Fall back to Modified LTD strategy
        logger.info("Trying Modified LTD strategy")
        ltd_wager = ModifiedLTDWager(
            market_id, 
            matched_amount, 
            time_to_start,
            runners[0].get('back_odds', 0),
            runners[1].get('back_odds', 0)
        )
        
        if ltd_wager.check_preconditions():
            ltd_wager.execute()
            return {"success": True, "message": "Modified LTD strategy executed successfully"}
        
        # No suitable strategy found
        return {"success": False, "message": "No suitable betting strategy found for this market"}
        
    except Exception as e:
        logger.error(f"Error in betting workflow: {str(e)}")
        return {"success": False, "message": f"Error: {str(e)}"}

# ------------------------------------------------
#               Helper Functions
# ------------------------------------------------
def calculate_implied_probability(odds: float) -> float:
    """Convert decimal odds to implied probability."""
    return 1 / odds if odds > 0 else 0

def check_preconditions(match: Match, min_matched_amount: float = 500) -> bool:
    """Check if basic betting preconditions are met."""
    if match.matched_amount < min_matched_amount:
        logger.warning(f"Insufficient market liquidity for match {match.market_id}")
        return False
    return True

# ------------------------------------------------
#               Account Functions
# ------------------------------------------------
async def get_account_funds():
    """Get account funds information."""
    payload = {
        "jsonrpc": "2.0",
        "method": "AccountAPING/v1.0/getAccountFunds",
        "params": {},
        "id": 1
    }
    
    async def fetch_account_funds():
        response = requests.post(
            "https://api.betfair.com/exchange/account/json-rpc/v1",
            headers=get_headers(),
            json=payload
        )
        handle_api_error(response)
        result = response.json()
        # Add debug logging to see the structure of the response
        logger.info(f"Account funds response: {result}")
        return result.get("result", {})
    
    result = await fetch_with_retry(fetch_account_funds)
    return result
from app.logger import logger
