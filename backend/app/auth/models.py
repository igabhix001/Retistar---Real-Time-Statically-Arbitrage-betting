from pydantic import BaseModel, EmailStr
from ..init_database import db

from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

# Initialize MongoDB client and database

client = MongoClient("MONGO_URI")  # Replace "MONGO_URI" with your MongoDB connection string

db = client["mongo_db"]  # Replace "mongo_db" with your database name

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
