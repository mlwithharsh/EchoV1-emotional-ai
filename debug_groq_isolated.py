
import os
import requests
import logging
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DebugGroq")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    logger.error("GROQ_API_KEY not found in environment!")
    exit(1)

class DebugNLPEngine:
    def __init__(self, model_name="llama3-8b-8192"):
        self.model_name = model_name
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        logger.info(f"Initialized with model: {self.model_name}")

    def call_groq_model(self, messages):
        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": 50,
            "temperature": 0.7
        }
        
        logger.info("Sending request to Groq...")
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)
            
            logger.info(f"Response Status Code: {response.status_code}")
            logger.info(f"Response Content: {response.text}")
            
            if response.status_code == 200:
                return response.json()
            else:
                return f"Error: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Request Exception: {e}")
            return str(e)

# Test with the OLD broken model
print("\n--- TEST 1: Decommissioned Model (llama3-8b-8192) ---")
engine_old = DebugNLPEngine(model_name="llama3-8b-8192")
messages = [{"role": "user", "content": "Hello, world!"}]
engine_old.call_groq_model(messages)

# Test with a NEW supported model (e.g., llama-3.3-70b-versatile or llama-3.1-8b-instant)
print("\n--- TEST 2: Supported Model (llama-3.1-8b-instant) ---")
engine_new = DebugNLPEngine(model_name="llama-3.1-8b-instant")
engine_new.call_groq_model(messages)
