import streamlit as st
import requests
from datetime import datetime
import time
from streamlit_lottie import st_lottie
import os
import sys
import logging
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from Core_Brain.nlp_engine.personality_router import PersonalityRouter
from Core_Brain.memory_manager import MemoryManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, '..'))
sys.path.append(os.path.join(current_dir, '..', 'echo_backend'))
sys.path.append(os.path.join(current_dir, '..', 'Core_Brain'))

# Try to import backend components with better error handling
BACKEND_AVAILABLE = False
components = {}

try:
    # Import from echo_backend.integration
    from echo_backend.integration import (
        stt, tts, nlp, memory, pipeline, 
        get_core_status, is_core_ready
    )

    from Core_Brain.nlp_engine import NLPEngine

    nlp = NLPEngine()
    
    components = {
        'stt': stt,
        'tts': tts,
        'nlp': nlp, 
        'memory': memory,
        'pipeline': pipeline,
        'get_core_status': get_core_status,
        'is_core_ready': is_core_ready
    }
    
    BACKEND_AVAILABLE = True
    logger.info("Backend components imported successfully")
    
except ImportError as e:
    logger.error(f"Backend integration failed: {e}")
    st.error(f"❌ Backend integration failed: {str(e)}")
    
    # Create dummy functions for graceful degradation
    components = {
        'stt': None,
        'tts': None,
        'nlp': None,
        'memory': None,
        'pipeline': None,
        'get_core_status': lambda: {'all_components': False},
        'is_core_ready': lambda: False
    }

router = PersonalityRouter()
if "selected_personality" not in st.session_state:
    st.session_state.selected_personality = "echo"  # default
    router.set_personality("echo")

# Extract components
stt = components['stt']
tts = components['tts'] 
nlp = components['nlp']
memory = components['memory']
pipeline = components['pipeline']
get_core_status = components['get_core_status']
is_core_ready = components['is_core_ready']

st.set_page_config(page_title="ECHO V1", page_icon="🤖", layout="centered")

