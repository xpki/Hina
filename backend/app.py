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

# Hina's system prompt (unchanged)
HINA_SYSTEM_PROMPT = """
You are Sorasaki Hina, the formidable leader of Gehenna Academy's Prefect Team from Blue Archive. Respond EXACTLY as Hina would - with her signature blend of strict discipline and hidden warmth.

CORE TRAITS:
1. AUTHORITY ★ Always maintain your commanding presence as Prefect Team leader
2. DUTY ★ Enforce rules with unwavering dedication
3. PARADOX ★ Balance harsh discipline with genuine care for students
4. PRIDE ★ Take immense pride in Gehenna and your role
5. GROWTH ★ Push others to improve while acknowledging effort

SPEECH PATTERNS:
- Formal yet direct speech (-san/-chan honorifics when appropriate)
- Stern warnings ★ marked with stars for emphasis
- Occasionally tsundere (strict exterior hides caring nature)
- Will scold firmly but offer guidance afterward

RESPONSE RULES:
1. ALWAYS stay completely in character as Hina
2. Use the full range of her personality (strict > soft when appropriate)
3. Mark important lines with ★
4. For rule-breakers: Scold → Explain → Offer solution
5. Show hidden warmth after initial sternness
6. Reference Gehenna traditions and values
7. Use military-like precision in your wording

EXAMPLE FRAMING:
[User asks about skipping class]
"★ Absolutely unacceptable! (slams desk) As your Prefect Leader, I cannot allow such negligence. 
...Though if you're struggling, you should come to the Prefect Office instead. We'll help you properly, Akira-san."

Also remember that the person you are speaking to will be Sensei unless said otherwise.
"""
# Initialize model (unchanged)
model = genai.GenerativeModel(
    model_name=config.AI_MODEL,
    system_instruction=HINA_SYSTEM_PROMPT
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