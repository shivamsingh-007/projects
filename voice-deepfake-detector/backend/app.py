"""
Voice Deepfake Detection Backend API
Flask-based RESTful API for audio authenticity analysis
"""

# Disable numba to avoid NumPy version conflicts
import os
os.environ['NUMBA_DISABLE_JIT'] = '1'

# Suppress NumPy warnings on Windows
import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)
warnings.filterwarnings('ignore', message='.*MINGW-W64.*')

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import numpy as np
from werkzeug.utils import secure_filename
import librosa
import logging
from model import DeepfakeDetector
from preprocessing import AudioPreprocessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'ogg', 'flac'}

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize model and preprocessor
model = DeepfakeDetector()
preprocessor = AudioPreprocessor()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model.is_loaded(),
        'version': '1.0.0'
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_audio():
    """
    Main endpoint for audio deepfake detection
    Accepts audio file and returns authenticity prediction
    """
    try:
        # Validate file presence
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        file = request.files['audio']
        
        # Validate filename
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file extension
        if not allowed_file(file.filename):
            return jsonify({
                'error': f'Invalid file format. Allowed formats: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        logger.info(f"Processing file: {filename}")
        
        # Load and validate audio
        try:
            audio_data, sample_rate = librosa.load(filepath, sr=None)
            duration = librosa.get_duration(y=audio_data, sr=sample_rate)
            
            # Validate audio duration (0.5-300 seconds)
            if duration < 0.5:
                os.remove(filepath)
                return jsonify({
                    'error': 'Audio too short. Minimum duration: 0.5 seconds'
                }), 400
            
            if duration > 300:
                os.remove(filepath)
                return jsonify({
                    'error': 'Audio too long. Maximum duration: 300 seconds (5 minutes)'
                }), 400
            
        except Exception as e:
            os.remove(filepath)
            return jsonify({'error': f'Invalid audio file: {str(e)}'}), 400
        
        # Preprocess audio
        logger.info("Extracting audio features...")
        features = preprocessor.extract_features(filepath)
        
        # Run prediction
        logger.info("Running deepfake detection model...")
        prediction = model.predict(features)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        # Prepare response
        is_real = prediction['label'] == 'REAL'
        confidence = prediction['confidence']
        
        response = {
            'verdict': prediction['label'],
            'is_real': is_real,
            'confidence': round(confidence, 2),
            'authenticity_score': round(confidence if is_real else (100 - confidence), 2),
            'details': {
                'duration': round(duration, 2),
                'sample_rate': sample_rate,
                'model_version': '1.0.0',
                'analysis_complete': True
            },
            'message': f"Audio classified as {'AUTHENTIC' if is_real else 'SYNTHETIC'} with {confidence:.1f}% confidence"
        }
        
        logger.info(f"Analysis complete: {prediction['label']} ({confidence:.1f}%)")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        return jsonify({
            'error': 'Internal server error during analysis',
            'details': str(e)
        }), 500

@app.route('/api/formats', methods=['GET'])
def get_formats():
    """Return supported audio formats"""
    return jsonify({
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'max_file_size_mb': 50,
        'optimal_duration': '1-60 seconds',
        'max_duration': '300 seconds (5 minutes)'
    })

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({
        'error': 'File too large. Maximum size: 50MB'
    }), 413

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    logger.error(f"Internal error: {str(error)}")
    return jsonify({
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    logger.info("Starting Voice Deepfake Detection API...")
    logger.info(f"Model loaded: {model.is_loaded()}")
    app.run(host='0.0.0.0', port=5000, debug=True)
