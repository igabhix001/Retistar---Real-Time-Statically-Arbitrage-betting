from fastapi import FastAPI, HTTPException
from app.auth.routes import auth_router
from fastapi.middleware.cors import CORSMiddleware
from app.config import config
from app.logger import logger
from app.betfair.auth import BetfairAuthManager

app = FastAPI()

# Include routes
app.include_router(auth_router, prefix="/auth")


@app.get("/")
async def root():
    return {"message": "Welcome to the Auth API"}


@app.on_event("startup")
async def startup_event():
    """Initialize Betfair session on startup."""
    try:
        BetfairAuthManager.login()
        logger.info("Betfair session initialized on startup.")
    except HTTPException as e:
        logger.error(f"Failed to initialize Betfair session on startup: {e.detail}")
    except Exception as e:
        logger.error(f"Unexpected error during startup: {e}")


@app.get("/protected-route")
async def protected_route():
    """
    Example route that requires a valid Betfair token.
    Returns token and login status.
    """
    try:
        token = BetfairAuthManager.get_token()
        if token:
            return {
                "message": "Accessed protected route successfully.",
                "session_token": token,
                "status": "Valid session",
            }
        else:
            raise HTTPException(status_code=401, detail="Unauthorized access.")
    except HTTPException as e:
        logger.error(f"Protected route error: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error on protected route: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")


# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# List all routes and start the server
if __name__ == "__main__":
    import uvicorn

    # Log all registered routes
    for route in app.routes:
        logger.info(f"Path: {route.path}, Name: {route.name}, Methods: {route.methods}")

    # Start the server
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
