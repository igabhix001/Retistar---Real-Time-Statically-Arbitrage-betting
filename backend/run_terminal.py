"""
Run the terminal interface for the Arbitrage Betting System.

This script provides a simple entry point to run the terminal interface
for the arbitrage betting system, as specified in Milestone 3.
"""
import asyncio
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.terminal_interface import run_terminal_interface

if __name__ == "__main__":
    print("Starting Arbitrage Betting Terminal Interface...")
    asyncio.run(run_terminal_interface())
