import os
from dotenv import load_dotenv

# Load environment variables from a .env file in the root
load_dotenv()

API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("API_KEY not found. Please set it in your .env file.")