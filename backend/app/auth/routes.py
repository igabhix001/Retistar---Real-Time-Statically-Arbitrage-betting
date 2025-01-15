from fastapi import APIRouter, HTTPException, Depends
from .models import User, Login, OTPVerification, user_collection, otp_collection
from .utils import hash_password, verify_password, create_access_token, generate_otp
from bson.objectid import ObjectId
import datetime
from pydantic import BaseModel


auth_router = APIRouter()

# Signup
@auth_router.post("/signup")
async def signup(user: User):
    try:
        existing_user = await user_collection.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        user.password = hash_password(user.password)
        user_data = user.dict()
        user_data["is_verified"] = False
        user_data["created_at"] = datetime.datetime.utcnow()

        result = await user_collection.insert_one(user_data)
        otp = generate_otp()

        await otp_collection.insert_one({
            "email": user.email,
            "otp": otp,
            "expires_at": datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
        })

        return {"message": "User created successfully. Verify your account.", "otp": otp}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Login
@auth_router.post("/login")
async def login(login_data: Login):
    # Find the user by email
    user = await user_collection.find_one({"email": login_data.email})
    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Generate and store OTP even for logged-in users
    otp = generate_otp()
    await otp_collection.update_one(
        {"email": login_data.email},
        {"$set": {"otp": otp, "expires_at": datetime.datetime.utcnow() + datetime.timedelta(minutes=10)}},
        upsert=True,
    )

    # Return OTP for debugging purposes (in production, you would email or text it instead)
    print(f"Generated OTP for {login_data.email}: {otp}")

    # Return the access token and OTP message
    return {
        "message": "Login successful. OTP sent to verify your account.",
        "otp": otp,  # This can be removed in production
    }

# Verify OTP
@auth_router.post("/verify")
async def verify_otp(data: OTPVerification):
    # Log the incoming OTP verification request
    print("Received email:", data.email)
    print("Received OTP:", data.otp)

    # Retrieve OTP data from the database
    otp_data = await otp_collection.find_one({"email": data.email, "otp": str(data.otp)})
    
    if not otp_data:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Log the fetched OTP data to verify it's correct
    print("Fetched OTP data:", otp_data)

    # Check if the OTP has expired
    if otp_data["expires_at"] < datetime.datetime.utcnow():
        print("OTP expired at:", otp_data["expires_at"])
        print("Current time:", datetime.datetime.utcnow())
        raise HTTPException(status_code=400, detail="OTP has expired")

    # Mark the user as verified
    await user_collection.update_one({"email": data.email}, {"$set": {"is_verified": True}})

    # Delete the OTP data to prevent reuse
    await otp_collection.delete_many({"email": data.email})

    return {"message": "Account verified successfully"}

# Resend OTP
class ResendOTPRequest(BaseModel):
    email: str
@auth_router.post("/resend-otp")
async def resend_otp(request: ResendOTPRequest):
    email = request.email
    # Check if the user exists in the database
    user = await user_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate a new OTP
    otp = generate_otp()

    # Delete the previous OTP if it exists
    await otp_collection.delete_many({"email": email})

    # Store the new OTP with an expiration time
    await otp_collection.update_one(
        {"email": email},
        {"$set": {"otp": otp, "expires_at": datetime.datetime.utcnow() + datetime.timedelta(minutes=10)}},
        upsert=True
    )

    # Log the OTP for debugging (in production, you'd send this via email/SMS)
    print(f"New OTP sent to {email}: {otp}")

    return {"message": "OTP sent", "otp": otp}

# Forgot Password

class ForgotPasswordRequest(BaseModel):
    email: str
@auth_router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    email =request.email
    user = await user_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = generate_otp()
    await otp_collection.update_one(
        {"email": email},
        {"$set": {"otp": otp, "expires_at": datetime.datetime.utcnow() + datetime.timedelta(minutes=10)}},
        upsert=True,
    )

    # Placeholder for sending the OTP via email (replace with actual email logic)
    print(f"Password reset OTP for {email}: {otp}")

    return {"message": "Password reset OTP sent. Please check your email."}


# Reset Password    

class ResetPasswordRequest(BaseModel):
    email: str
    new_password: str

@auth_router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    # Check if the email exists
    user = await user_collection.find_one({"email": request.email})
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    # Hash the new password and update it in the database
    hashed_password = hash_password(request.new_password)
    result = await user_collection.update_one({"email": request.email}, {"$set": {"password": hashed_password}})
    
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Password update failed")

    return {"message": "Password reset successfully"}
