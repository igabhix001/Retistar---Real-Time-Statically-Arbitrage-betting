from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

try:
    client = AsyncIOMotorClient(MONGO_URI)
    db = client["mongo_db"]  # Replace "mongo_db" with your database name
    print("Connected to MongoDB successfully!")
except Exception as e:
    print("Error connecting to MongoDB:", e)
    db = None  # Ensure `db` is still defined to prevent import errors
