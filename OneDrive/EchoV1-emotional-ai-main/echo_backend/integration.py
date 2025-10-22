# Connects APIs, services, etc.
import logging
import sys
import os

# Add the Core_Brain path to sys.path if not already there
current_dir = os.path.dirname(os.path.abspath(__file__))
core_brain_path = os.path.join(current_dir, '..', 'Core_Brain')
if core_brain_path not in sys.path:
    sys.path.append(core_brain_path)

# Add the project root to sys.path for proper imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

logger = logging.getLogger(__name__)

def initialize_components():
    """Initialize all components with proper error handling"""
    try:
        # Try to import Core_Brain components
        from Core_Brain import stt, tts, nlp, memory, get_core_status, is_core_ready        
        # Verify components are initialized
        if not is_core_ready():
            logger.warning("Some core components failed to initialize")
            status = get_core_status()
            failed = [name for name, ready in status.items() if not ready]
            logger.warning(f"Failed components: {failed}")
        
        return {
            'stt': stt,
            'tts': tts, 
            'nlp': nlp,
            'memory': memory,
            'get_core_status': get_core_status,
            'is_core_ready': is_core_ready
        }
        
    except ImportError as e:
        logger.error(f"Failed to import Core_Brain components: {e}")
        return None

# Initialize components
_components = initialize_components()

# Export components (with None fallbacks)
if _components:
    stt = _components['stt']
    tts = _components['tts'] 
    nlp = _components['nlp']
    memory = _components['memory']
    get_core_status = _components['get_core_status']
    is_core_ready = _components['is_core_ready']
else:
    stt = None
    tts = None
    nlp = None 
    memory = None
    get_core_status = lambda: {}
    is_core_ready = lambda: False

def pipeline(audio_file_path: str) -> dict:
    """Process audio through the complete pipeline"""
    
    if not _components:
        return {
            "error": "Backend components not available",
            "transcribed_text": "",
            "intent": "unknown",
            "emotion": "neutral", 
            "sentiment": "neutral",
            "response_text": "Backend integration failed. Components not initialized."
        }
    
    try:
        # Transcribe audio
        if stt is None:
            raise Exception("Speech-to-Text component not available")
        
        text = stt.transcribe_file(audio_file_path)
        
        if not text or text.strip() == "":
            return {
                "transcribed_text": "",
                "intent": "unknown",
                "emotion": "neutral",
                "sentiment": "neutral", 
                "response_text": "No speech detected in audio file."
            }
        
        # Analyze with NLP
        if nlp is None:
            result = {
                'intent': 'unknown',
                'emotion': 'neutral',
                'sentiment': 'neutral',
                'response': 'Analysis component not available.'
            }
        else:
            result = nlp.analyze(text, memory_manager=memory)
        
        # Generate speech response
        audio_response_path = None
        if tts is not None:
            try:
                audio_response = tts.speak(result["response"])
                if audio_response and not "[TTS Error]" in str(audio_response):
                    audio_response_path = audio_response
            except Exception as e:
                logger.warning(f"Text-to-speech failed: {e}")
        
        return {
            "transcribed_text": text,
            "intent": result['intent'],
            "emotion": result['emotion'],
            "sentiment": result['sentiment'], 
            "response_text": result['response'],
            "response_audio_path": audio_response_path
        }
        
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        return {
            "error": str(e),
            "transcribed_text": "",
            "intent": "unknown",
            "emotion": "neutral",
            "sentiment": "neutral",
            "response_text": f"Pipeline failed: {str(e)}"
        }
