from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import config

# Setup
genai.configure(api_key=config.GEMINI_API_KEY)
app = Flask(__name__)
CORS(app)

# Load model
model = genai.GenerativeModel(
    model_name = config.AI_MODEL
)

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")

    

    try:
        response = model.generate_content(message)
        content = response.text.strip()

        return jsonify({
            "choices": [{
                "message": {
                    "content": content
                }
            }]
        })

    except Exception as e:
        print("Gemini API error:", e)
        return jsonify({
            "error": {
                "message": str(e)
            }
        }), 500
@app.route("/api/chat", methods=["GET"])
def hello():
    return "✅ Flask API is running (" + config.AI_MODEL + "). Use POST to send messages.", 200

if __name__ == "__main__":
    app.run(debug=True)
