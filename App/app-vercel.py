import streamlit as st
import requests
from datetime import datetime
import time
from streamlit_lottie import st_lottie
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'echo_backend'))
sys.path.append(os.path.join(project_root, 'Core_Brain'))

# Import components (Vercel-friendly version)
try:
    from Core_Brain.nlp_engine.personality_router import PersonalityRouter
    from Core_Brain.memory_manager import MemoryManager
    from Core_Brain.nlp_engine.nlp_engine import NLPEngine
    
    # Initialize components
    nlp = NLPEngine()
    memory = MemoryManager()
    router = PersonalityRouter()
    
    BACKEND_AVAILABLE = True
    logger.info("Backend components imported successfully")
    
except ImportError as e:
    logger.error(f"Backend integration failed: {e}")
    st.error(f"❌ Backend integration failed: {str(e)}")
    BACKEND_AVAILABLE = False

# Initialize session state
if "selected_personality" not in st.session_state:
    st.session_state.selected_personality = "echo"
    if BACKEND_AVAILABLE:
        router.set_personality("echo")

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

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
        .vercel-notice {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
            color: #495057;
        }
    </style>
""", unsafe_allow_html=True)

# Vercel deployment notice
st.markdown("""
<div class="vercel-notice">
    <h4>🚀 Vercel Deployment Notice</h4>
    <p>This is a Vercel-optimized version of EchoV1. Audio recording features are disabled due to Vercel's serverless limitations.</p>
    <p><strong>Available features:</strong> Text input, emotion analysis, personality responses</p>
    <p><strong>Disabled features:</strong> Voice recording, audio playback</p>
</div>
""", unsafe_allow_html=True)

st.title("ECHO V1 - Your Emotional Companion")
st.markdown("**Powered by llama3-8b-8192**")
st.markdown("<div class='main-title'>🎧 ECHO V1 - Your Emotional Companion</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-text'>Type your message — Echo will understand and reply with empathy.</div>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # System status
    st.subheader("🔧 System Status")
    
    if BACKEND_AVAILABLE:
        st.markdown('<div class="status-online">🟢 All Systems Online</div>', unsafe_allow_html=True)
        st.write("✅ NLP Engine")
        st.write("✅ Memory Manager")
        st.write("✅ Personality Router")
    else:
        st.markdown('<div class="status-offline">🔴 Some Components Offline</div>', unsafe_allow_html=True)
        st.write("❌ Core components failed to load")
    
    # Personality settings
    st.subheader("🧑‍🤝‍🧑 Personality Settings")
    personalities = ["echo", "Suzi", "Legal Advisor", "Philosopher Mentor"]
    
    personality_choice = st.radio(
        "Choose Personality:",
        personalities,
        index=personalities.index(st.session_state.selected_personality)
    )
    
    if personality_choice != st.session_state.selected_personality:
        st.session_state.selected_personality = personality_choice
        if BACKEND_AVAILABLE:
            router.set_personality(personality_choice)
        st.success(f"✅ Personality switched to {personality_choice.title()}")

    # Memory settings
    st.subheader("🧠 Memory Settings")
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
    
    st.subheader("💬 Recent Conversations")
    if st.session_state.conversation_history:
        for i, conv in enumerate(reversed(st.session_state.conversation_history[-3:])):
            st.write(f"**You:** {conv['user'][:30]}...")
            st.write(f"**Echo:** {conv['response'][:30]}...")
            st.write("---")
    else:
        st.write("No conversations yet.")

# Main functionality
if not BACKEND_AVAILABLE:
    st.error("❌ Backend components not available. Please check your installation.")
    st.markdown("""
    ### Troubleshooting Steps:
    1. **Check Dependencies**: Ensure all required packages are installed
    2. **Verify File Structure**: Make sure Core_Brain and echo_backend folders exist
    3. **Check Imports**: Verify all import paths are correct
    4. **Run Tests**: Check individual components work
    """)
    st.stop()

# Text input interface
st.subheader("✍️ Chat with Echo")
user_input = st.text_area("Type your message here:", height=150, placeholder="Type your message...")

if st.button("📤 Send Message", use_container_width=True):
    if user_input.strip():
        with st.spinner("🧠 Analyzing your message..."):
            try:
                if nlp is None:
                    result = {
                        'intent': 'unknown',
                        'emotion': 'neutral',
                        'sentiment': 'neutral',
                        'response': 'Analysis component not available.'
                    }
                else:
                    # Use NLP analysis
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
                    st.metric("🎯 Intent", result['intent'].title())
                with col2_text:
                    st.metric("😊 Emotion", result['emotion'].title())  
                with col3_text:
                    st.metric("📊 Sentiment", result['sentiment'].title())
                
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
                st.error(f"❌ Analysis failed: {str(e)}")
    else:
        st.warning("⚠️ Please enter some text first.")

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** For best results, be clear and specific in your messages.")
if BACKEND_AVAILABLE and nlp:
    try:
        model_name = getattr(nlp, 'model_name', 'Unknown')
        st.markdown(f"🤖 **Echo Status:** Online | **Model:** {model_name}")
    except:
        st.markdown("🤖 **Echo Status:** Online")

# Vercel deployment info
st.markdown("---")
st.markdown("""
### 🚀 Deployment Information
- **Platform:** Vercel (Serverless)
- **Features:** Text-based interaction only
- **Limitations:** No audio recording/playback
- **Alternative:** Use Render.com for full audio features
""")
