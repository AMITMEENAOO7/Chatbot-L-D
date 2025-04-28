from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever  # make sure you have this module ready

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from frontend

# Load Ollama model
model = OllamaLLM(model="llama3.2")  # or "llama3" depending on your local Ollama model
template = """
You are an expert in answering questions about a pizza restaurant.

Here are some relevant reviews: {reviews}

Here is the question to answer: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    question = data.get("prompt", "")

    if not question:
        return jsonify({"error": "No prompt provided"}), 400

    try:
        reviews = retriever.invoke(question)
        result = chain.invoke({"reviews": reviews, "question": question})
        return jsonify({"response": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)
