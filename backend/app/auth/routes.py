from fastapi import APIRouter, HTTPException, Request
from .models import User, Login, OTPVerification, user_collection, otp_collection
from .utils import hash_password, verify_password, generate_otp
from bson.objectid import ObjectId
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import jwt
from app.logger import logger
from app.betfair.auth import BetfairAuthManager
from app.config import config
from app.init_database import db
SECRET_KEY = config.SECRET_KEY

auth_router = APIRouter()

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