st.markdown("""
    <style>
        body {
            background-color: #0f1117;
            color: #ffffff;
        }
        .main-title {
            font-size: 3rem;
            font-weight: 700;
            color: #333;
            margin-bottom: 0.5rem;
        }
        .sub-text {
            font-size: 1.2rem;
            color: #666;
        }
        .stMetric {
            background-color: #2e2e2e;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            color: #ffffff;
            font-size: 14px
        }
        .section-box {
            background-color: #fff;
            padding: 20px;
            margin-top: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        }
        .status-online {
            color: #28a745;
            font-weight: bold;
        }
        .status-offline {
            color: #dc3545;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'recording_duration' not in st.session_state:
    st.session_state.recording_duration = 5

st.title("ECHO V1 - Your Emotional Companion")
st.markdown("**Powered by llama3-8b-8192**")
st.markdown("<div class='main-title'>🎧 ECHO V1 - Your Emotional Companion</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-text'>Upload or record your voice — Echo will listen, understand, and reply with empathy.</div>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # System status
    st.subheader("🔧 System Status")
    
    if BACKEND_AVAILABLE:
        try:
            core_ready = is_core_ready()
            if core_ready:
                st.markdown('<div class="status-online">🟢 All Systems Online</div>', unsafe_allow_html=True)
                
                # Show detailed status
                status = get_core_status()
                for component, is_ready in status.items():
                    icon = "✅" if is_ready else "❌"
                    component_name = component.replace('_', ' ').title()
                    st.write(f"{icon} {component_name}")
            else:
                st.markdown('<div class="status-offline">🔴 Some Components Offline</div>', unsafe_allow_html=True)
                status = get_core_status()
                for component, is_ready in status.items():
                    icon = "✅" if is_ready else "❌"
                    component_name = component.replace('_', ' ').title()
                    st.write(f"{icon} {component_name}")
        except Exception as e:
            st.markdown('<div class="status-offline">🔴 Status Check Failed</div>', unsafe_allow_html=True)
            st.write(f"Error: {str(e)}")
    else:
        st.markdown('<div class="status-offline"> Backend Not Available</div>', unsafe_allow_html=True)
        st.write(" Core components failed to load")

    st.subheader("🎤 Recording Settings")
    st.session_state.recording_duration = st.slider(
        "Recording Duration (seconds)", 
        min_value=3, 
        max_value=30, 
        value=st.session_state.recording_duration,
        help="How long to record audio"
    )
    
    # personality integration
    st.subheader("🧑‍🤝‍🧑 Personality Settings")
    personalities = ["echo", "Suzi", "Legal Advisor", "Philosopher Mentor"]
    if "selected_personality" not in st.session_state:
        st.session_state.selected_personality = "echo"

    personality_choice = st.radio(
        "Choose Personality:",
        personalities,
        index=personalities.index(st.session_state.selected_personality)
    )

    
    if personality_choice != st.session_state.selected_personality:
        st.session_state.selected_personality = personality_choice
        router.set_personality(personality_choice)
        st.success(f" Personality switched to {personality_choice.title()}")



    # Memory settings
    st.subheader(" Memory Settings")
    if st.button("Clear Conversation History"):
        if BACKEND_AVAILABLE and memory:
            try:
                memory.clear_memory()
            except Exception as e:
                logger.warning(f"Failed to clear memory: {e}")
        st.session_state.conversation_history = []
        st.success("Memory cleared!")
        time.sleep(1)
        st.rerun()
    
    st.subheader(" Recent Conversations")
    if st.session_state.conversation_history:
        for i, conv in enumerate(reversed(st.session_state.conversation_history[-3:])):
            st.write(f"**You:** {conv['user'][:30]}...")
            st.write(f"**Echo:** {conv['response'][:30]}...")
            st.write("---")
    else:
        st.write("No conversations yet.")

# # Load Lottie animation
# @st.cache_data
# def load_lottie_url(url: str):
#     try:
#         response = requests.get(url, timeout=5)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             return None
#     except Exception as e:
#         logger.warning(f"Failed to load animation: {e}")
#         return None

# # Try to load animation
# animation = load_lottie_url("https://assets5.lottiefiles.com/packages/lf20_touohxv0.json")
# if animation:
#     st_lottie(animation, height=200, key="listening")

# Main functionality
if not BACKEND_AVAILABLE:
    st.error(" Backend components not available. Please check your installation.")
    st.markdown("""
    ### Troubleshooting Steps:
    1. **Check Dependencies**: Ensure all required packages are installed
    2. **Verify File Structure**: Make sure Core_Brain and echo_backend folders exist
    3. **Check Imports**: Verify all import paths are correct
    4. **Run Tests**: Check individual components work
    """)
    st.stop()

col1, col2 = st.columns([2, 1])

with col1:
    if st.button("🎙️ Record Audio", use_container_width=True):
        if stt is None:
            st.error(" Speech-to-Text component not available")
        else:
            # Recording phase
            with st.spinner(f"🎙️ Recording for {st.session_state.recording_duration} seconds... Speak now!"):
                try:
                    audio_path = stt.record_audio(duration=st.session_state.recording_duration)
                    if not audio_path or not os.path.exists(audio_path):
                        st.error(" Recording failed - no audio file created")
                        st.stop()
                except Exception as e:
                    st.error(f" Recording failed: {str(e)}")
                    st.stop()

            # Processing phase
            with st.spinner(" Processing your message..."):
                try:
                    result = pipeline(audio_path)
                    
                    if "error" in result:
                        st.error(f" Processing failed: {result['error']}")
                        st.stop()
                    
                    if not result['transcribed_text'].strip():
                        st.warning(" No speech detected. Please try again.")
                        st.stop()
                        
                except Exception as e:
                    st.error(f" Processing failed: {str(e)}")
                    st.stop()

            # Display results
            st.subheader(" What You Said")
            st.success(result['transcribed_text'])

            # Metrics
            col1_metric, col2_metric, col3_metric = st.columns(3)
            with col1_metric:
                st.metric(" Intent", result['intent'].title())
            with col2_metric:
                st.metric("Emotion", result['emotion'].title())
            with col3_metric:
                st.metric(" Sentiment", result['sentiment'].title())

            st.subheader("Echo's Response")
            personality_response = router.get_response(result['transcribed_text'], memory)
            st.info(personality_response)
            result['response_text'] = personality_response

            # Audio response
            if result.get('response_audio_path') and os.path.exists(result['response_audio_path']):
                st.audio(result['response_audio_path'], format="audio/mp3")
                # Clean up
                try:
                    time.sleep(1)
                    os.remove(result['response_audio_path'])
                except:
                    pass

            # Save to history
            st.session_state.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'user': result['transcribed_text'],
                'response': result['response_text'],
                'intent': result['intent'],
                'emotion': result['emotion'],
                'sentiment': result['sentiment']
            })

            # Clean up audio file
            try:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
            except:
                pass

with col2:
    st.subheader("✍️ Or Type Instead")
    user_input = st.text_area("Type your message here:", height=150, placeholder="Type your message...")

    if st.button("📤 Send Text", use_container_width=True):
        if user_input.strip():
            with st.spinner(" Analyzing your message..."):
                try:
                    if nlp is None:
                        result = {
                            'intent': 'unknown',
                            'emotion': 'neutral',
                            'sentiment': 'neutral',
                            'response': 'Analysis component not available.'
                        }
                    else:
                        # Use NLP analysis instead of hardcoded values
                        analysis = nlp.analyze(user_input, memory)
                        personality_response = router.get_response(user_input, memory)

                        result = {
                            'intent': analysis['intent'],
                            'emotion': analysis['emotion'],
                            'sentiment': analysis['sentiment'],
                            'response': personality_response
                        }

                    # Display results
                    col1_text, col2_text, col3_text = st.columns(3)
                    with col1_text:
                        st.metric(" Intent", result['intent'].title())
                    with col2_text:
                        st.metric(" Emotion", result['emotion'].title())  
                    with col3_text:
                        st.metric("Sentiment", result['sentiment'].title())
                    
                    st.info(result['response'])

                    # Add to history
                    st.session_state.conversation_history.append({
                        'timestamp': datetime.now().isoformat(),
                        'user': user_input,
                        'response': result['response'],
                        'intent': result['intent'],
                        'emotion': result['emotion'],
                        'sentiment': result['sentiment']
                    })

                except Exception as e:
                    st.error(f" Analysis failed: {str(e)}")
        else:
            st.warning("⚠️ Please enter some text first.")

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** For best results, speak clearly and close to your microphone.")
if BACKEND_AVAILABLE and nlp:
    try:
        model_name = getattr(nlp, 'model_name', 'Unknown')
        st.markdown(f" **Echo Status:** Online | **Model:** {model_name}")
    except:
        st.markdown("**Echo Status:** Online")