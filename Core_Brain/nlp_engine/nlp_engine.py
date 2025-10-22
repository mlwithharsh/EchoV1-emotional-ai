# NLP, intent detection, emotion sense
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import time
from functools import lru_cache
import requests
import logging
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, continue without it
    pass
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


class NLPEngine:
    def __init__(self, model_name="llama3-8b-8192"):
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        
        # Groq API setup for cloud deployment
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        

    def call_groq_model(self, messages, max_tokens=200, temperature=0.7):
        """Call Groq API - cloud-ready replacement for HF"""
        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 1,
            "stream": False
        }
        
        for attempt in range(3):
            try:
                response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)
                
                if not response.content:
                    self.logger.warning(f"[Attempt {attempt+1}] Empty response from model.")
                    if attempt < 2:  # Don't sleep on last attempt
                        time.sleep(3)
                    continue

                if response.status_code == 429:  # Rate limit
                    self.logger.warning(f"[Attempt {attempt+1}] Rate limit hit, waiting...")
                    if attempt < 2:  # Don't sleep on last attempt
                        time.sleep(5)
                    continue

                if response.status_code != 200:
                    self.logger.warning(f"[Attempt {attempt+1}] HTTP {response.status_code}: {response.text}")
                    if attempt < 2:  # Don't sleep on last attempt
                        time.sleep(3)
                    continue

                try:
                    result = response.json()
                    if "choices" in result and len(result["choices"]) > 0:
                        return result["choices"][0]["message"]["content"].strip()
                    else:
                        self.logger.warning(f"[Attempt {attempt+1}] Invalid response structure: {result}")
                        if attempt < 2:
                            time.sleep(3)
                        continue
                
                except Exception as e:
                    self.logger.error(f"[Attempt {attempt+1}] JSON parsing error: {e}")
                    if attempt < 2:
                        time.sleep(3)
                    continue

            except Exception as e:
                self.logger.error(f"[Attempt {attempt+1}] Request Error: {e}")
                if attempt < 2:
                    time.sleep(3)

        return "[Groq Error]: Failed after 3 attempts"


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
        valid_intents = ["greeting", "question", "request", "get_weather", "emotional_support", "manipulation_check", "unknown"]
        return result if result in valid_intents else "unknown"


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
        
        if result.startswith("[Groq Error]"):
            self.logger.warning(f"Groq API error in emotion detection: {result}")
            return {"emotion": "neutral", "sentiment": "neutral"}

        try:
            # Extract JSON from response
            start_idx = result.find('{')
            end_idx = result.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = result[start_idx:end_idx]
                parsed_data = json.loads(json_str)
                
                # Validate required fields
                if "emotion" in parsed_data and "sentiment" in parsed_data:
                    # Validate emotion and sentiment values
                    valid_emotions = ["happy", "sad", "angry", "fear", "surprise", "disgust", "neutral"]
                    valid_sentiments = ["positive", "negative", "neutral"]
                    
                    emotion = parsed_data.get("emotion", "neutral")
                    sentiment = parsed_data.get("sentiment", "neutral")
                    
                    if emotion not in valid_emotions:
                        emotion = "neutral"
                    if sentiment not in valid_sentiments:
                        sentiment = "neutral"
                        
                    return {"emotion": emotion, "sentiment": sentiment}
                else:
                    self.logger.warning(f"Missing required fields in emotion detection response: {parsed_data}")
                    return {"emotion": "neutral", "sentiment": "neutral"}
            else:
                self.logger.warning(f"No valid JSON found in emotion detection response: {result}")
                return {"emotion": "neutral", "sentiment": "neutral"}
            
        except json.JSONDecodeError as e:
            self.logger.error(f"[JSON Parsing Error]: {e}")
        except Exception as e:
            self.logger.error(f"[Unexpected Error in emotion detection]: {e}")
            
        # Default fallback
        return {"emotion": "neutral", "sentiment": "neutral"}

    # def generate_response(self,intent: str , emotion: str , user_input: str) -> str:
    #     system_prompt = (
    #         f"You are Echo, a caring AI assistant. The user is showing '{emotion}' emotion. "
    #         f"The intent is '{intent}'. Reply in a helpful, warm, or insightful way."
    #         )
    #     return self._call_llm(system_prompt, user_input, max_tokens=300)


    def analyze(self, user_input: str, memory_manager=None) -> dict:
        context = ""
        if memory_manager:
            context = memory_manager.get_context_text()

        intent = self.detect_intent(user_input)
        emotion_data = self.detect_emotion(user_input)
        sentiment = emotion_data.get("sentiment", "neutral") if emotion_data else "neutral"
        text = user_input

        # Inject context into system prompt for better LLM reply
        system_prompt = (
            f"You are Echo, a helpful AI assistant.\n"
            f"User's emotion: {emotion_data['emotion']}\n"
            f"User's intent: {intent}\n"
            f"Sentiment: {sentiment}\n"
            f"User said: {text}\n"
            "Reply as Echo with empathy and understanding (2-3 sentences):"
        )

        if context:
            system_prompt += f"\nHere is the recent conversation:\n{context}\nRespond appropriately."

        # Generate the response using chat format
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        response = self.call_groq_model(messages, max_tokens=150, temperature=0.8)
        
        # Save memory
        if memory_manager:
            memory_manager.add_memory(user_input, response)

        return {
            "intent": intent,
            "emotion": emotion_data["emotion"],
            "sentiment": emotion_data["sentiment"],
            "response": response
        }
