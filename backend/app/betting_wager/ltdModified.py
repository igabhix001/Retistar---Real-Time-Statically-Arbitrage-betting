# ------------------------------------------------
#                     Imports
# ------------------------------------------------
from typing import Dict, Any
from app.logger import logger
from app.betfair import fetch_market_data
from app.betfair.utils import place_bet, check_preconditions, calculate_implied_probability
from app.betfair.utils import Match, Wager

# ------------------------------------------------
#               Constants
# ------------------------------------------------
GV_SCAN_START_MINUTES_LTD = 180
GV_MATCHED_BETS_DOLLARS_MINIMUM = 500
GV_LTD_MIN_ODDS_RANGE_RELATIVE = 1.75
GV_LTD_MIN_PROB_MARGIN_PERCENT = 0.9
GV_LTD_MIN_ROI_PERCENT = 0.1

# ------------------------------------------------
#               Modified LTD Wager Logic
# ------------------------------------------------
class ModifiedLTDWager:
    def __init__(self, market_id: str, matched_amount: float, time_to_start: int, team1_odds: float, team2_odds: float):
        self.match = Match(market_id, matched_amount, time_to_start)
        self.match.team1_odds = team1_odds
        self.match.team2_odds = team2_odds

    # ------------------------------------------------
    #               Preconditions Check
    # ------------------------------------------------
    def check_preconditions(self) -> bool:
        """Check if the match meets the requirements for Modified LTD Wager."""
        if self.match.time_to_start > GV_SCAN_START_MINUTES_LTD:
            logger.warning(f"Match {self.match.market_id} starts too late.")
            return False
        if self.match.matched_amount < GV_MATCHED_BETS_DOLLARS_MINIMUM:
            logger.warning(f"Market liquidity too low.")
            return False
        if max(self.match.team1_odds, self.match.team2_odds) / min(self.match.team1_odds, self.match.team2_odds) < GV_LTD_MIN_ODDS_RANGE_RELATIVE:
            logger.warning("Odds difference between teams is too small. Skipping LTD bet.")
            return False
        self.match.is_bettable = True
        return True

    # ------------------------------------------------
    #               Execute LTD Wager
    # ------------------------------------------------
    def execute(self):
        """Execute the Modified LTD Wager workflow."""
        if not self.check_preconditions():
            return
        
        market_data = fetch_market_data(self.match.market_id)
        if not market_data or "runners" not in market_data:
            logger.error("Failed to fetch valid market data")
            return
        
        draw_odds = []
        for runner in market_data.get('runners', []):
            back_odds = runner.get('back_odds')
            lay_odds = runner.get('lay_odds')
            if back_odds and lay_odds:
                draw_odds.append({
                    "selection_id": runner.get("selection_id"),
                    "back_odds": back_odds,
                    "lay_odds": lay_odds
                })
        
        if not draw_odds:
            logger.warning("No valid draw odds found. Exiting betting workflow.")
            return
        
        best_outcome = max(draw_odds, key=lambda x: x["back_odds"])
        logger.info(f"Placing bet on draw: Back Odds = {best_outcome['back_odds']}")
        
        selection_id = best_outcome["selection_id"]
        if selection_id:
            place_bet(self.match.market_id, selection_id, side="BACK", size=10, price=best_outcome["back_odds"])
        else:
            logger.warning("Failed to identify a valid selection ID for the draw market.")
