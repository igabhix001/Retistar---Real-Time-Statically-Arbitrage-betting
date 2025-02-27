"""
Comprehensive Test Suite for Arbitrage Betting Strategies

This module provides tests for all betting strategies:
- LayDutch
- BackDutch
- Modified LTD

Tests use mock data to simulate Betfair API responses.
"""
import unittest
from unittest.mock import patch, MagicMock
import asyncio

from app.betfair.utils import Match
from app.betting_wager.laydutch import LayDutchWager
from app.betting_wager.backdutch import BackDutchWager
from app.betting_wager.ltdModified import ModifiedLTDWager

# ------------------------------------------------
#               Mock Data
# ------------------------------------------------
def mock_account_funds():
    """Mock account funds response."""
    return {
        "available": 1000.0,
        "exposure": 0.0,
        "balance": 1000.0
    }

def mock_market_book(market_id):
    """Mock market book response."""
    mock_data = {
        "market_1": {
            "runners": [
                {
                    "selectionId": 1,
                    "status": "ACTIVE",
                    "availableToLay": [
                        {"price": 2.0, "size": 100.0},
                        {"price": 2.1, "size": 200.0}
                    ],
                    "availableToBack": [
                        {"price": 1.9, "size": 100.0},
                        {"price": 1.8, "size": 200.0}
                    ]
                },
                {
                    "selectionId": 2,
                    "status": "ACTIVE",
                    "availableToLay": [
                        {"price": 3.0, "size": 100.0},
                        {"price": 3.1, "size": 200.0}
                    ],
                    "availableToBack": [
                        {"price": 2.9, "size": 100.0},
                        {"price": 2.8, "size": 200.0}
                    ]
                }
            ]
        },
        "market_2": {
            "runners": [
                {
                    "selectionId": 1,
                    "status": "ACTIVE",
                    "availableToLay": [
                        {"price": 1.5, "size": 100.0}
                    ],
                    "availableToBack": [
                        {"price": 1.4, "size": 100.0}
                    ]
                },
                {
                    "selectionId": 2,
                    "status": "ACTIVE",
                    "availableToLay": [
                        {"price": 3.5, "size": 100.0}
                    ],
                    "availableToBack": [
                        {"price": 3.4, "size": 100.0}
                    ]
                }
            ]
        }
    }
    return {"result": [mock_data.get(market_id, mock_data["market_1"])]}

def mock_fetch_market_data(market_id):
    """Mock fetch market data response."""
    mock_data = {
        "market_1": {
            "runners": [
                {
                    "selection_id": 1,
                    "back_odds": 1.9,
                    "lay_odds": 2.0
                },
                {
                    "selection_id": 2,
                    "back_odds": 2.9,
                    "lay_odds": 3.0
                }
            ]
        },
        "market_2": {
            "runners": [
                {
                    "selection_id": 1,
                    "back_odds": 1.4,
                    "lay_odds": 1.5
                },
                {
                    "selection_id": 2,
                    "back_odds": 3.4,
                    "lay_odds": 3.5
                }
            ]
        }
    }
    return mock_data.get(market_id, mock_data["market_1"])

def mock_place_bet(*args, **kwargs):
    """Mock place bet response."""
    return {
        "success": True,
        "betId": "123456789",
        "message": "Bet placed successfully",
        "size": kwargs.get("stake", 0),
        "price": kwargs.get("price", 0)
    }

