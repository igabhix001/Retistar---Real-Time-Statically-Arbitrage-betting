"""
Terminal Interface for Arbitrage Betting System

This module provides a command-line interface for the arbitrage betting system,
simulating the dashboard inputs and outputs as specified in Milestone 3.
"""
import asyncio
import sys
from typing import Dict, Any, List, Optional
from decimal import Decimal

from app.logger import logger
from app.betfair.auth import BetfairAuthManager
from app.betfair.utils import (
    list_event_types,
    list_events,
    list_market_catalogue,
    list_market_book,
    get_account_funds,
    fetch_market_data
)
from app.betting_wager.laydutch import LayDutchWager
from app.betting_wager.backdutch import BackDutchWager
from app.betting_wager.ltdModified import ModifiedLTDWager

# Define Match and Wager classes if they're not already defined
class Match:
    """Represents a betting match with market information."""
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
    """Base class for all wager types."""
    def __init__(self, match: Match):
        self.match = match
        self.result = {}
    
    async def execute(self) -> Dict[str, Any]:
        """Execute the wager. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement execute()")

# Terminal UI helper functions
def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"{title.center(80)}")
    print("=" * 80)

def print_section(title: str):
    """Print a formatted section title."""
    print("\n" + "-" * 80)
    print(f"{title}")
    print("-" * 80)

def get_user_input(prompt: str, default: Any = None) -> str:
    """Get user input with a default value."""
    default_text = f" [{default}]" if default is not None else ""
    user_input = input(f"{prompt}{default_text}: ").strip()
    return user_input if user_input else default

def get_numeric_input(prompt: str, default: Optional[float] = None, min_value: Optional[float] = None, 
                     max_value: Optional[float] = None) -> float:
    """Get numeric input with validation."""
    while True:
        try:
            default_text = f" [{default}]" if default is not None else ""
            user_input = input(f"{prompt}{default_text}: ").strip()
            value = float(user_input) if user_input else default
            
            if value is None:
                print("A value is required.")
                continue
                
            if min_value is not None and value < min_value:
                print(f"Value must be at least {min_value}.")
                continue
                
            if max_value is not None and value > max_value:
                print(f"Value must be at most {max_value}.")
                continue
                
            return value
        except ValueError:
            print("Please enter a valid number.")

def get_selection_input(prompt: str, options: List[Dict[str, Any]], 
                       display_func=lambda x: str(x)) -> Dict[str, Any]:
    """Get user selection from a list of options."""
    print(f"\n{prompt}")
    for i, option in enumerate(options, 1):
        print(f"{i}. {display_func(option)}")
    
    while True:
        try:
            selection = int(input("\nEnter selection number: "))
            if 1 <= selection <= len(options):
                return options[selection - 1]
            print(f"Please enter a number between 1 and {len(options)}.")
        except ValueError:
            print("Please enter a valid number.")

async def execute_betting_workflow(market_id: str, time_to_start: int, matched_amount: float) -> Dict[str, Any]:
    """
    Execute the betting workflow based on user preferences.
    
    Args:
        market_id: The Betfair market ID
        time_to_start: Minutes until the event starts
        matched_amount: Amount matched on the market
        
    Returns:
        Dict containing the results of the betting operation
    """
    print_section("Executing Betting Workflow")
    
    # Create a Match object
    match = Match(market_id, matched_amount, time_to_start)
    
    # Get market data to populate odds
    market_data = await fetch_market_data(match.market_id)
    if not market_data or "result" not in market_data or not market_data["result"]:
        logger.error("Failed to fetch market data")
        return {"success": False, "message": "Failed to fetch market data"}
    
    # Extract odds from market data if available
    runners = market_data.get('result', [{}])[0].get('runners', [])
    if len(runners) >= 2:
        match.team1_odds = runners[0].get('ex', {}).get('availableToBack', [{}])[0].get('price', 0)
        match.team2_odds = runners[1].get('ex', {}).get('availableToBack', [{}])[0].get('price', 0)
    
    # Get strategy selection from user
    print("\nSelect betting strategy:")
    print("1. LayDutch Strategy")
    print("2. BackDutch Strategy")
    print("3. Modified LTD Strategy")
    
    strategy_choice = get_numeric_input("Enter strategy number", default=1, min_value=1, max_value=3)
    
    # Execute the selected strategy
    result = {"success": False, "message": "Strategy execution failed"}
    
    try:
        if strategy_choice == 1:
            print("\nExecuting LayDutch Strategy...")
            wager = LayDutchWager(match)
            result = await wager.execute()
        elif strategy_choice == 2:
            print("\nExecuting BackDutch Strategy...")
            wager = BackDutchWager(match)
            # BackDutchWager doesn't have an async execute method, so we call place_back_dutch_bets
            wager.place_back_dutch_bets()
            result = {"success": True, "message": "BackDutch bets placed"}
        elif strategy_choice == 3:
            print("\nExecuting Modified LTD Strategy...")
            wager = ModifiedLTDWager(market_id, matched_amount, time_to_start, match.team1_odds, match.team2_odds)
            wager.execute()
            result = {"success": True, "message": "Modified LTD strategy executed"}
    except Exception as e:
        logger.error(f"Error executing strategy: {str(e)}")
        result = {"success": False, "message": f"Error: {str(e)}"}
    
    # Display results
    print_section("Betting Results")
    if result["success"]:
        print("✅ Betting operation successful!")
        for key, value in result.items():
            if key != "bet_results":  # Skip detailed bet results for cleaner output
                print(f"{key}: {value}")
        
        if "bet_results" in result:
            print("\nIndividual bet results:")
            for i, bet in enumerate(result["bet_results"], 1):
                print(f"Bet {i}: {bet.get('message', 'No details')}")
    else:
        print("❌ Betting operation failed!")
        print(f"Reason: {result.get('message', 'Unknown error')}")
    
    return result

async def browse_markets():
    """Browse available markets and select one for betting."""
    print_header("Market Browser")
    
    # Fetch event types (sports)
    event_types_response = await list_event_types()
    if not event_types_response or "result" not in event_types_response:
        print("Failed to fetch event types.")
        return None
    
    event_types = event_types_response["result"]
    selected_event_type = get_selection_input(
        "Select a sport:",
        event_types,
        lambda x: f"{x['eventType']['name']}"
    )
    
    # Fetch events for the selected sport
    events_response = await list_events(selected_event_type["eventType"]["id"])
    if not events_response or "result" not in events_response or not events_response["result"]:
        print("No events found for this sport.")
        return None
    
    selected_event = get_selection_input(
        "Select an event:",
        events_response["result"],
        lambda x: f"{x['event']['name']} - {x['event']['countryCode']}"
    )
    
    # Fetch markets for the selected event
    markets_response = await list_market_catalogue(selected_event["event"]["id"])
    if not markets_response or "result" not in markets_response or not markets_response["result"]:
        print("No markets found for this event.")
        return None
    
    selected_market = get_selection_input(
        "Select a market:",
        markets_response["result"],
        lambda x: f"{x['marketName']} - {x.get('totalMatched', 0)}"
    )
    
    # Get market details
    market_id = selected_market["marketId"]
    
    # Get market book to see matched amount and time to start
    market_book = await list_market_book(market_id)
    if not market_book or "result" not in market_book or not market_book["result"]:
        print("Failed to fetch market details.")
        return None
    
    market_details = market_book["result"][0]
    matched_amount = market_details.get("totalMatched", 0)
    
    # Calculate time to start in minutes (simplified)
    time_to_start = get_numeric_input("Enter minutes until event starts", default=60, min_value=0)
    
    return {
        "market_id": market_id,
        "matched_amount": matched_amount,
        "time_to_start": time_to_start
    }

async def account_summary():
    """Display account summary information."""
    print_header("Account Summary")
    
    try:
        # Get account funds
        funds = await get_account_funds()
        if funds:
            print(f"Available Balance: ${funds.get('availableToBetBalance', 0):.2f}")
            print(f"Exposure: ${funds.get('exposure', 0):.2f}")
            print(f"Total Balance: ${funds.get('balance', 0):.2f}")
            print(f"Retained Commission: ${funds.get('retainedCommission', 0):.2f}")
            print(f"Exposure Limit: ${funds.get('exposureLimit', 0):.2f}")
        else:
            print("Unable to fetch account information.")
    except Exception as e:
        print(f"Error fetching account information: {str(e)}")
        import traceback
        traceback.print_exc()

async def main_menu():
    """Display the main menu and handle user selection."""
    while True:
        print_header("Arbitrage Betting System - Terminal Interface")
        print("\n1. Browse Markets")
        print("2. Enter Market ID Manually")
        print("3. Account Summary")
        print("4. Exit")
        
        choice = get_numeric_input("\nSelect an option", default=1, min_value=1, max_value=4)
        
        if choice == 1:
            market_info = await browse_markets()
            if market_info:
                await execute_betting_workflow(
                    market_info["market_id"],
                    market_info["time_to_start"],
                    market_info["matched_amount"]
                )
        
        elif choice == 2:
            market_id = get_user_input("Enter Market ID")
            if not market_id:
                continue
                
            time_to_start = get_numeric_input("Enter minutes until event starts", default=60, min_value=0)
            matched_amount = get_numeric_input("Enter matched amount", default=1000, min_value=0)
            
            await execute_betting_workflow(market_id, time_to_start, matched_amount)
        
        elif choice == 3:
            await account_summary()
        
        elif choice == 4:
            print("\nExiting application. Goodbye!")
            break

async def run_terminal_interface():
    """Initialize and run the terminal interface."""
    print_header("Initializing Arbitrage Betting System")
    
    try:
        # Initialize Betfair session
        print("Connecting to Betfair API...")
        BetfairAuthManager.login()
        print("✅ Connected to Betfair API")
        
        # Run the main menu
        await main_menu()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        logger.error(f"Terminal interface error: {str(e)}")
    
    print("\nShutting down...")

if __name__ == "__main__":
    asyncio.run(run_terminal_interface())
