from langchain_community.embeddings import HuggingFaceEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def main():
    # Get embedding for words using sentence-transformers
    embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Get embeddings for both words
    word1 = "apple"
    word2 = "iphone"
    vector1 = embedding_function.embed_query(word1)
    vector2 = embedding_function.embed_query(word2)
    
    # Convert to numpy arrays and reshape for cosine similarity
    vector1 = np.array(vector1).reshape(1, -1)
    vector2 = np.array(vector2).reshape(1, -1)
    
    # Calculate cosine similarity
    similarity = cosine_similarity(vector1, vector2)[0][0]
    
    print(f"Vector for '{word1}': {vector1.flatten()[:5]}...")  # Print first 5 values
    print(f"Vector length: {len(vector1.flatten())}")
    print(f"Comparing ({word1}, {word2}): {similarity:.4f}")


if __name__ == "__main__":
    main()