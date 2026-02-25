from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# List available models
try:
    models = client.models.list()
    print("Available models:")
    for model in models:
        print(f"  - {model.name}")
        if hasattr(model, 'supported_generation_methods'):
            print(f"    Supported methods: {model.supported_generation_methods}")
except Exception as e:
    print(f"Error listing models: {e}")

# Try a simple generation
try:
    print("\nTrying simple generation with gemini-2.5-flash...")
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents='Say hello'
    )
    print(f"Success! Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
