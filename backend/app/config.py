import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    MONGO_URI = os.getenv("MONGO_URI")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

config = Config()
