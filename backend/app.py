from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import config

# Setup
genai.configure(api_key=config.GEMINI_API_KEY)
app = Flask(__name__)
CORS(app)

# Initialize chat session
chat_session = None

# Hina's system prompt
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

# Initialize model
model = genai.GenerativeModel(
    model_name=config.AI_MODEL,
    system_instruction=HINA_SYSTEM_PROMPT
)

def init_chat():
    global chat_session
    chat_session = model.start_chat(history=[])

@app.route("/api/chat", methods=["POST"])
def chat():
    global chat_session
    data = request.get_json()
    message = data.get("message", "")

    # Initialize chat if not exists
    if chat_session is None:
        init_chat()

    try:
        # Send message with context
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
        return jsonify({
            "error": {"message": str(e)}
        }), 500

@app.route("/api/reset", methods=["POST"])
def reset_chat():
    init_chat()
    return jsonify({"status": "Chat reset"})

@app.route("/api/chat", methods=["GET"])
def hello():
    return "✅ Flask API is running (" + config.AI_MODEL + "). Use POST to send messages.", 200

if __name__ == "__main__":
    init_chat()
    app.run(debug=True)