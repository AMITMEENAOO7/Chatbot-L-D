from flask import Flask, request, jsonify
from openai import OpenAI
import json
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from frontend

# Set your OpenAI API key
client = OpenAI(api_key="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")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    prompt = data.get("prompt", "")
    print("Prompt received:", prompt)

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    try:

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=20
        )
        message = response.choices[0].message["content"].strip()
        print("Response:", message)
        return jsonify({"response": message})
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)


