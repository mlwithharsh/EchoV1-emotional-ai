import logging
from .speech_to_text import SpeechToText 
from .text_to_speech import TextToSpeech 
from .memory_manager import MemoryManager
from .nlp_engine.nlp_engine import NLPEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

__version__ = "1.0.0"
__description__ = "Core AI Assistant Brain - Integrated Speech, NLP, and Memory"

def _initialize_components():
    """Initialize all core components with proper error handling."""
    components = {}
    
    try:
        components['stt'] = SpeechToText(model_name="small")
        logger.info("Speech-to-Text initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Speech-to-Text: {e}")
        components['stt'] = None
    
    try:
        components['tts'] = TextToSpeech()
        logger.info("Text-to-Speech initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Text-to-Speech: {e}")
        components['tts'] = None
    
    try:
        components['nlp'] = NLPEngine()
        logger.info("NLP Engine initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize NLP Engine: {e}")
        components['nlp'] = None
    
    try:
        components['memory'] = MemoryManager()
        logger.info("Memory Manager initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Memory Manager: {e}")
        components['memory'] = None
    
    return components

_components = _initialize_components()

stt = _components['stt']
tts = _components['tts'] 
nlp = _components['nlp']
memory = _components['memory']

__all__ = [
    'SpeechToText',
    'TextToSpeech', 
    'NLPEngine',
    'MemoryManager',
    'stt',
    'tts',
    'nlp', 
    'memory'
]

def get_core_status():
    """
    Get the initialization status of all core components.
    
    Returns:
        dict: Status of each component (True if initialized, False if failed)
    """
    return {
        'speech_to_text': stt is not None,
        'text_to_speech': tts is not None,
        'nlp_engine': nlp is not None,
        'memory_manager': memory is not None
    }

def is_core_ready():
    """
    Check if all core components are ready.
    
    Returns:
        bool: True if all components initialized successfully
    """
    status = get_core_status()
    return all(status.values())

if is_core_ready():
    logger.info("All core brain components initialized successfully")
else:
    failed_components = [name for name, status in get_core_status().items() if not status]
    logger.warning(f"Some components failed to initialize: {failed_components}")
