#!/usr/bin/env python3
"""
Setup script for EchoV1 Emotional AI
This script helps set up the environment and install dependencies.
"""

import os
import sys
import subprocess
import shutil

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        print(" Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print(" Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print(" Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            shutil.copy(".env.example", ".env")
            print(" Created .env file from template")
            print("  Please edit .env file with your API keys")
        else:
            # Create basic .env file
            with open(".env", "w") as f:
                f.write("# EchoV1 Configuration\n")
                f.write("GROQ_API_KEY=your_groq_api_key_here\n")
            print("Created basic .env file")
            print("  Please edit .env file with your API keys")
    else:
        print(" .env file already exists")

def check_audio_dependencies():
    """Check if audio recording dependencies are available"""
    try:
        import sounddevice
        import soundfile
        print(" Audio recording dependencies available")
        return True
    except ImportError:
        print("  Audio recording dependencies not available")
        print("   Install with: pip install sounddevice soundfile")
        return False

def main():
    """Main setup function"""
    print("EchoV1 Emotional AI Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Check audio dependencies
    check_audio_dependencies()
    
    print("\n🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Edit .env file with your API keys")
    print("2. Run: streamlit run App/app.py")
    print("3. Open http://localhost:8501 in your browser")

if __name__ == "__main__":
    main()
