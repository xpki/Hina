from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import config
from datetime import datetime, timedelta

# Setup
genai.configure(api_key=config.GEMINI_API_KEY)
app = Flask(__name__)
CORS(app)

# Session storage with timeout
active_sessions = {}
SESSION_TIMEOUT = timedelta(minutes=30)  # Sessions expire after 30 minutes

# Initialize model (unchanged)
model = genai.GenerativeModel(
    model_name=config.AI_MODEL,
    system_instruction=config.HINA_SYSTEM_PROMPT
)

def get_chat_session(client_id):
    """Get or create a chat session for the client"""
    now = datetime.now()
    
    # Clean up expired sessions
    for sid in list(active_sessions.keys()):
        if active_sessions[sid]['expires'] < now:
            del active_sessions[sid]
    
    # Create new session if needed
    if client_id not in active_sessions:
        active_sessions[client_id] = {
            'session': model.start_chat(history=[]),
            'expires': now + SESSION_TIMEOUT
        }
    else:
        # Renew expiration time
        active_sessions[client_id]['expires'] = now + SESSION_TIMEOUT
    
    return active_sessions[client_id]['session']

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")
    client_id = request.headers.get('X-Client-ID')  # Frontend sends this
    
    if not client_id:
        return jsonify({"error": "Client ID required"}), 400

    try:
        chat_session = get_chat_session(client_id)
        
        response = chat_session.send_message(
            message,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.9,
                "max_output_tokens": 500
            }
        )

        return jsonify({
            "choices": [{
                "message": {
                    "content": response.text
                }
            }]
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/api/reset", methods=["POST"])
def reset_chat():
    client_id = request.headers.get('X-Client-ID')
    if client_id in active_sessions:
        del active_sessions[client_id]
    return jsonify({"status": "Chat reset"})

@app.route("/api/chat", methods=["GET"])
def hello():
    return f"✅ Hina AI ({config.AI_MODEL}) - Active sessions: {len(active_sessions)}", 200

if __name__ == "__main__":
    app.run(debug=True)