from gtts import gTTS
import tempfile
import logging
import base64
import io

class TextToSpeech:
    def __init__(self, lang="en"):
        self.lang = lang
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def text_to_audio_bytes(self, text: str) -> bytes:
        """Convert text to audio bytes (for API responses)"""
        if not text.strip():
            self.logger.warning("No text provided for speech synthesis.")
            return b""

        try:
            tts = gTTS(text=text, lang=self.lang)
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            return audio_buffer.read()
            
        except Exception as e:
            self.logger.error(f"GTTS error: {e}")
            return b""

    def text_to_base64_audio(self, text: str) -> str:
        """Convert text to base64 encoded audio (for web frontend)"""
        try:
            audio_bytes = self.text_to_audio_bytes(text)
            if audio_bytes:
                return base64.b64encode(audio_bytes).decode('utf-8')
            return ""
        except Exception as e:
            self.logger.error(f"Base64 encoding error: {e}")
            return ""

    def speak(self, text: str) -> str:
        """Generate speech file (for local development)"""
        if not text.strip():
            self.logger.warning("No text provided for speech synthesis.")
            return ""

        try:
            tts = gTTS(text=text, lang=self.lang)
            temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tts.save(temp.name)
            return temp.name
        except Exception as e:
            self.logger.error(f"GTTS error: {e}")
            return "[TTS Error]: Failed to generate speech"

    def speak_to_response(self, text: str) -> dict:
        """Generate speech and return as API response format"""
        try:
            audio_base64 = self.text_to_base64_audio(text)
            if audio_base64:
                return {
                    "success": True,
                    "audio": audio_base64,
                    "format": "mp3",
                    "text": text
                }
            else:
                return {"success": False, "error": "Failed to generate speech"}
        except Exception as e:
            self.logger.error(f"Speech generation error: {e}")
            return {"success": False, "error": str(e)}



# from modules.text_to_speech import TextToSpeech

# tts = TextToSpeech()
# tts.speak("Hello, how can I help you today?")
