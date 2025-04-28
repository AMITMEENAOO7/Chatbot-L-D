import os
import logging
from flask import Blueprint, request, jsonify
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
#import ollama
from langchain.prompts import ChatPromptTemplate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
response_bp = Blueprint('response', __name__)

# Constants
CHROMA_PATH = 'chroma'
OLLAMA_MODEL = 'llama2'  # or 'llama3' if you're using LLaMA 3

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser

#MODEL = "llama3.2"
MODEL= "mistral"
model = Ollama(model=MODEL)
parser = StrOutputParser()


def get_relevant_context(query, k=5):
    """Retrieve relevant context from vector database"""
    try:
        print(f"Searching vector database for query: {query}")
        
        # Load the Chroma database
        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
        
        # Perform similarity search
        results = db.similarity_search_with_score(query, k=k)
        
        # Format the results
        context = []
        for doc, score in results:
            context.append({
                "content": doc.page_content,
                "score": float(score),
                "metadata": doc.metadata
            })
            print(f"Found relevant document with score: {score}")
        
        return context
    except Exception as e:
        print(f"Error retrieving context: {str(e)}")
        logger.error(f"Error retrieving context: {str(e)}")
        return []

def create_prompt(query, context):
    """Create a prompt that combines the query with relevant context"""
    prompt = f"""You are a helpful AI assistant. Use the following context to answer the question.
If the context doesn't contain relevant information, say so.

Context:
"""
    
    # Add each context item
    for i, item in enumerate(context, 1):
        prompt += f"\nDocument {i} (Relevance: {item['score']:.2f}):\n{item['content']}\n"
    
    # Add the query
    prompt += f"\nQuestion: {query}\n\nAnswer:"
    
    print(f"Created prompt with {len(context)} context items")
    return prompt

def get_ollama_response(c,q):

    """Get response from local Ollama model"""
    try:
        template = """
        Answer the question based on the context below. If you can't 
        answer the question in detail, reply "I don't know".

        Context: {context}

        Question: {question}
        """

        print('CONNNN',c)

        prompt = ChatPromptTemplate.from_template(template)
        prompt.format(context="Mary's younger sister is Susana", question="Who is Mary's sister?")

        chain = prompt | model | parser
        
        response = chain.invoke({"context": c, "question": q})
        print(response)
        
        print("Received response from Ollama")
        return response
            
    except Exception as e:
        print(f"Error calling Ollama: {str(e)}")
        logger.error(f"Error calling Ollama: {str(e)}")
        return f"Error: {str(e)}"



@response_bp.route("/generate", methods=["POST"])

def handle_query():
    print("\n=== Starting query processing ===")
    try:
        # Get query from request
        data = request.get_json()
        print('data',data)

        query = data.get("prompt", "")
        print(f"Received query: {query}")
        if not data or 'prompt' not in data:
            print("No query provided in request")
            return jsonify({"error": "No query provided"}), 400
        
        
        # Get relevant context from vector database
        context = get_relevant_context(query)
        if not context:
            print("No relevant context found")
            return jsonify({
                "error": "No relevant information found in the database",
                "query": query
            }), 404
        
        # Create prompt with context
        prompt = create_prompt(query, context)
        
        # Get response from Ollama
        response = get_ollama_response(context,query)
        
        # Return the response with context information
        return jsonify({
            "response": response,
            "query": query,
            "context_used": len(context),
            "sources": [item["metadata"] for item in context]
        }), 200
        
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        logger.error(f"Error processing query: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        print("=== Query processing completed ===\n") 