import os
import fitz  # PyMuPDF
import docx2txt  # Improved DOCX extraction
from flask import Blueprint, request, jsonify
import logging
import re
from werkzeug.utils import secure_filename
from datetime import datetime
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
upload_bp = Blueprint('upload', __name__)

# Directory to store extracted text files and vector database
UPLOAD_FOLDER = 'uploads'
CHROMA_PATH = 'chroma'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CHROMA_PATH, exist_ok=True)

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['pdf', 'docx']

def extract_text_from_file(file):
    """Extract text content from different file types"""
    ext = file.filename.rsplit('.', 1)[1].lower()
    print(f"Extracting text from file: {file.filename} (type: {ext})")

    if ext == 'pdf':
        try:
            text = extract_text_from_pdf(file)
            print(f"Successfully extracted {len(text)} characters from PDF")
        except Exception as e:
            print(f"Error extracting text from PDF: {str(e)}")
            logger.exception("Error extracting text from PDF:")
            text = ""
    elif ext == 'docx':
        try:
            text = extract_text_from_docx(file)
            print(f"Successfully extracted {len(text)} characters from DOCX")
        except Exception as e:
            print(f"Error extracting text from DOCX: {str(e)}")
            logger.exception("Error reading DOCX file:")
            text = ""
    else:
        text = ""
    
    return text

def extract_text_from_pdf(file):
    """Extract text from PDF file"""
    text = ""
    try:
        with fitz.open(stream=file.read(), filetype="pdf") as pdf_document:
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                page_text = page.get_text()
                text += page_text
                print(f"Extracted {len(page_text)} characters from page {page_num + 1}")
    except Exception as e:
        print(f"Error reading PDF file: {str(e)}")
        logger.exception("Error reading PDF file:")
        text = ""
    
    return text

def extract_text_from_docx(file):
    """Extract text from DOCX file"""
    try:
        text = docx2txt.process(file)
    except Exception as e:
        print(f"Error reading DOCX file: {str(e)}")
        logger.exception("Error reading DOCX file:")
        text = ""
    return text

def save_to_vector_db(text, filename, file_type):
    """Save text to vector database"""
    print(f"Saving text to vector database: {filename} (type: {file_type})")
    try:
        # Create a document with metadata
        doc = Document(
            page_content=text,
            metadata={
                "source": filename,
                "file_type": file_type,
                "upload_date": datetime.now().isoformat()
            }
        )
        print(f"Created document with {len(text)} characters")
        
        # Split the text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=100,
            length_function=len,
            add_start_index=True,
        )
        chunks = text_splitter.split_documents([doc])
        print(f"Split text into {len(chunks)} chunks")
        
        # Load existing database or create new one
        if os.path.exists(CHROMA_PATH):
            print("Loading existing Chroma database")
            db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
            db.add_documents(chunks)
            print("Added documents to existing database")
        else:
            print("Creating new Chroma database")
            db = Chroma.from_documents(chunks, embeddings, persist_directory=CHROMA_PATH)
            print("Created new database with documents")
        
        db.persist()
        print("Persisted database changes")
        return True, f"Successfully processed {filename}"
        
    except Exception as e:
        print(f"Error saving to vector database: {str(e)}")
        logger.error(f"Error saving to vector database: {str(e)}")
        return False, f"Error saving to vector database: {str(e)}"

@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    print("\n=== Starting file upload process ===")
    try:
        # Check if file is in the request
        if 'file' not in request.files:
            print("No file part in the request")
            logger.error("No file part in the request")
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files['file']
        print(f"Received file: {file.filename}")
        
        # Validate file
        if file.filename == '':
            print("No file selected")
            logger.error("No file selected")
            return jsonify({"error": "No file selected"}), 400

        if not allowed_file(file.filename):
            print(f"Invalid file type: {file.filename}")
            logger.error("Invalid file type")
            return jsonify({"error": "Invalid file type"}), 400

        # Process file
        try:
            # Extract text from file
            print("Starting text extraction")
            extracted_text = extract_text_from_file(file)
            print(f"Text extraction completed: {len(extracted_text)} characters")

            if not extracted_text:
                print("No text could be extracted from the file")
                return jsonify({"error": "No text could be extracted from the file"}), 400

            # Create filename for the extracted text
            base_filename = os.path.splitext(file.filename)[0]
            text_filename = f"{base_filename}_extracted.txt"
            text_path = os.path.join(UPLOAD_FOLDER, text_filename)
            print(f"Created text filename: {text_filename}")

            # Save the extracted text to file
            with open(text_path, 'a', encoding='utf-8') as f:
                f.write(extracted_text + '\n')
            print(f"Saved extracted text to {text_path}")

            # Save to vector database
            file_type = file.filename.rsplit('.', 1)[1].lower()
            print("Starting vector database save")
            success, message = save_to_vector_db(extracted_text, file.filename, file_type)

            if success:
                print("File processing completed successfully")
                return jsonify({
                    "message": "File processed successfully",
                    "filename": text_filename,
                    "file_type": file_type,
                    "text_length": len(extracted_text)
                }), 200
            else:
                print(f"Error processing file: {message}")
                return jsonify({
                    "error": "Error processing file",
                    "details": message
                }), 500

        except Exception as e:
            print(f"Error processing file: {str(e)}")
            logger.error(f"Error processing file: {str(e)}")
            return jsonify({"error": str(e)}), 500

    except Exception as e:
        print(f"Error in upload_file: {str(e)}")
        logger.error(f"Error in upload_file: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        print("=== File upload process completed ===\n")

