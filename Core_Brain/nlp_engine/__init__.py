from .nlp_engine import NLPEngine

# Package metadata
__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "NLP Engine for intent detection and emotion analysis"

# Export main classes/functions
__all__ = [
    'NLPEngine',
]

DEFAULT_MODEL = "llama3-8b-8192"
SUPPORTED_INTENTS = [
    "greeting", 
    "question", 
    "request", 
    "get_weather", 
    "emotional_support", 
    "manipulation_check", 
    "unknown"
]

def create_nlp_engine(model_name=None):
    """
    Factory function to create an NLPEngine instance with default settings.
    
    Args:
        model_name (str, optional): Model to use. Defaults to DEFAULT_MODEL.
    
    Returns:
        NLPEngine: Configured NLP engine instance
    """
    return NLPEngine(model_name or DEFAULT_MODEL)
