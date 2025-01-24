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
    try:
        BetfairAuthManager.login()
        logger.info("Betfair session initialized on startup.")
    except Exception as e:
        logger.error(f"Startup error: {e}")

@app.get("/protected-route")
async def protected_route():
    try:
        token = BetfairAuthManager.get_token()
        return {
            "message": "Accessed protected route successfully.",
            "session_token": token,
        }
    except Exception as e:
        logger.error(f"Protected route error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")

@app.get("/rate-limit-status")
async def rate_limit_status():
    return {
        "remaining": RATE_LIMIT_REMAINING,
        "reset_time": RATE_LIMIT_RESET,
    }

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn

    for route in app.routes:
        logger.info(f"Path: {route.path}, Name: {route.name}, Methods: {route.methods}")

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
