# ------------------------------------------------
#                     Imports
# ------------------------------------------------
from typing import List, Dict, Any, Optional
from decimal import Decimal, ROUND_DOWN
import asyncio
from app.logger import logger
from app.betfair import fetch_market_data
from app.betfair.utils import (
    
    place_bet,
    calculate_implied_probability,
    check_preconditions,
    Match,
    Wager,
    get_account_funds,
    list_market_book,
    fetch_with_retry
)

# ------------------------------------------------
#               Global Variables
# ------------------------------------------------
# Time and Market Conditions
GV_SCAN_START_MINUTES = 180  # Maximum time before event start to consider betting
GV_MATCHED_BETS_DOLLARS_MINIMUM = 500  # Minimum market liquidity

# Odds and Risk Management
GV_ODDS_RANGE_ABSOLUTE = 2.0  # Absolute odds range threshold
GV_ODDS_RANGE_RELATIVE = 0.4762  # 47.62% relative odds range
GV_MIN_ODDS = 1.5  # Minimum acceptable odds
GV_MAX_ODDS = 10.0  # Maximum acceptable odds
MIN_STAKE = 2.0  # Minimum stake per Betfair API
MIN_LIQUIDITY_FACTOR = 1.5  # Required liquidity multiplier over stake

# Fund Management
GV_LTD_MAX_FUNDS_PERCENTAGE = 0.20  # Maximum 20% of total funds per wager
GV_LTD_RESERVED_FUNDS_PERCENTAGE = 0.30  # 30% funds reserved for other strategies
GV_MIN_ROI = 0.035  # Minimum ROI threshold (3.5%)
GV_TARGET_ROI = 0.05  # Target ROI for stake calculation (5%)

# Commission and Fees
COMMISSION_RATE = 0.05  # Betfair's standard commission rate

