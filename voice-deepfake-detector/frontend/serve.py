"""
Frontend Server - Serves the HTML/CSS/JS files properly
"""

from flask import Flask, send_from_directory, send_file
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='.')
CORS(app)

@app.route('/')
def index():
    """Serve index.html"""
    return send_file('index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('.', path)

if __name__ == '__main__':
    print("\n" + "="*70)
    print("  Frontend Server Starting...")
    print("  Access at: http://localhost:3000")
    print("="*70 + "\n")
    app.run(host='0.0.0.0', port=3000, debug=False)