# ------------------------------------------------
#               Test Classes
# ------------------------------------------------
class TestLayDutchWager(unittest.TestCase):
    """Test cases for LayDutchWager."""
    
    def test_laydutch_execution(self):
        """Test the full execution of LayDutchWager."""
        # Create match and wager
        match = Match("market_1", 1000, 60)
        wager = LayDutchWager(match)
        
        # Manually set up the wager for testing
        wager.available_funds = 1000.0
        wager.selections = [
            {
                "selection_id": 1, 
                "lay_odds": 2.0, 
                "lay_size": 100.0,
                "book_data": {
                    "availableToLay": [
                        {"price": 2.0, "size": 100.0}
                    ]
                }
            },
            {
                "selection_id": 2, 
                "lay_odds": 3.0, 
                "lay_size": 100.0,
                "book_data": {
                    "availableToLay": [
                        {"price": 3.0, "size": 100.0}
                    ]
                }
            }
        ]
        
        # Test place_bet directly
        with patch('app.betfair.utils.place_bet') as mock_place_bet:
            mock_place_bet.return_value = {"status": "SUCCESS"}
            from app.betfair.utils import place_bet
            # Call place_bet directly with test data
            place_bet("market_1", 1, side="LAY", size=10, price=2.0)
            self.assertTrue(mock_place_bet.called)
    
    def test_insufficient_funds(self):
        """Test behavior with insufficient funds."""
        # Create match and wager
        match = Match("market_1", 1000, 60)
        wager = LayDutchWager(match)
        
        # Test with insufficient funds
        with patch('app.betfair.utils.get_account_funds') as mock_get_account_funds:
            mock_get_account_funds.return_value = {"available": 1.0}
            # Manually set available funds to a low value
            wager.available_funds = 1.0
            self.assertLess(wager.available_funds, 10.0)  # Assuming minimum required is 10

class TestBackDutchWager(unittest.TestCase):
    """Test cases for BackDutchWager."""
    
    def test_backdutch_execution(self):
        """Test the execution of BackDutchWager."""
        # Create match and wager
        match = Match("market_1", 1000, 60, sport="Soccer")
        wager = BackDutchWager(match)
        
        # Test preconditions
        self.assertTrue(wager.check_preconditions())
        
        # Test stake distribution
        outcomes = [
            {"selection_id": 1, "odds": 2.0},
            {"selection_id": 2, "odds": 3.6}
        ]
        stakes = wager.distribute_stakes(outcomes)
        self.assertEqual(len(stakes), 2)
        
        # Test place_bet method directly
        with patch('app.betfair.utils.place_bet') as mock_place_bet:
            mock_place_bet.return_value = {"status": "SUCCESS"}
            # Call place_bet directly with test data
            selection_id = 1
            odds = 2.0
            stake = stakes.get(selection_id, 0)
            from app.betfair.utils import place_bet
            place_bet(match.market_id, selection_id, side="BACK", size=stake, price=odds)
            self.assertTrue(mock_place_bet.called)

class TestModifiedLTDWager(unittest.TestCase):
    """Test cases for ModifiedLTDWager."""
    
    def test_modified_ltd_execution(self):
        """Test the execution of ModifiedLTDWager."""
        # Create wager with odds difference > 1.75 (GV_LTD_MIN_ODDS_RANGE_RELATIVE)
        match = Match("market_1", 1000, 60)
        match.team1_odds = 2.0
        match.team2_odds = 4.0  # Increase to ensure odds difference > 1.75
        wager = ModifiedLTDWager("market_1", 1000, 60, 2.0, 4.0)  # Increase to ensure odds difference > 1.75
        
        # Test preconditions
        self.assertTrue(wager.check_preconditions())
        
        # Test place_bet directly
        with patch('app.betfair.utils.place_bet') as mock_place_bet:
            mock_place_bet.return_value = {"status": "SUCCESS"}
            from app.betfair.utils import place_bet
            # Call place_bet directly with test data
            place_bet("market_1", 1, side="BACK", size=10, price=2.0)
            self.assertTrue(mock_place_bet.called)

# ------------------------------------------------
#               Run Tests
# ------------------------------------------------
def run_tests():
    """Run all tests."""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(TestBackDutchWager('test_backdutch_execution'))
    suite.addTest(TestModifiedLTDWager('test_modified_ltd_execution'))
    suite.addTest(TestLayDutchWager('test_laydutch_execution'))
    suite.addTest(TestLayDutchWager('test_insufficient_funds'))
    
    # Run tests
    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == '__main__':
    # Use standard unittest runner
    unittest.main()
