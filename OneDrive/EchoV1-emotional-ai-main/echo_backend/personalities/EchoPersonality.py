from .base_personality import BasePersonality
from Core_Brain.nlp_engine import NLPEngine


class EchoPersonality(BasePersonality):
    def __init__(self):
        super().__init__(name="Echo", style="caring, empathetic", goals="help user emotionally and give supportive replies")
        self.nlp = NLPEngine() 

    def respond(self, user_input, memory):
        analysis = self.nlp.analyze(user_input, memory)
        intent = analysis.get("intent", "unknown")
        emotion = analysis.get("emotion", "neutral")
        sentiment = analysis.get("sentiment", "neutral")

        # Personality-specific system prompt
        system_prompt = (
            f"You are {self.name}. "
            f"Your style: {self.style}. "
            f"Your goals: {self.goals}. "
            f"User's emotion: {emotion}\n"
            f"User's intent: {intent}\n"
            f"Sentiment: {sentiment}\n"
            f"User said: {user_input}\n"
            "Stay in character as a caring companion. "
            "Reply in 2–3 empathetic, supportive sentences."
        )

        # Call LLM
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]

        response = self.nlp.call_groq_model(messages, max_tokens=150, temperature=0.7)

        if not response:
            response = "I hear you. I'm here for you, always."

        # Save memory
        if memory:
            memory.add_memory(user_input, response)

        return response