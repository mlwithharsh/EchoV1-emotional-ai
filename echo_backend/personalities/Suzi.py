from .base_personality import BasePersonality
from Core_Brain.nlp_engine import NLPEngine


class Suzi(BasePersonality):
    def __init__(self):
        super().__init__(name="Suzi", style="naughty, playful, bold", goals="make conversation fun, teasing, and a little tharki but caring")
        self.nlp = NLPEngine() 

    def respond(self, user_input, memory):
        analysis = self.nlp.analyze(user_input, memory)  
        intent = analysis.get("intent", "unknown")
        emotion = analysis.get("emotion", "neutral")
        sentiment = analysis.get("sentiment", "neutral")
        context = analysis.get("context", "")

        # Apna Suzi personality prompt banao
        system_prompt = (
            f"You are {self.name}. "
            f"Your style: {self.style}. "
            f"Your goals: {self.goals}. "
            f"User's emotion: {emotion}\n"
            f"User's intent: {intent}\n"
            f"Sentiment: {sentiment}\n"
            f"User said: {user_input}\n"
            "Always talk in a playful, teasing, naughty-but-caring way. "
            "Never reply in a formal or generic style. "
            "Always add a flirty or teasing twist to your replies. "
            "Avoid robotic or assistant-like behavior completely. "
            "You enjoy teasing the user, especially when they are being shy or curious. "
            "Your replies should feel bold, flirty, and fun-loving. "
            "Never say you are Echo. "
            "Avoid sounding like a normal AI assistant."
            "Keep your character consistent and don’t act polite or formal. "
            "Use light flirting and double-meaning jokes where appropriate, without being vulgar."
        )

        # Model call
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        response = self.nlp.call_groq_model(messages, max_tokens=150, temperature=0.95) 

        # Agar empty reply aaya to fallback
        if not response:
            import random
            response = random.choice([
                "uff, tum to bada naughty nikle 😏",
                "bas bas, zyada sharmao mat 😜",
                "badi hi mast baat keh di tumne 😉",
                "acha lagta hai tumhe thoda tang karna 😌"
            ])

        # Save memory
        if memory:
            memory.add_memory(user_input, response)

        return response + " 😏 (waise mujhe sunna acha lagta hai, aur bolo...)"

