import streamlit as st
import requests
from datetime import datetime
import time
from streamlit_lottie import st_lottie
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from echo_backend.integration import stt, tts, nlp, memory, pipeline
    from Core_Brain import get_core_status , is_core_ready
    BACKEND_AVAILABLE = True
except ImportError:
    st.error("Backend integration failed. Please check your setup.")
    BACKEND_AVAILABLE = False



st.set_page_config(page_title = "ECHO V1" , page_icon = "🤖", layout="centered")

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
            background-color: #ffffff;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }
        .section-box {
            background-color: #fff;
            padding: 20px;
            margin-top: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'recording_duration' not in st.session_state:
    st.session_state.recording_duration = 5  # Default recording duration in seconds

st.title("ECHO V1 - Your Emotional Companion")

st.markdown("**Powered by llama3-8b-8192**", unsafe_allow_html=True)
st.markdown("<div class='main-title'>🎧 ECHO V1 - Your Emotional Companion</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-text'>Upload or record your voice — Echo will listen, understand, and reply with empathy.</div>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Settings")
    
    # System status
    st.subheader("🔧 System Status")

    if BACKEND_AVAILABLE and is_core_ready():
        st.markdown('<div class="status-indicator status-online">🟢 All Systems Online</div>', unsafe_allow_html=True)
        
        # Show detailed status
        status = get_core_status()
        for component, is_ready in status.items():
            icon = "✅" if is_ready else "❌"
            st.write(f"{icon} {component.replace('_', ' ').title()}")
    else:
        st.markdown('<div class="status-indicator status-offline">🔴 System Issues Detected</div>', unsafe_allow_html=True)
    

    st.subheader("🎤 Recording Settings")
    st.session_state.recording_duration = st.slider(
        "Recording Duration (seconds)", 
        min_value=3, 
        max_value=30, 
        value=st.session_state.recording_duration,
        help="How long to record audio"
    )
    
    # Memory settings
    st.subheader("🧠 Memory Settings")
    if st.button("Clear Conversation History"):
        if BACKEND_AVAILABLE and memory:
            memory.clear_memory()
        st.session_state.conversation_history = []
        st.success("Memory cleared!")
        time.sleep(1)
        st.rerun()
    
    st.subheader("💬 Recent Conversations")
    if st.session_state.conversation_history:
        st.markdown('<div class="conversation-history">', unsafe_allow_html=True)
        for i, conv in enumerate(reversed(st.session_state.conversation_history[-5:])):  # Show last 5
            st.write(f"**You:** {conv['user'][:50]}...")
            st.write(f"**Echo:** {conv['response'][:50]}...")
            st.write("---")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.write("No conversations yet.")


# Load Lottie animation (enhanced with error handling)
@st.cache_data
def load_lottie_url(url: str):
    try:
        response = requests.get(url , timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to load animation: {response.status_code}")
            return None

    except Exception as e:
        st.error(f"Error loading Lottie animation: {str(e)}")
        return None

# Try to load animation
animation = load_lottie_url("https://assets5.lottiefiles.com/packages/lf20_touohxv0.json")
if animation:
    st_lottie(animation, height=200, key="listening")

if not BACKEND_AVAILABLE:
    st.error("❌ Backend components not available. Please check your installation.")
    st.stop()


if not is_core_ready():
    st.warning("⚠️ Some system components are not ready. Check the sidebar for details.")
    failed_components = [name for name, status in get_core_status().items() if not status]
    st.write(f"Failed components: {', '.join(failed_components)}")

col1 , col2 = st.columns([2, 1])

with col1:
    if st.button("Recording Audio" , use_container_width=True ):
        if stt is None :
            st.error("Speech-to-Text component not available")
        else:
            # Recording phase
            with st.spinner(f"Recording for {st.session_state.recording_duration} seconds... Speak now"):
                try:
                    audio_path = stt.record_audio(duration=st.session_state.recording_duration)
                except Exception as e:
                    st.error(f"Recording failed: {str(e)}")
                    audio_path = None

            if audio_path and os.path.exists(audio_path):
                # Transcription phase
                with st.spinner("Processing audio..."):
                    try:
                        text = stt.transcribe_file(audio_path)
                        if not text or text.strip() == "":
                            st.warning("No speech detected. Please try speaking louder or closer to the microphone.")
                            if os.path.exists(audio_path):
                                os.remove(audio_path)
                            st.stop()

                    except Exception as e:
                        st.error(f"Transcription failed: {str(e)}")
                        if os.path.exists(audio_path):
                            os.remove(audio_path)
                        st.stop()

            # NLP Analysis phase
                with st.spinner("Analyzing intent and emotion..."):
                    try:
                        if nlp is None:
                           result = {
                                'intent': 'unknown',
                                'emotion': 'neutral', 
                                'sentiment': 'neutral',
                                'response': 'I heard you, but my analysis system is currently unavailable.'
                            }

                        else:
                            result = nlp.analyze(text , memory_manager=memory)

                    except Exception as e:
                        stt.error(f"Analysis failed: {str(e)}")
                        result = {
                            'intent': 'unknown',
                            'emotion': 'neutral',
                            'sentiment': 'neutral',
                            'response': 'I heard you, but my analysis system is currently unavailable.'
                        }

# Display results
                st.subheader("📝 What You Said")
                st.success(text)

                # Metrics display
                col1_metric, col2_metric, col3_metric = st.columns(3)
                with col1_metric:
                    st.metric("🎯 Intent", result['intent'].title())
                with col2_metric:
                    st.metric("😊 Emotion", result['emotion'].title())
                with col3_metric:
                    st.metric("📊 Sentiment", result['sentiment'].title())

                st.subheader("💬 Echo's Response")
                st.info(result['response'])

                # Text-to-Speech phase
                if tts is not None:
                    with st.spinner("🔊 Generating speech..."):
                        try:
                            speech_result = tts.speak(result['response'])
                            
                            if "[TTS Error]" in speech_result:
                                st.warning("🔇 Text-to-speech failed due to internet or system issue.")
                            else:
                                # Extract audio file path
                                if "File saved at:" in speech_result:
                                    audio_path = speech_result.split("File saved at: ")[-1].strip()
                                else:
                                    audio_path = speech_result.strip()

                                if os.path.exists(audio_path):
                                    st.audio(audio_path, format="audio/mp3")
                                    # Clean up audio file after a delay
                                    try:
                                        time.sleep(1)  # Brief delay before cleanup
                                        os.remove(audio_path)
                                    except:
                                        pass  # Ignore cleanup errors
                        except Exception as e:
                            st.warning(f"Speech generation failed: {str(e)}")
                else:
                    st.info("Text-to-speech component not available.")


            # Save conversation history
                st.session_state.conversation_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'user': text,
                    'response': result['response'],
                    'intent': result['intent'],
                    'emotion': result['emotion'],
                    'sentiment': result['sentiment']
                })

                if os.path.exists(audio_path):
                    try:
                        os.remove(audio_path)
                    except:
                        pass    

            else:
                st.error("No audio data recorded. Please try again.")

with col2:
    # Text input alternative
    st.subheader("✍️ Or Type Instead")
    user_input = st.text_area("Type your message here:", height=150, placeholder="Type your message...")

    if st.button("Send Text", use_container_width=True):
        if user_input.strip():
            with st.spinner("🧠 Analyzing your message..."):
                try:
                    if nlp is None:
                        result = {
                            'intent': 'unknown',
                            'emotion': 'neutral',
                            'sentiment': 'neutral',
                            'response': 'I received your message, but my analysis system is currently unavailable.'
                        }

                    else:
                        result = nlp.analyze(user_input, memory_manager=memory)

                    st.success(f"**Intent:** {result['intent']} | **Emotion:** {result['emotion']} | **Sentiment:** {result['sentiment']}")
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
                    st.error(f"Analysis failed: {str(e)}")
        else:
            st.warning("Please enter some text first.")

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** For best results, speak clearly and close to your microphone.")
if BACKEND_AVAILABLE:
    st.markdown(f"🤖 **Echo Status:** Online | **Model:** {nlp.model_name if nlp else 'N/A'}")