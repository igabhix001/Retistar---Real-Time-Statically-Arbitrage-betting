Clone the repo go to backend folder and run the following command in your terminal

#
pip install -r requirements.txt

if pip not work try this command

#
pip install -r requirements.txt --break-system-packages


#
create .env file and add the following lines
SECRET_KEY=##########
MONGO_URI=###########
BETFAIR_API_KEY=your_betfair_api_key
BETFAIR_USERNAME=your_betfair_username
BETFAIR_PASSWORD=your_betfair_password

# Running the API Server
uvicorn app.main:app --reload

And you are good to go. You can access the API at https://localhost:8000/

# Milestone 3: Terminal Interface for Arbitrage Betting

For Milestone 3, a terminal interface has been implemented to demonstrate all the required functionality without the dashboard. This allows for testing and using the arbitrage betting system directly from the command line.

## Running the Terminal Interface

To run the terminal interface, execute the following command:

```
python run_terminal.py
```

## Features of the Terminal Interface

1. **Market Browsing**: Browse available sports, events, and markets
2. **Manual Market Entry**: Enter market ID and parameters manually
3. **Account Summary**: View account balance and exposure
4. **Betting Strategies**:
   - LayDutch Strategy: Places lay bets across multiple selections
   - BackDutch Strategy: Places back bets across multiple selections
   - Modified LTD Strategy: Specialized strategy for specific market conditions

## Testing the Betting Strategies

To run tests for the betting strategies:

```
python -m unittest app.test.test_betting_strategies
```

## Milestone 3 Requirements Fulfilled

1. Complete functionality implemented in Python terminal
2. User input variables simulated via terminal input
3. Dashboard outputs simulated via print functions
4. All specified functionalities implemented:
   - Odds scanning
   - Demand scanning
   - Bet placement
   - Exception handling
   - Logging
5. Bot can function as specified without dashboard interface

The system is now ready for Milestone 4, which will involve building the dashboard/frontend interface.
