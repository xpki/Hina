import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

def list_models():
    models = genai.list_models()
    print("Available models:")
    for model in models:
        print(f"- {model.name}: supported generation methods: {model.supported_generation_methods}")

if __name__ == "__main__":
    list_models()
