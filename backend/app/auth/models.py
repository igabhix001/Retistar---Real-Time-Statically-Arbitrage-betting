from pydantic import BaseModel, EmailStr
from typing import Optional
from pymongo import MongoClient
from app.init_database import db

# Pydantic schemas
class User(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

class Login(BaseModel):
    email: EmailStr
    password: str

class OTPVerification(BaseModel):
    email: EmailStr
    otp: str

# MongoDB Models


user_collection = db["users"]
otp_collection = db["otps"]
