from flask import Flask
from upload import upload_bp  
from flask_cors import CORS
from response import response_bp

app = Flask(__name__)
CORS(app)

app.secret_key = 'your_secret_key'  # Replace with your actual secret key


app.register_blueprint(upload_bp)
app.register_blueprint(response_bp)

# Your other routes and app setup
if __name__ == "__main__":
    app.run(debug=False, port=5000)
