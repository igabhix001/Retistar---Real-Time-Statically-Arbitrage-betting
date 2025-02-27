# ------------------------------------------------
#                   Imports
# ------------------------------------------------
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import uvicorn
from app.auth.routes import auth_router
from app.config import config
from app.logger import logger
from app.betfair.auth import BetfairAuthManager
from app.betfair.utils import execute_betting_workflow

# ------------------------------------------------
#               FastAPI App Setup
# ------------------------------------------------
app = FastAPI()

# Include routes
app.include_router(auth_router, prefix="/auth")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------
#                   Routes
# ------------------------------------------------
@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to the Auth API"}

# ------------------------------------------------
#               Startup Event
# ------------------------------------------------
@app.on_event("startup")
async def startup_event():
    """Initialize Betfair session on startup."""
    try:
        BetfairAuthManager.login()
        asyncio.create_task(BetfairAuthManager.monitor_connection())  # Start connection monitor
        logger.info("Betfair session initialized on startup.")
    except Exception as e:
        logger.error(f"Startup error: {e}")



# ------------------------------------------------
#               Main Execution
# ------------------------------------------------
if __name__ == "__main__":
    # Log all registered routes
    for route in app.routes:
        logger.info(f"Path: {route.path}, Name: {route.name}, Methods: {route.methods}")

    # Run the betting workflow
    market_id = "1.123456789"  # Example market ID
    time_to_start = 179  # Minutes to start (example)
    matched_amount = 7968  # Matched amount in AUD (example)
    asyncio.run(execute_betting_workflow(market_id, time_to_start, matched_amount))

    # Start the FastAPI server
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)