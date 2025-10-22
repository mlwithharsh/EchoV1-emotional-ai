from cryptography.fernet import Fernet
import uuid
from datetime import datetime
class MemoryManager:
    def __init__(self , key = None):
        if key is None:
            key = Fernet.generate_key()
        self.fernet = Fernet(key)

        self.history = []

    def add_memory(self, user ,echo , session_id = None):
        try:
            if not session_id:
                session_id = str(uuid.uuid4())

            encrypted_user = self.fernet.encrypt(user.encode()).decode()
            encrypted_echo = self.fernet.encrypt(echo.encode()).decode()

            self.history.append({
                "session": session_id,
                "user": encrypted_user,
                "echo": encrypted_echo,
                "timestamp": datetime.now().isoformat()
                })
                
            if len(self.history) > 5:
                self.history.pop(0)
        except Exception as e:
            # Log error but don't crash the application
            print(f"Memory storage error: {e}")


    def get_context_text(self , session_id = None):
        try:
            if session_id:
                session_history = [
                    msg for msg in self.history if msg["session"] == session_id
                ]
            else:
                # If no session_id provided, return all history
                session_history = self.history

            return "\n".join([
                f"User: {self.fernet.decrypt(msg['user'].encode()).decode()}\n"
                f"Echo: {self.fernet.decrypt(msg['echo'].encode()).decode()}"
                for msg in session_history
            ])
        except Exception as e:
            # Return empty context if decryption fails
            print(f"Memory retrieval error: {e}")
            return ""

        
    # Inside MemoryManager class
    def clear_memory(self , session_id = None):
        if session_id:
            self.history = [
                msg for msg in self.history if msg["session"] != session_id
            ]
        else:
            self.history = []


#     def get_content(self):
#         return self.history