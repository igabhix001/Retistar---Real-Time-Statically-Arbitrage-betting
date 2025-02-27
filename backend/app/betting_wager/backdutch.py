from typing import List, Dict, Any
from app.betfair import fetch_market_data
from app.betfair.utils import (
    place_bet,
    calculate_implied_probability,
    check_preconditions,
    Match,
    Wager
)
from app.logger import logger
# ------------------------------------------------
#                     Imports
# ------------------------------------------------

# ------------------------------------------------
#               Global Variables
# ------------------------------------------------
GV_BACKDUTCH_MIN_ROI = 0.035  # Minimum ROI (3.5%)
GV_MATCHED_BETS_DOLLARS_MINIMUM = 500  # Market liquidity threshold
GV_RELATIVE_ODDS_EQUAL_SCALING = 0.8
GV_RELATIVE_ODDS_UNDERDOG_SCALING = 0.4
GV_ODDS_INCREASE_FAVOURITE_LEADER = 0.03  # 3% increase for Leader scaling
MIN_STAKE = 2.0  # Minimum stake to comply with Betfair's API

# ------------------------------------------------
#               BackDutchWager Class
# ------------------------------------------------
class BackDutchWager:
    def __init__(self, match):
        self.match = match
        self.outcomes = []  # Store outcome data with odds and stakes

    # ------------------------------------------------
    #               Preconditions Check
    # ------------------------------------------------
    def check_preconditions(self) -> bool:
        """Check if the match meets the BackDutch Wager criteria."""
        if self.match.matched_amount < GV_MATCHED_BETS_DOLLARS_MINIMUM:
            logger.warning(f"Insufficient market liquidity for match {self.match.market_id}.")
            return False
        if self.match.time_to_start > 1440:  # Matches must start within 24 hours
            logger.warning(f"Match {self.match.market_id} starts too late.")
            return False
        if self.match.sport in ["Cycling", "Darts", "Esports", "Politics"]:
            logger.warning(f"Excluded sport detected: {self.match.sport}.")
            return False
        return True

    # ------------------------------------------------
    #       Implied Probability Calculation
    # ------------------------------------------------
    def calculate_implied_probability(self, odds: float) -> float:
        """Convert decimal odds to implied probability."""
        return 1 / odds if odds > 0 else 0

    # ------------------------------------------------
    #               Stake Distribution Logic
    # ------------------------------------------------
    def distribute_stakes(self, outcomes: List[Dict[str, Any]]) -> Dict[int, float]:
        """Distribute stakes across outcomes to achieve target ROI."""
        total_implied_prob = sum(self.calculate_implied_probability(outcome['odds']) for outcome in outcomes)
        if total_implied_prob >= 1:
            logger.warning("No arbitrage opportunity (implied probability ≥ 1).")
            return {}
        base_stake = 100  # Base stake for calculations
        stakes = {
            outcome['selection_id']: max(
                MIN_STAKE,  # Ensure minimum stake
                base_stake * self.calculate_implied_probability(outcome['odds']) / total_implied_prob
            )
            for outcome in outcomes
        }
        return stakes

    # ------------------------------------------------
    #               Place BackDutch Bets
    # ------------------------------------------------
    def place_back_dutch_bets(self):
        """Place BackDutch bets if conditions are met."""
        try:
            if not self.check_preconditions():
                return
            market_data = fetch_market_data(self.match.market_id)
            if not market_data or "runners" not in market_data:
                logger.error("Failed to fetch valid market data")
                return
            runners = market_data.get('runners', [])
            outcomes = [
                {
                    "selection_id": runner.get("selection_id"),
                    "odds": runner.get("back_odds")
                }
                for runner in runners if runner.get("back_odds") and runner.get("back_odds") > 1.01
            ]
            if len(outcomes) < 2:
                logger.warning("Not enough valid outcomes for BackDutch Wager.")
                return
            stakes = self.distribute_stakes(outcomes)
            if not stakes:
                return
            for outcome in outcomes:
                selection_id = outcome['selection_id']
                odds = outcome['odds']
                stake = stakes.get(selection_id, 0)
                if stake > 0:
                    logger.info(f"Placing Back Bet: Selection {selection_id}, Odds {odds}, Stake {stake}")
                    place_bet(self.match.market_id, selection_id, side="BACK", size=stake, price=odds)
        except Exception as e:
            logger.error(f"Error in place_back_dutch_bets: {e}")
            return

    # ------------------------------------------------
    #               Place Bet Helper
    # ------------------------------------------------
    # Removed the place_bet method as it's no longer needed
