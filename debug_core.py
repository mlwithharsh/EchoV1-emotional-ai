
import sys
import os
import logging

# Configure logging to print to stdout
try:
    import audioop
except ImportError:
    try:
        import audioop_lts as audioop
        import sys
        sys.modules["audioop"] = audioop
        print("Monkeypatched audioop with audioop_lts")
    except ImportError:
        print("Failed to import audioop and audioop_lts")

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

print("Starting debug_core.py")
try:
    from Core_Brain import stt, tts, nlp, memory, get_core_status, is_core_ready
    print("Imported Core_Brain successfully")
except ImportError as e:
    print(f"Failed to import Core_Brain: {e}")
    sys.exit(1)

print("Checking Core Status:")
status = get_core_status()
print(status)

if not is_core_ready():
    print("Core is NOT ready.")
    # Check checks manually to see the error, but __init__.py already logs errors.
    # We rely on logging to see the actual exception.
else:
    print("Core is READY.")
