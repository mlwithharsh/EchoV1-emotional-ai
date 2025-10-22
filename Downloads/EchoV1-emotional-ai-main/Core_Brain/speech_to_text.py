
# speech_to_text.py - Cloud deployment ready
import whisper
from pydub import AudioSegment
import tempfile 
import logging
import io
import base64

class SpeechToText:
    def __init__(self, model_name="small", sample_rate=16000):
        self.model = whisper.load_model(model_name)
        self.sample_rate = sample_rate
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def process_audio_bytes(self, audio_bytes: bytes) -> str:
        """Process audio bytes directly (from web upload or API)"""
        try:
            # Create temporary file from bytes
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name
            
            # Process and transcribe
            audio = self.process_audio(temp_file_path)
            return self.transcribe(audio)
            
        except Exception as e:
            self.logger.error(f"Error processing audio bytes: {e}")
            return ""

    def process_base64_audio(self, base64_audio: str) -> str:
        """Process base64 encoded audio (from web frontend)"""
        try:
            # Decode base64 to bytes
            audio_bytes = base64.b64decode(base64_audio)
            return self.process_audio_bytes(audio_bytes)
            
        except Exception as e:
            self.logger.error(f"Error processing base64 audio: {e}")
            return ""

    def process_audio(self, audio_path: str) -> AudioSegment:
        """Process audio file to correct format"""
        try:
            audio = AudioSegment.from_file(audio_path)
            audio = audio.set_frame_rate(16000)
            audio = audio.set_channels(1)
            audio = audio.set_sample_width(2)  # 16-bit PCM
            audio = audio.normalize()
            return audio
        except Exception as e:
            self.logger.error(f"Error processing audio: {e}")
            return None

    def transcribe(self, audio_segment: AudioSegment) -> str:
        """Transcribe audio segment to text"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
                audio_segment.export(temp.name, format="wav")
                result = self.model.transcribe(temp.name, language="en", task="transcribe")
                return result['text'].strip()
                
        except Exception as e:
            self.logger.error(f"Error during transcription: {e}")
            return ""

    def transcribe_file(self, file_path: str) -> str:
        """Transcribe audio file directly"""
        try:
            audio = self.process_audio(file_path)
            if audio:
                return self.transcribe(audio)
            return ""
        except Exception as e:
            self.logger.error(f"Error during file transcription: {e}")
            return ""

    def record_audio(self, duration: int = 5) -> str:
        """Record audio for specified duration and return file path"""
        try:
            import sounddevice as sd
            import soundfile as sf
            import tempfile
            
            # Record audio
            sample_rate = 16000
            audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
            sd.wait()  # Wait until recording is finished
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                sf.write(temp_file.name, audio_data, sample_rate)
                return temp_file.name
                
        except ImportError:
            self.logger.error("sounddevice and soundfile are required for audio recording. Install with: pip install sounddevice soundfile")
            return ""
        except Exception as e:
            self.logger.error(f"Error during audio recording: {e}")
            return ""





# main() function use 
# from modules.speech_to_text import SpeechToText

# stt = SpeechToText(model_name="small")
# raw_audio = stt.record_audio(duration=5)
# audio_segment = stt.numpy_to_audiosegment(raw_audio)
# clean_audio = stt.preprocess(audio_segment)
# text = stt.transcribe(clean_audio)

# print("User said:", text)
