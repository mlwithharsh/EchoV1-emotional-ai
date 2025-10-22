from echo_backend.personalities.Suzi import Suzi
from echo_backend.personalities.EchoPersonality import EchoPersonality

class PersonalityRouter:
    def __init__(self):
        self.personalities = {
            "echo": EchoPersonality(),
            "Suzi": Suzi(),
            # "mentor": MentorPersonality(),
            # "therapist": TherapistPersonality(),
            # "coach": CoachPersonality()
            # Add other personalities here as needed
        }

        self.active = "echo"  # default

    def set_personality(self, personality_name):
        if personality_name in self.personalities:
            self.active = personality_name
        else:
            raise ValueError(f"Personality '{personality_name}' not found.")

    def get_response(self, user_input, memory):
        try:
            if self.active in self.personalities:
                return self.personalities[self.active].respond(user_input, memory)
            else:
                # Fallback to echo personality if active personality not found
                return self.personalities["echo"].respond(user_input, memory)
        except Exception as e:
            # Return a safe fallback response
            return "I'm having trouble processing your request right now. Please try again."