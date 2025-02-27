# test_back_dutch_wager.py

import unittest
from unittest.mock import patch
from app.betting_wager.backdutch import BackDutchWager

# Mock Match class
class MockMatch:
    def __init__(self, market_id, matched_amount, time_to_start, sport):
        self.market_id = market_id
        self.matched_amount = matched_amount
        self.time_to_start = time_to_start
        self.sport = sport

# Mock market data
def mock_fetch_market_data(market_id):
    mock_data = {
        "market_1": {  # Equal Scaling Case
            "result": [{
                "runners": [
                    {"selectionId": 1, "status": "ACTIVE", "ex": {"availableToBack": [{"price": 2.0}]}},
                    {"selectionId": 2, "status": "ACTIVE", "ex": {"availableToBack": [{"price": 3.6}]}}
                ]
            }]
        },
        "market_2": {  # Underdog Scaling Case
            "result": [{
                "runners": [
                    {"selectionId": 1, "status": "ACTIVE", "ex": {"availableToBack": [{"price": 1.5}]}},
                    {"selectionId": 2, "status": "ACTIVE", "ex": {"availableToBack": [{"price": 1.8}]}}
                ]
            }]
        },
        "market_3": {  # Champion Scaling Case
            "result": [{
                "runners": [
                    {"selectionId": 1, "status": "ACTIVE", "ex": {"availableToBack": [{"price": 2.2}]}},
                    {"selectionId": 2, "status": "ACTIVE", "ex": {"availableToBack": [{"price": 2.5}]}}
                ]
            }]
        },
        "market_4": {  # No Arbitrage Opportunity (IP ≥ 1)
            "result": [{
                "runners": [
                    {"selectionId": 1, "status": "ACTIVE", "ex": {"availableToBack": [{"price": 1.5}]}},
                    {"selectionId": 2, "status": "ACTIVE", "ex": {"availableToBack": [{"price": 1.6}]}}
                ]
            }]
        },
        "market_5": {  # Low Liquidity Case
            "result": [{
                "runners": [
                    {"selectionId": 1, "status": "ACTIVE", "ex": {"availableToBack": [{"price": 2.8}]}},
                    {"selectionId": 2, "status": "ACTIVE", "ex": {"availableToBack": [{"price": 3.0}]}}
                ]
            }]
        }
    }
    return mock_data.get(market_id, {})

# --------------------------------------------------
#                Test Suite Class
# --------------------------------------------------
class TestBackDutchWager(unittest.TestCase):

    @patch('app.betfair.utils.fetch_market_data', side_effect=mock_fetch_market_data)
    def test_equal_scaling(self, mock_fetch):
        match = MockMatch("market_1", 1000, 60, "Soccer")
        wager = BackDutchWager(match)
        wager.place_back_dutch_bets()

    @patch('app.betfair.utils.fetch_market_data', side_effect=mock_fetch_market_data)
    def test_underdog_scaling(self, mock_fetch):
        match = MockMatch("market_2", 1500, 30, "Tennis")
        wager = BackDutchWager(match)
        wager.place_back_dutch_bets()

    @patch('app.betfair.utils.fetch_market_data', side_effect=mock_fetch_market_data)
    def test_champion_scaling(self, mock_fetch):
        match = MockMatch("market_3", 2000, 20, "Basketball")
        wager = BackDutchWager(match)
        wager.place_back_dutch_bets()

    @patch('app.betfair.utils.fetch_market_data', side_effect=mock_fetch_market_data)
    def test_no_arbitrage(self, mock_fetch):
        match = MockMatch("market_4", 1200, 15, "Soccer")
        wager = BackDutchWager(match)
        wager.place_back_dutch_bets()

    @patch('app.betfair.utils.fetch_market_data', side_effect=mock_fetch_market_data)
    def test_low_liquidity(self, mock_fetch):
        match = MockMatch("market_5", 400, 90, "Cricket")  # Liquidity < 500
        wager = BackDutchWager(match)
        wager.place_back_dutch_bets()

# --------------------------------------------------
#                Test Runner
# --------------------------------------------------
if __name__ == '__main__':
    unittest.main()