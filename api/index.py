import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Simple HTML response
HTML_RESPONSE = """
<!DOCTYPE html>
<html>
<head>
    <title>ECHO V1 - Your Emotional Companion</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 20px; }
        .chat-container { background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px; min-height: 300px; }
        .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .user-message { background: #007bff; color: white; text-align: right; }
        .echo-message { background: #e9ecef; }
        .input-container { display: flex; gap: 10px; }
        .input-container input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        .input-container button { padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 ECHO V1</h1>
        <p>Your Emotional AI Companion</p>
    </div>
    
    <div class="chat-container" id="chatContainer">
        <div class="message echo-message">
            <strong>Echo:</strong> Hello! I'm your emotional AI companion. How are you feeling today?
        </div>
    </div>
    
    <div class="input-container">
        <input type="text" id="userInput" placeholder="Type your message here..." onkeypress="handleKeyPress(event)">
        <button onclick="sendMessage()">Send</button>
    </div>

    <script>
        function handleKeyPress(event) {
            if (event.key === 'Enter') sendMessage();
        }
        
        function sendMessage() {
            const input = document.getElementById('userInput');
            const message = input.value.trim();
            if (!message) return;
            
            // Add user message
            addMessage(message, 'user');
            input.value = '';
            
            // Add loading message
            addMessage('Thinking...', 'echo');
            
            // Send to API
            fetch('/api/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: message})
            })
            .then(response => response.json())
            .then(data => {
                // Remove loading message
                const chatContainer = document.getElementById('chatContainer');
                chatContainer.removeChild(chatContainer.lastChild);
                
                // Add response
                addMessage(data.response || 'Sorry, I encountered an error.', 'echo');
            })
            .catch(error => {
                // Remove loading message
                const chatContainer = document.getElementById('chatContainer');
                chatContainer.removeChild(chatContainer.lastChild);
                addMessage('Sorry, I encountered an error. Please try again.', 'echo');
            });
        }
        
        function addMessage(text, sender) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.innerHTML = `<strong>${sender === 'user' ? 'You' : 'Echo'}:</strong> ${text}`;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return HTML_RESPONSE

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message.strip():
            return jsonify({'response': 'Please enter a message.'})
        
        # Simple response without heavy AI processing for now
        responses = [
            "I understand you're feeling that way. I'm here to listen and support you.",
            "That sounds challenging. How can I help you work through this?",
            "I hear you. Your feelings are valid and important.",
            "Thank you for sharing that with me. I'm here for you.",
            "That's a lot to process. Take your time, I'm listening."
        ]
        
        import random
        response = random.choice(responses)
        
        return jsonify({
            'response': response,
            'intent': 'emotional_support',
            'emotion': 'caring',
            'sentiment': 'positive'
        })
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({
            'response': 'I encountered an error processing your message. Please try again.'
        })

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
