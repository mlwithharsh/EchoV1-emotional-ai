from cryptography.fernet import Fernet
import uuid
from datetime import datetime
class MemoryManager:
    def __init__(self , key = None):
        if key is None:
            key = Fernet.generate_key()
        self.fernet = Fernet(key)

        self.history = []

    def add_memory(self, user, echo, session_id=None):
        try:
            if not session_id:
                session_id = str(uuid.uuid4())

            # Validate inputs
            if not user or not echo:
                print("Warning: Empty user or echo input, skipping memory storage")
                return

            encrypted_user = self.fernet.encrypt(user.encode()).decode()
            encrypted_echo = self.fernet.encrypt(echo.encode()).decode()

            self.history.append({
                "session": session_id,
                "user": encrypted_user,
                "echo": encrypted_echo,
                "timestamp": datetime.now().isoformat()
            })
                
            # Keep only last 5 conversations to prevent memory bloat
            if len(self.history) > 5:
                self.history.pop(0)
        except Exception as e:
            # Log error but don't crash the application
            print(f"Memory storage error: {e}")
            # Store unencrypted as fallback for critical conversations
            try:
                self.history.append({
                    "session": session_id or str(uuid.uuid4()),
                    "user": user,
                    "echo": echo,
                    "timestamp": datetime.now().isoformat(),
                    "encrypted": False
                })
                if len(self.history) > 5:
                    self.history.pop(0)
            except Exception as fallback_error:
                print(f"Fallback memory storage also failed: {fallback_error}")


    def get_context_text(self, session_id=None):
        try:
            if session_id:
                session_history = [
                    msg for msg in self.history if msg["session"] == session_id
                ]
            else:
                # If no session_id provided, return all history
                session_history = self.history

            context_parts = []
            for msg in session_history:
                try:
                    # Check if message is encrypted
                    if msg.get("encrypted", True):  # Default to True for backward compatibility
                        user_text = self.fernet.decrypt(msg['user'].encode()).decode()
                        echo_text = self.fernet.decrypt(msg['echo'].encode()).decode()
                    else:
                        # Unencrypted fallback
                        user_text = msg['user']
                        echo_text = msg['echo']
                    
                    context_parts.append(f"User: {user_text}\nEcho: {echo_text}")
                except Exception as msg_error:
                    print(f"Error processing message {msg.get('timestamp', 'unknown')}: {msg_error}")
                    continue
            
            return "\n".join(context_parts)
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