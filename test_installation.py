#!/usr/bin/env python3
"""
Test script to verify EchoV1 installation
Run this script to check if all components are working correctly.
"""

import sys
import os
import traceback

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    required_modules = [
        'streamlit',
        'requests', 
        'numpy',
        'pydub',
        'gtts',
        'cryptography',
        'dotenv'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"{module}")
        except ImportError as e:
            print(f" {module}: {e}")
            failed_imports.append(module)
    
    return len(failed_imports) == 0

def test_core_brain():
    """Test Core_Brain components"""
    print("\n Testing Core_Brain components...")
    
    try:
        project_root = os.path.dirname(os.path.abspath(__file__))
        sys.path.append(project_root)
        
        from Core_Brain import stt, tts, nlp, memory, get_core_status, is_core_ready
    
        print("Core_Brain imports successful")
        
        # Check component status
        status = get_core_status()
        print(f" Component status: {status}")
        
        if is_core_ready():
            print(" All core components ready")
            return True
        else:
            print("  Some components not ready")
            return False
            
    except Exception as e:
        print(f" Core_Brain test failed: {e}")
        traceback.print_exc()
        return False

def test_nlp_engine():
    """Test NLP engine functionality"""
    print("\n🤖 Testing NLP engine...")
    
    try:
        from Core_Brain.nlp_engine.nlp_engine import NLPEngine
        
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your_groq_api_key_here":
            print(" GROQ_API_KEY not set in .env file")
            return False
        
        nlp = NLPEngine()
        print("NLP Engine initialized")
        
        print(" NLP Engine test passed")
        return True
        
    except Exception as e:
        print(f" NLP Engine test failed: {e}")
        return False

def test_audio_components():
    """Test audio components"""
    print("\n🎤 Testing audio components...")
    
    try:
        from Core_Brain.speech_to_text import SpeechToText
        from Core_Brain.text_to_speech import TextToSpeech
        
        stt = SpeechToText()
        print(" Speech-to-Text initialized")
        
        tts = TextToSpeech()
        print("Text-to-Speech initialized")
        
        return True
        
    except Exception as e:
        print(f" Audio components test failed: {e}")
        return False

def main():
    """Main test function"""
    print("EchoV1 Installation Test")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Core Brain Test", test_core_brain),
        ("NLP Engine Test", test_nlp_engine),
        ("Audio Components Test", test_audio_components)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                print(f" {test_name} PASSED")
                passed += 1
            else:
                print(f" {test_name} FAILED")
        except Exception as e:
            print(f" {test_name} FAILED with exception: {e}")
    
    print(f"\n{'='*50}")
    print(f" Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! EchoV1 is ready to use.")
        print("\nNext steps:")
        print("1. Run: streamlit run App/app.py")
        print("2. Open http://localhost:8501 in your browser")
    else:
        print("  Some tests failed. Please check the errors above.")
        print("Make sure all dependencies are installed and .env file is configured.")

if __name__ == "__main__":
    main()
