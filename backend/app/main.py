from fastapi import FastAPI, Depends
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
    BetfairAuthManager.login()

@app.get("/protected-route")
async def protected_route():
    """Example route that uses Betfair token."""
    token = BetfairAuthManager.get_token()
    return {"message": "Accessed Betfair API", "session_token": token}
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
    for route in app.routes:
        logger.info(f"Path: {route.path}, Name: {route.name}, Methods: {route.methods}")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