# ------------------------------------------------
#               LayDutchWager Class
# ------------------------------------------------
class LayDutchWager:
    def __init__(self, match: Match):
        """
        Initialize LayDutchWager with match data and setup initial state.
        
        Args:
            match (Match): Match object containing market information
        """
        self.match = match
        self.selections = []  # List of selections with odds and stakes
        self.total_liability = 0.0
        self.potential_profit = 0.0
        self.roi = 0.0
        self.available_funds = 0.0
        self.market_depth = {}  # Store market depth information

    # Constants for market validation
    MIN_TOTAL_PROBABILITY = 0.8
    MAX_TOTAL_PROBABILITY = 1.2
    MIN_SELECTION_PROBABILITY = 0.1

    # ------------------------------------------------
    #               Fund Management
    # ------------------------------------------------
    async def calculate_available_funds(self) -> bool:
        """Calculate available funds for lay dutch wagering."""
        try:
            account_funds = await fetch_with_retry(get_account_funds)
            if not account_funds:
                logger.error("Failed to fetch account funds")
                return False

            total_funds = account_funds['available']
            
            # Dynamic fund allocation based on account balance
            max_wager_funds = min(
                total_funds * GV_LTD_MAX_FUNDS_PERCENTAGE,
                total_funds - (total_funds * GV_LTD_RESERVED_FUNDS_PERCENTAGE)
            )
            
            self.available_funds = max_wager_funds
            return self.available_funds >= MIN_STAKE
            
        except Exception as e:
            logger.error(f"Error calculating available funds: {str(e)}")
            return False

    # ------------------------------------------------
    #               Market Validation
    # ------------------------------------------------
    async def validate_market_conditions(self) -> bool:
        """
        Validate if market conditions are suitable for lay dutching.
        Includes market depth validation and single selection support.
        
        Returns:
            bool: True if conditions are met, False otherwise
        """
        try:
            # Basic preconditions
            if not check_preconditions(self.match, GV_MATCHED_BETS_DOLLARS_MINIMUM):
                return False

            if self.match.time_to_start > GV_SCAN_START_MINUTES:
                logger.warning(f"Event starts too far in future: {self.match.time_to_start} minutes")
                return False

            # Fetch market data with retry
            market_data = await fetch_with_retry( self.match.market_id)
            if not market_data:
                logger.warning("Failed to fetch market data after retries")
                return False

            # Get market book for depth information
            market_book = await fetch_with_retry(list_market_book, self.match.market_id)
            if not market_book:
                logger.warning("Failed to fetch market book after retries")
                return False

            # Process selections with improved market depth validation
            valid_selections = []
            for runner in market_data['runners']:
                lay_odds = runner['lay_odds']
                if GV_MIN_ODDS <= lay_odds <= GV_MAX_ODDS:
                    runner_book = next(
                        (r for r in market_book['runners'] if r['selectionId'] == runner['selection_id']),
                        None
                    )
                    
                    # Calculate available liquidity considering price sensitivity
                    available_liquidity = self.calculate_available_liquidity(runner_book, lay_odds)
                    
                    if available_liquidity >= MIN_STAKE * MIN_LIQUIDITY_FACTOR:
                        runner['available_liquidity'] = available_liquidity
                        runner['book_data'] = runner_book  # Store for later use
                        valid_selections.append(runner)

            # Support both single and multiple selection scenarios
            if not valid_selections:
                logger.warning("No valid selections found")
                return False

            if len(valid_selections) >= 2:
                # Multiple selection validation
                odds_range = max(s['lay_odds'] for s in valid_selections) / min(s['lay_odds'] for s in valid_selections)
                if odds_range < GV_ODDS_RANGE_ABSOLUTE:
                    logger.warning(f"Odds range {odds_range} below minimum {GV_ODDS_RANGE_ABSOLUTE}")
                    return False
            else:
                # Single selection validation
                selection = valid_selections[0]
                if selection['lay_odds'] < GV_MIN_ODDS * 1.1:  # Higher threshold for single lays
                    logger.warning("Single selection odds too low")
                    return False

            self.selections = valid_selections

            # Additional validation
            if not self.selections:
                return False

            total_probability = sum(1/s['lay_odds'] for s in self.selections)
            
            if total_probability < self.MIN_TOTAL_PROBABILITY:
                logger.warning(f"Total probability {total_probability:.2f} too low")
                return False
                
            if total_probability > self.MAX_TOTAL_PROBABILITY:
                logger.warning(f"Total probability {total_probability:.2f} too high")
                return False

            # Check individual probabilities and liquidity
            min_required_liquidity = MIN_STAKE * MIN_LIQUIDITY_FACTOR * len(self.selections)
            total_liquidity = 0
            weighted_liquidity = 0

            for selection in self.selections:
                prob = 1/selection['lay_odds']
                if prob < self.MIN_SELECTION_PROBABILITY:
                    logger.warning(f"Selection probability too low: {prob:.2f}")
                    return False
                    
                norm_prob = prob/total_probability
                avail_liq = self.get_available_liquidity(selection)
                
                total_liquidity += avail_liq
                weighted_liquidity += avail_liq * norm_prob

            if total_liquidity < min_required_liquidity:
                logger.warning(f"Insufficient liquidity: {total_liquidity:.2f}")
                return False

            avg_weighted_liq = weighted_liquidity / len(self.selections)
            if avg_weighted_liq < min_required_liquidity / len(self.selections):
                logger.warning("Imbalanced liquidity distribution")
                return False

            return True

        except Exception as e:
            logger.error(f"Error validating market conditions: {str(e)}")
            return False

    def calculate_available_liquidity(self, runner_book: Dict[str, Any], target_odds: float) -> float:
        """
        Calculate available liquidity considering price sensitivity.
        
        Args:
            runner_book: Market book data for a runner
            target_odds: Target lay odds
            
        Returns:
            float: Available liquidity at or better than target odds
        """
        if not runner_book or 'availableToLay' not in runner_book:
            return 0.0
            
        total_liquidity = 0.0
        price_sensitivity = 0.02  # 2% price sensitivity
        
        for price_level in runner_book['availableToLay']:
            if price_level['price'] <= target_odds * (1 + price_sensitivity):
                total_liquidity += price_level['size']
                
        return total_liquidity

    def get_available_liquidity(self, selection):
        return self.calculate_available_liquidity(selection['book_data'], selection['lay_odds'])

    # ------------------------------------------------
    #               Price Monitoring
    # ------------------------------------------------
    def validate_price_movement(self, current_odds: float, original_odds: float) -> bool:
        """
        Validate if price movement is within acceptable range.
        
        Args:
            current_odds: Current lay odds
            original_odds: Original lay odds when selection was validated
            
        Returns:
            bool: True if price movement is acceptable
        """
        max_movement = 0.05  # Maximum 5% price movement allowed
        movement = abs(current_odds - original_odds) / original_odds
        
        if movement > max_movement:
            logger.warning(f"Price movement {movement:.2%} exceeds maximum allowed {max_movement:.2%}")
            return False
        return True

    # ------------------------------------------------
    #               Stake Calculation
    # ------------------------------------------------
    def calculate_optimal_stakes(self) -> bool:
        """
        Calculate optimal lay stakes for each selection.
        Implements dynamic bankroll management and proper commission handling.
        
        Returns:
            bool: True if profitable stakes were found, False otherwise
        """
        try:
            # Calculate total implied probability adjusted for commission
            total_probability = 0
            for selection in self.selections:
                lay_odds = selection['lay_odds']
                imp_prob = calculate_implied_probability(lay_odds)
                # Adjust probability for commission and market inefficiency
                adj_prob = imp_prob * (1 + COMMISSION_RATE)
                selection['probability'] = adj_prob
                total_probability += adj_prob

            if total_probability >= 1:
                logger.warning("No arbitrage opportunity - total probability >= 1")
                return False

            # Dynamic target profit calculation
            base_target = self.available_funds * GV_TARGET_ROI
            # Adjust target based on probability margin
            probability_margin = 1 - total_probability
            adjusted_target = base_target * probability_margin

            # Calculate stakes with improved liquidity consideration
            profit_factor = adjusted_target / (1 - total_probability)
            total_liability = 0
            
            for selection in self.selections:
                # Base stake calculation
                stake = profit_factor * selection['probability']
                
                # Get available liquidity at different price points
                available_liquidity = self.get_available_liquidity(selection)
                
                # Adjust stake based on available liquidity with safety margin
                max_stake = available_liquidity / (MIN_LIQUIDITY_FACTOR * 1.1)  # Additional 10% safety margin
                stake = min(stake, max_stake)
                
                # Calculate liability and round stake
                liability = stake * (selection['lay_odds'] - 1)
                selection['stake'] = Decimal(stake).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
                selection['liability'] = liability
                total_liability += liability

            if total_liability > self.available_funds:
                logger.warning("Total liability exceeds available funds")
                return False

            # Calculate actual ROI with commission
            self.total_liability = total_liability
            gross_profit = adjusted_target
            net_profit = gross_profit * (1 - COMMISSION_RATE)
            self.potential_profit = net_profit
            self.roi = net_profit / total_liability if total_liability > 0 else 0

            return self.roi >= GV_MIN_ROI

        except Exception as e:
            logger.error(f"Error calculating stakes: {str(e)}")
            return False

    # ------------------------------------------------
    #               Wager Execution
    # ------------------------------------------------
    async def execute(self) -> Dict[str, Any]:
        """
        Execute the lay dutch wager by placing all calculated bets.
        Implements retry logic and comprehensive validation.
        
        Returns:
            Dict[str, Any]: Result of wager execution
        """
        try:
            # Validate conditions and calculate stakes
            if not await self.calculate_available_funds():
                return {"success": False, "message": "Insufficient funds"}

            if not await self.validate_market_conditions():
                return {"success": False, "message": "Market conditions not suitable"}

            if not self.calculate_optimal_stakes():
                return {"success": False, "message": "Could not find profitable stakes"}

            # Revalidate market conditions before placing bets
            current_market_book = await fetch_with_retry(list_market_book, self.match.market_id)
            if not current_market_book:
                return {"success": False, "message": "Failed to fetch current market data"}

            # Check for significant price movements
            for selection in self.selections:
                current_runner = next(
                    (r for r in current_market_book['runners'] 
                     if r['selectionId'] == selection['selection_id']),
                    None
                )
                if not current_runner:
                    return {"success": False, "message": "Selection no longer available"}

                current_odds = current_runner['availableToLay'][0]['price']
                if not self.validate_price_movement(current_odds, selection['lay_odds']):
                    return {
                        "success": False, 
                        "message": "Significant price movement detected",
                        "original_odds": selection['lay_odds'],
                        "current_odds": current_odds
                    }

            # Log execution details
            logger.info(f"Executing LayDutch wager for match {self.match.market_id}")
            logger.info(f"Total liability: ${self.total_liability:.2f}")
            logger.info(f"Potential profit: ${self.potential_profit:.2f}")
            logger.info(f"ROI: {self.roi*100:.2f}%")
            logger.info(f"Number of selections: {len(self.selections)}")

            # Place lay bets with retry mechanism and sequential execution
            bet_results = []
            for selection in self.selections:
                bet_result = await fetch_with_retry(
                    place_bet,
                    market_id=self.match.market_id,
                    selection_id=selection['selection_id'],
                    stake=float(selection['stake']),
                    price=selection['lay_odds'],
                    side="LAY"
                )
                
                if not bet_result or not bet_result.get('success'):
                    error_msg = bet_result.get('message') if bet_result else "Failed to place bet"
                    logger.error(f"Failed to place lay bet: {error_msg}")
                    
                    # If we've already placed some bets, log the partial execution
                    if bet_results:
                        logger.warning(f"Partial bet execution: {len(bet_results)} of {len(self.selections)} bets placed")
                    
                    return {
                        "success": False, 
                        "message": "Failed to place all bets",
                        "partial_execution": bool(bet_results),
                        "bets_placed": len(bet_results),
                        "total_bets": len(self.selections)
                    }
                
                bet_results.append(bet_result)
                logger.info(f"Successfully placed bet {len(bet_results)} of {len(self.selections)}")

            # Calculate actual execution metrics
            executed_liability = sum(float(bet['size']) * (float(bet['price']) - 1) 
                                  for bet in bet_results)
            executed_commission = executed_liability * COMMISSION_RATE
            
            return {
                "success": True,
                "total_liability": self.total_liability,
                "actual_liability": executed_liability,
                "potential_profit": self.potential_profit,
                "commission": executed_commission,
                "net_roi": (self.potential_profit - executed_commission) / executed_liability,
                "number_of_selections": len(self.selections),
                "bet_results": bet_results
            }

        except Exception as e:
            logger.error(f"Error executing lay dutch wager: {str(e)}")
            return {"success": False, "message": str(e)}


