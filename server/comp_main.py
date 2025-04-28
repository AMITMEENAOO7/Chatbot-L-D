from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from frontend

# Initialize embeddings and load the Chroma database
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
CHROMA_PATH = "chroma"

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    query = data.get("prompt", "")
    print("Query received:", query)

    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        # Load the Chroma database
        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
        
        # Perform similarity search
        results = db.similarity_search_with_score(query, k=3)
        
        # Format the results
        response = []
        for doc, score in results:
            response.append({
                "content": doc.page_content,
                "score": float(score),
                "metadata": doc.metadata
            })
            
        print("Response:", response)
        return jsonify({"response": response})
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)

