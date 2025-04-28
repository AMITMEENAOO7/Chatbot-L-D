from flask import Flask, request, jsonify
from huggingface_hub import login
import transformers
import torch
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from frontend

from langchain.document_loaders import DirectoryLoader
DATA_PATH = "books"
def load_documents():
  loader = DirectoryLoader (DATA_PATH, glob="*.md")
  documents = loader.load()
  return documents

# Login to Hugging Face
print(torch.cuda.is_available())

hf_token = os.getenv("HF_TOKEN", "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")
login(hf_token)

# Load LLaMA model pipeline
#model_id = "meta-llama/Llama-3.1-8B"
#model_id = "TheBloke/Llama-3-8B-Instruct-GGUF"
model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

pipeline = transformers.pipeline(
    "text-generation", model=model_id, model_kwargs={"torch_dtype": torch.bfloat16,}, device_map="auto"
)


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    prompt = data.get("prompt", "")
    print(prompt)

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    result = pipeline(prompt, max_new_tokens=100, do_sample=True, temperature=0.7)[0]["generated_text"]
    print('result : ',result)
    return jsonify({"response": result})

if __name__ == "__main__":
    app.run(port=5000)

