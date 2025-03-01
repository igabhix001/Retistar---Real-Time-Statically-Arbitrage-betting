# Retistar Arbitrage Betting System - User Guide

## Introduction

Welcome to the Retistar Arbitrage Betting System! This terminal-based application allows you to execute various arbitrage betting strategies on Betfair markets. This guide will walk you through the setup process and explain how to use the system effectively.

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- Betfair account with API access
- Required Python packages

### Installation

1. Ensure you have Python installed on your system
2. Navigate to the backend directory:
   ```
   cd path/to/Retistar---Real-Time-Statically-Arbitrage-betting/backend
   ```
3. Install required packages:
   ```
   pip install -r requirements.txt
   ```

### Configuration

Before using the system, ensure your Betfair API credentials are properly configured in the application.

## Running the Application

1. Navigate to the backend directory:
   ```
   cd path/to/Retistar---Real-Time-Statically-Arbitrage-betting/backend
   ```

2. Run the terminal interface:
   ```
   python run_terminal.py
   ```

3. The system will initialize and connect to the Betfair API automatically.

## Using the Terminal Interface

### Main Menu

When you start the application, you'll see the main menu with these options:

```
================================================================================
                 Arbitrage Betting System - Terminal Interface
================================================================================

1. Browse Markets
2. Enter Market ID Manually
3. Account Summary
4. Exit
```

### Option 1: Browse Markets

This option allows you to browse available sports events and markets:

1. Select a sport from the list (e.g., Horse Racing, Soccer, Tennis)
2. Select an event from the list of available events for that sport
3. Select a market from the list of available markets for that event
4. Enter the minutes until the event starts (default: 60)
5. Enter the matched amount for simulation purposes (default: 1000)
6. The system will then proceed to the betting workflow

### Option 2: Enter Market ID Manually

If you already know the Betfair market ID you want to bet on:

1. Enter the market ID (e.g., "1.123456789")
2. Enter the minutes until the event starts
3. Enter the matched amount
4. The system will then proceed to the betting workflow

### Option 3: Account Summary

Displays your Betfair account information:
- Available Balance
- Exposure
- Total Balance
- Retained Commission
- Exposure Limit

### Option 4: Exit

Exits the application.

## Placing Bets

After selecting a market (either through browsing or manual entry), you'll enter the betting workflow:

1. The system will fetch market data and display the available odds
2. You'll be prompted to select a betting strategy:
   ```
   Select betting strategy:
   1. LayDutch Strategy
   2. BackDutch Strategy
   3. Modified LTD Strategy
   ```

3. After selecting a strategy, the system will:
   - Analyze the market conditions
   - Calculate optimal stakes
   - Check if the opportunity meets the strategy's criteria
   - Place bets if all conditions are met

4. The system will display the results of the betting operation, including:
   - Success/failure status
   - Total liability
   - Potential profit
   - ROI (Return on Investment)
   - Commission
   - Individual bet results

## Understanding the Betting Strategies

### 1. LayDutch Strategy

**What it does:** Places lay bets on multiple selections to guarantee a profit regardless of the outcome.

**How it works:**
- Calculates available funds
- Analyzes market liquidity
- Calculates optimal stakes for each selection
- Places lay bets if the ROI meets the minimum threshold (default: 3.5%)

**Best used when:** You identify a market where the combined implied probabilities of all outcomes are less than 100%.

### 2. BackDutch Strategy

**What it does:** Places back bets on multiple selections to distribute risk.

**How it works:**
- Calculates optimal stakes for each selection
- Places back bets on selections with favorable odds
- Aims to achieve a balanced return regardless of outcome

**Best used when:** You want to spread your risk across multiple outcomes in a market.

### 3. Modified LTD Strategy

**What it does:** Combines elements of lay betting and dutching for a hybrid approach.

**How it works:**
- Analyzes market conditions
- Calculates optimal stakes using a modified algorithm
- Places bets with a focus on minimizing risk while maximizing potential returns

**Best used when:** Markets have specific odds patterns that traditional strategies might miss.

## Tips for Successful Arbitrage Betting

1. **Start small:** Begin with small stakes to test the strategies and gain confidence.

2. **Focus on liquidity:** Strategies perform best in markets with high liquidity (high matched amounts).

3. **Timing matters:** Some strategies perform better at specific times before an event starts.

4. **Monitor your account:** Regularly check your account summary to track your balance and exposure.

5. **Understand commission:** Remember that Betfair's commission (default 5%) affects your net profit.

6. **Be patient:** Not every market will offer profitable arbitrage opportunities.

## Troubleshooting

If you encounter issues:

1. **API Connection Problems:**
   - Check your internet connection
   - Verify your Betfair API credentials
   - Ensure your Betfair account is active and in good standing

2. **Betting Failures:**
   - Ensure you have sufficient funds in your Betfair account
   - Verify that the market is still open and available for betting
   - Check if odds have changed significantly since analysis

3. **System Errors:**
   - Check the application logs for detailed error information
   - Restart the application if it becomes unresponsive
   - Ensure you're running the latest version of the software

## Advanced Usage

### Strategy Parameters

Each strategy has configurable parameters that determine its behavior:

**LayDutch Strategy:**
- Minimum ROI: 3.5%
- Target ROI: 5%
- Maximum funds percentage: 20% of total funds
- Reserved funds percentage: 30%

**BackDutch Strategy:**
- Minimum stake: $2.0
- Minimum liquidity factor: 1.5x stake

**Modified LTD Strategy:**
- Custom parameters for hybrid approach

Advanced users can modify these parameters in the source code to adjust risk tolerance and betting behavior.

## Conclusion

The Retistar Arbitrage Betting System provides a powerful tool for executing arbitrage betting strategies on Betfair markets. By following this guide and practicing with small stakes, you can learn to identify and capitalize on arbitrage opportunities effectively.

Remember that all betting carries risk, and past performance is not indicative of future results. Always bet responsibly and within your means.

For technical support or questions about the system, please contact the development team.

---

© 2025 Retistar Arbitrage Betting System
