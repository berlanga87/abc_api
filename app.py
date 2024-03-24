from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from openai import OpenAI
import os

# Initialize Flask app
app = Flask(__name__)

openai = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Initialize Limiter for rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["5 per minute"]  # Example limit, adjust as needed
)

# Example in-memory API keys
VALID_API_KEYS = {"your_api_key_1": True}

# OpenAI API key setup

# Middleware for API key validation
@app.before_request
def before_request_func():
    api_key = request.headers.get('Authorization')
    if not api_key or api_key not in VALID_API_KEYS:
        return jsonify({"error": "Unauthorized"}), 401

@app.route('/generate-text', methods=['POST'])
@limiter.limit("5 per minute")
def generate_text():
    data = request.json
    if 'text' not in data:
        return jsonify({"error": "Missing text query"}), 400

    # Prompt transformation
    instruction = "Please generate a sample support article for ABCorp (a financial services firm) that answers the following query from a Support agent: "
    transformed_text = f"{instruction} {data['text']}"

    try:
        response = openai.chat.completions.create(
          model="gpt-3.5-turbo",  # Use the desired model
          messages=[
              {"role": "system", "content": "You are a helpful assistant."},
              {"role": "user", "content": transformed_text},
          ]
        )
        print(response.choices[0].message.content)

        generated_text = response.choices[0].message.content
        
        return jsonify({"response": generated_text}), 200
    except Exception as e:
        return jsonify({"error": "Failed to generate text", "details": str(e)}), 502


if __name__ == '__main__':
    app.run()
