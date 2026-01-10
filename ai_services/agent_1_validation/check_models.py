from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

print("Fetching available models...")
for model in client.models.list():
    if "generateContent" in model.supported_actions:
        print(f"- {model.name}")