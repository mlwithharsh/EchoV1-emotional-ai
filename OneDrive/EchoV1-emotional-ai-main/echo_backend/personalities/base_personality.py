class BasePersonality:
    def __init__(self, name , goals, style):
        self.name = name
        self.style = style
        self.goals = goals

    def respond(self,user_input, memory):
        """Default response if child personality doesn't override."""
        return f"{self.name} says: I am still learning how to respond."

