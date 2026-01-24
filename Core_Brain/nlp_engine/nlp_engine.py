# NLP, intent detection, emotion sense
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import time
import random
from functools import lru_cache
import requests
import logging

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class NLPEngine:
    def __init__(self, model_name="llama-3.1-8b-instant"):
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)
        # Ensure logging is configured to show our messages
        if not self.logger.handlers:
            logging.basicConfig(level=logging.INFO)
        
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Verify API Key existence on init (fail early warning)
        if not GROQ_API_KEY:
            self.logger.critical("GROQ_API_KEY is missing! LLM calls will fail.")

    def _get_fallback_response(self, context_type="general"):
        """Provide safe fallback responses when LLM is completely unavailable."""
        fallbacks = {
            "general": [
                "I'm having a little trouble thinking clearly right now, but I'm here for you.",
                "My connection to the cloud seems to be drifting. Could you say that again?",
                "I want to reply, but my thoughts are a bit scrambled. One moment please."
            ],
            "emotion": '{"emotion": "neutral", "sentiment": "neutral"}',
            "intent": "unknown"
        }
        return random.choice(fallbacks.get(context_type, fallbacks["general"]))

    def call_groq_model(self, messages, max_tokens=200, temperature=0.7, retry_count=3):
        """
        Robust Groq API Caller with:
        - Input validation
        - Exponential backoff
        - Specific error handling
        - Fallback protection
        """
        # 1. Input Validation
        if not messages or not isinstance(messages, list):
            self.logger.error("Invalid messages format provided to call_groq_model")
            return "[Error]: Invalid input format"
            
        if not GROQ_API_KEY:
            self.logger.error("Cannot call Groq: API Key missing")
            return self._get_fallback_response("general")

        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 1,
            "stream": False
        }
        
        # 2. Retry Logic with Backoff
        for attempt in range(retry_count):
            try:
                response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=10)
                
                # 3. HTTP Error Handling
                if response.status_code == 200:
                    try:
                        result = response.json()
                        if "choices" in result and len(result["choices"]) > 0:
                            content = result["choices"][0]["message"]["content"]
                            if content:
                                return content.strip()
                            else:
                                self.logger.warning(f"[Attempt {attempt+1}] Received empty content from LLM.")
                        else:
                            self.logger.warning(f"[Attempt {attempt+1}] Unexpected JSON structure: {result}")
                            
                    except json.JSONDecodeError:
                        self.logger.error(f"[Attempt {attempt+1}] Failed to parse JSON response.")
                
                elif response.status_code == 401:
                    self.logger.critical("Groq Authentication Failed. Check API Key.")
                    return "Authentication Error: Please check your API key."
                    
                elif response.status_code == 429:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    self.logger.warning(f"Rate limited. Retrying in {wait_time:.2f}s...")
                    time.sleep(wait_time)
                    continue
                    
                else:
                    self.logger.warning(f"[Attempt {attempt+1}] HTTP {response.status_code}: {response.text}")
                    # Don't retry client errors (4xx) except 429
                    if 400 <= response.status_code < 500:
                        return f"API Error {response.status_code}: {response.text}"
            
            except requests.exceptions.Timeout:
                self.logger.warning(f"[Attempt {attempt+1}] Request timed out.")
            except requests.exceptions.ConnectionError:
                self.logger.warning(f"[Attempt {attempt+1}] Connection error.")
            except Exception as e:
                self.logger.error(f"[Attempt {attempt+1}] Unexpected error: {e}")

            # Backoff for next attempt
            if attempt < retry_count - 1:
                time.sleep(2 ** attempt)

        # 4. Ultimate Fallback
        self.logger.error("All retries failed for Groq API call.")
        return self._get_fallback_response("general")

    @lru_cache(maxsize=128)
    def detect_intent_cached(self, user_input: str) -> str:
        return self.detect_intent(user_input)

    def detect_intent(self, user_input: str) -> str:
        messages = [
            {
                "role": "system",
                "content": "You are an intent detector. Respond with one word only: 'greeting', 'question', 'request', 'get_weather', 'emotional_support', 'manipulation_check', or 'unknown'."
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
        
        result = self.call_groq_model(messages, max_tokens=10).lower().strip()
        
        # Fallback check
        if any(err in result for err in ["Error", "trouble", "scrambled"]):
            return "unknown"
            
        valid_intents = ["greeting", "question", "request", "get_weather", "emotional_support", "manipulation_check", "unknown"]
        # Basic fuzzy matching or cleaning
        for intent in valid_intents:
            if intent in result:
                return intent
        return "unknown"

    def detect_emotion(self, user_input: str) -> dict:
        messages = [
            {
                "role": "system", 
                "content": "You are an emotion and sentiment detector. Reply ONLY with JSON like: {\"emotion\": \"sad\", \"sentiment\": \"negative\"}"
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
        
        result = self.call_groq_model(messages, max_tokens=50)
        
        # Check for error message in result
        if any(err in result for err in ["Error", "trouble", "scrambled"]):
             return {"emotion": "neutral", "sentiment": "neutral"}

        try:
            # Extract JSON from response (robust finding)
            start_idx = result.find('{')
            end_idx = result.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = result[start_idx:end_idx]
                parsed_data = json.loads(json_str)
                
                emotion = parsed_data.get("emotion", "neutral")
                sentiment = parsed_data.get("sentiment", "neutral")
                return {"emotion": emotion, "sentiment": sentiment}
            
        except Exception as e:
            self.logger.warning(f"Failed to parse emotion JSON: {e}")
            
        return {"emotion": "neutral", "sentiment": "neutral"}

    def analyze(self, user_input: str, memory_manager=None) -> dict:
        context = ""
        if memory_manager:
            try:
                context = memory_manager.get_context_text()
            except Exception as e:
                self.logger.error(f"Memory manager error: {e}")

        intent = self.detect_intent(user_input)
        emotion_data = self.detect_emotion(user_input)
        sentiment = emotion_data.get("sentiment", "neutral")
        
        # Inject context into system prompt
        system_prompt = (
            f"You are Echo, a helpful AI assistant.\n"
            f"User's emotion: {emotion_data['emotion']}\n"
            f"User's intent: {intent}\n"
            f"Sentiment: {sentiment}\n"
            f"User said: {user_input}\n"
            "Reply as Echo with empathy and understanding (2-3 sentences):"
        )

        if context:
            system_prompt += f"\nRecent Context:\n{context}\n"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        response = self.call_groq_model(messages, max_tokens=150, temperature=0.8)
        
        # Save memory
        if memory_manager:
            try:
                memory_manager.add_memory(user_input, response)
            except Exception as e:
                self.logger.error(f"Failed to save memory: {e}")

        return {
            "intent": intent,
            "emotion": emotion_data["emotion"],
            "sentiment": emotion_data["sentiment"],
            "response": response
        }
