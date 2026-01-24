
import sys
import platform

print(f"Python Version: {sys.version}")
print(f"Platform: {platform.platform()}")

try:
    import pydub
    print(f"Pydub imported. Version: {pydub.__version__ if hasattr(pydub, '__version__') else 'unknown'}")
    from pydub import AudioSegment
    print("AudioSegment imported")
except ImportError as e:
    print(f"Pydub import failed: {e}")
except Exception as e:
    print(f"Pydub error: {e}")

try:
    import audioop
    print("audioop imported from stdlib")
except ImportError:
    print("audioop NOT found in stdlib")
    try:
        import pyaudioop
        print("pyaudioop imported")
    except ImportError:
        print("pyaudioop NOT found")
