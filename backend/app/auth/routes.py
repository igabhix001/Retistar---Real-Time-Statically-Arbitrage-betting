from fastapi import APIRouter, HTTPException, Request, FastAPI
import jwt
from .models import User, Login, OTPVerification, user_collection, otp_collection
from .utils import hash_password, verify_password, generate_otp
from bson.objectid import ObjectId
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from app.logger import logger
from app.betfair.auth import BetfairAuthManager
from app.config import config
from app.betfair.utils import execute_betting_workflow, fetch_market_data,get_all_market_data
from typing import List
from app.betfair.stream import BetfairStream

SECRET_KEY = config.SECRET_KEY

auth_router = APIRouter()
# Use FastAPI's state management
app = FastAPI()
app.state.betfair_stream = None


# Signup
@auth_router.post("/signup")
async def signup(user: User):
    try:
        logger.info("Processing signup for email: %s", user.email)
        existing_user = await user_collection.find_one({"email": user.email})
        if existing_user:
            logger.warning("Email already exists: %s", user.email)
            raise HTTPException(status_code=400, detail="Email already exists")
        
        user.password = hash_password(user.password)
        user_data = user.dict()
        user_data["is_verified"] = False
        user_data["created_at"] = datetime.now(timezone.utc)

        await user_collection.insert_one(user_data)
        otp = generate_otp()

        await otp_collection.insert_one({
            "email": user.email,
            "otp": otp,
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10)
        })

        logger.info("User created successfully: %s", user.email)
        return {"message": "User created successfully. Verify your account.", "otp": otp}
    except Exception as e:
        logger.error("Error in signup: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Login
@auth_router.post("/login")
async def login(login_data: Login):
    try:
        logger.info("Processing login for email: %s", login_data.email)
        user = await user_collection.find_one({"email": login_data.email})
        if not user or not verify_password(login_data.password, user["password"]):
            logger.warning("Invalid credentials for email: %s", login_data.email)
            raise HTTPException(status_code=400, detail="Invalid credentials")
        
        if not user["is_verified"]:
            logger.warning("Account not verified: %s", login_data.email)
            raise HTTPException(
                status_code=400,
                detail="Account not verified. Please complete signup verification to continue."
            )

        otp = generate_otp()
        await otp_collection.update_one(
            {"email": login_data.email},
            {"$set": {"otp": otp, "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10)}},
            upsert=True
        )

        logger.info("OTP sent to email: %s", login_data.email)
        return {"message": "OTP has been sent to your email. Please verify.", "otp_sent": True}
    except Exception as e:
        logger.error("Error in login: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Verify OTP
@auth_router.post("/verify")
async def verify_otp(data: OTPVerification):
    try:
        logger.info("Verifying OTP for email: %s", data.email)
        otp_data = await otp_collection.find_one({"email": data.email, "otp": str(data.otp)})
        if not otp_data:
            logger.warning("Invalid OTP for email: %s", data.email)
            raise HTTPException(status_code=400, detail="Invalid OTP")

        if otp_data["expires_at"] < datetime.now(timezone.utc):
            logger.warning("OTP expired for email: %s", data.email)
            raise HTTPException(status_code=400, detail="OTP has expired")
        
        user = await user_collection.find_one({"email": data.email})
        if not user:
            logger.error("User not found for email: %s", data.email)
            raise HTTPException(status_code=404, detail="User not found")

        if not user["is_verified"]:
            await user_collection.update_one({"email": data.email}, {"$set": {"is_verified": True}})
        
        await otp_collection.delete_many({"email": data.email})
        token = jwt.encode({"user_id": str(user["_id"]), "exp": datetime.now(timezone.utc) + timedelta(days=7)}, SECRET_KEY, algorithm="HS256")

        response = JSONResponse({"message": "OTP verified successfully. Login complete.", "token": token})
        response.set_cookie(key="token", value=token, httponly=True, secure=True, max_age=7*24*3600)
        logger.info("OTP verified and login completed for email: %s", data.email)
        
        #BetfairAuthManager.login()  # Non-interactive Betfair login
        return response # Return response with token cookie
         
    except Exception as e:
        logger.error("Error verifying OTP: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Resend OTP
class ResendOTPRequest(BaseModel):
    email: str

@auth_router.post("/resend-otp")
async def resend_otp(request: ResendOTPRequest):
    user = await user_collection.find_one({"email": request.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = generate_otp()
    await otp_collection.update_one(
        {"email": request.email},
        {"$set": {"otp": otp, "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10)}},
        upsert=True
    )

    return {"message": "OTP sent successfully."}


# Forgot Password
class ForgotPasswordRequest(BaseModel):
    email: str

@auth_router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    user = await user_collection.find_one({"email": request.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = generate_otp()
    await otp_collection.update_one(
        {"email": request.email},
        {"$set": {"otp": otp, "expires_at": datetime.utcnow() + timedelta(minutes=10)}},
        upsert=True
    )

    return {"message": "Password reset OTP sent to your email."}


# Reset Password
class ResetPasswordRequest(BaseModel):
    email: str
    new_password: str

@auth_router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    user = await user_collection.find_one({"email": request.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    hashed_password = hash_password(request.new_password)
    result = await user_collection.update_one({"email": request.email}, {"$set": {"password": hashed_password}})
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Password reset failed")

    return {"message": "Password reset successfully"}

# Check session
@auth_router.get("/check-session")
async def check_session(request: Request):
    # Retrieve token from cookies
    token = request.cookies.get("token")
    if not token:
        return {"authenticated": False, "message": "Token not found in cookies."}

    try:
        # Decode token
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        
        # Validate user_id
        if not user_id:
            return {"authenticated": False, "message": "Invalid token payload."}

        # Check if the user exists in the database
        user = await user_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return {"authenticated": False, "message": "User not found."}

        # If all checks pass
        return {"authenticated": True}

    except jwt.ExpiredSignatureError:
        return {"authenticated": False, "message": "Token has expired."}
    except jwt.InvalidTokenError:
        return {"authenticated": False, "message": "Invalid token."}
    except Exception as e:
        # Catch unexpected errors and log them
        print(f"Unexpected error during session check: {str(e)}")
        return {"authenticated": False, "message": "An error occurred."}


# Logout
@auth_router.post("/logout")
async def logout():
    response = JSONResponse({"message": "Logout successful"})
    response.delete_cookie("token")
    return response

# Protected route
@auth_router.get("/protected-route")
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
    
# ---------------------------------------------------
# Betting Logic routes
#-----------------------------------------------------
@auth_router.post("/place-bet/")
async def place_bet_endpoint(market_id: str, selection_id: int, side: str, size: float, price: float):
    """Endpoint to place a bet."""
    try:
        logger.info(f"Received request to place bet on market ID: {market_id}")

        # Example values for time_to_start and matched_amount
        time_to_start = 179  # Replace with actual logic to calculate time to start
        matched_amount = 7968  # Replace with actual logic to fetch matched amount

        # Execute the betting workflow
        response = execute_betting_workflow(market_id, time_to_start, matched_amount)

        # Return the response
        return {"message": "Bet placed successfully", "response": response}

    except HTTPException as e:
        logger.error(f"HTTPException: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    
#-----------------------------------------------------
    # Fetch market specific data endpoint
#-----------------------------------------------------
    
    
@auth_router.post("/fetch-market-data/")
async def fetch_market_data_endpoint(market_id: str):
        """Endpoint to fetch market data."""
        try:
            logger.info(f"Received request to fetch market data for market ID: {market_id}")

            # Fetch market data
            market_data = fetch_market_data(market_id)

            # Return the response
            return {"message": "Market data fetched successfully", "market_data": market_data}

        except HTTPException as e:
            logger.error(f"HTTPException: {e.detail}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
        
#-----------------------------------------------------  
        # Fetch market data endpoint
#-----------------------------------------------------

@auth_router.post("/get-all-market-data/")
async def get_all_market_data_endpoint():
    """Endpoint to fetch market data for all markets."""
    try:
        logger.info("Received request to fetch market data for all markets")

        # Fetch market data
        market_data = get_all_market_data()

        # Return the response
        return {"message": "Market data fetched successfully", "market_data": market_data}

    except HTTPException as e:
        logger.error(f"HTTPException: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")

#-----------------------------------------------------
 # Fetch market specific data endpoint
#-----------------------------------------------------

@auth_router.post("/fetch-market-specific-data/")
async def fetch_market_specific_data_endpoint():
    """Endpoint to fetch market specific data."""

    market_id = 1 # Example market ID

    try:
        logger.info(f"Received request to fetch market specific data for market ID: {market_id}")    

        # Fetch market specific data
        market_data = fetch_market_data(market_id)  

        # Return the response
        return {"message": "Market specific data fetched successfully", "market_data": market_data}

    except HTTPException as e:
        logger.error(f"HTTPException: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")  
     
#-----------------------------------------------------
# Stream routes
#------------------------------------------------


@auth_router.post("/stream/start")
async def start_stream(market_ids: List[str]):
    """Start streaming market data for specified markets."""
    try:
        if app.betfair_stream and app.betfair_stream.running:
            return {"message": "Stream is already running"}

        app.betfair_stream = BetfairStream()
        app.betfair_stream.start()
        app.betfair_stream.subscribe_to_markets(market_ids)
        
        return {"message": "Stream started successfully"}
    except Exception as e:
        logger.error(f"Error starting stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@auth_router.post("/stream/stop")
async def stop_stream():
    """Stop the market data stream."""
    try:
        if app.betfair_stream:
            app.betfair_stream.stop()
            app.betfair_stream = None
            return {"message": "Stream stopped successfully"}
        return {"message": "No active stream to stop"}
    except Exception as e:
        logger.error(f"Error stopping stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))


