from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
from datetime import datetime

from config import Config
from image_generator import ImageGenerator
from image_processor import ImageProcessor
from utils import logger, log_api_call

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

CORS(app)

# Initialize components
generator = ImageGenerator()
processor = ImageProcessor()

# Create necessary directories
os.makedirs(Config.DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)

@app.route('/')
def index():
    """Render the main application page."""
    return render_template('index.html', 
                          aspect_ratios=Config.SUPPORTED_ASPECT_RATIOS)

@app.route('/api/generate', methods=['POST'])
@log_api_call
def generate_image():
    """
    API endpoint for image generation.
    
    Expected JSON payload:
    {
        "prompt": "A cat wearing a hat",
        "aspect_ratio": "1:1",
        "api": "openai",
        "style_preset": "photographic",
        "quality": "hd",
        "n": 1
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        prompt = data.get('prompt', '').strip()
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        aspect_ratio = data.get('aspect_ratio', '1:1')
        if aspect_ratio not in Config.SUPPORTED_ASPECT_RATIOS:
            return jsonify({'error': f'Unsupported aspect ratio: {aspect_ratio}'}), 400
        
        api = data.get('api', 'openai')
        style_preset = data.get('style_preset', 'photographic')
        quality = data.get('quality', 'hd')
        n = min(data.get('n', 1), 4)  # Limit to 4 images
        
        # Prepare generation parameters
        params = {
            'aspect_ratio': aspect_ratio,
            'style_preset': style_preset,
            'quality': quality,
            'n': n
        }
        
        # Generate image
        result = generator.generate_image(
            prompt=prompt,
            api=api,
            **params
        )
        
        if not result.get('success'):
            return jsonify({
                'success': False,
                'error': result.get('error', 'Generation failed'),
                'type': result.get('type', 'unknown')
            }), 500
        
        # Process and save images
        processed_result = processor.process_generation_result(
            result,
            save_to_disk=True
        )
        
        return jsonify(processed_result)
        
    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@app.route('/api/validate', methods=['POST'])
def validate_image():
    """
    Validate an image from URL or base64.
    """
    try:
        data = request.get_json()
        image_data = data.get('image_data', '')
        image_type = data.get('type', 'url')  # 'url' or 'base64'
        
        if image_type == 'url':
            image_bytes = processor.download_image_from_url(image_data)
        else:
            image_bytes = processor.decode_base64_image(image_data)
        
        if not image_bytes:
            return jsonify({'valid': False, 'error': 'Failed to retrieve image'}), 400
        
        is_valid, error_msg = processor.validate_image_integrity(image_bytes)
        
        return jsonify({
            'valid': is_valid,
            'message': error_msg,
            'size': len(image_bytes)
        })
        
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)}), 500

@app.route('/api/cleanup', methods=['POST'])
def cleanup_images():
    """Clean old generated images."""
    try:
        days = request.get_json().get('days', 7)
        removed = processor.clean_old_images(days)
        return jsonify({'removed': removed, 'message': f'Removed {removed} old images'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/downloads/<path:filename>')
def download_file(filename):
    """Serve downloaded images."""
    return send_from_directory(Config.DOWNLOAD_FOLDER, filename)

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get generation history."""
    try:
        history_file = 'generation_history.json'
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
            return jsonify({'history': history[-20:]})  # Last 20 entries
        return jsonify({'history': []})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Log startup information
    logger.info("=" * 60)
    logger.info("Multimodal Image Generation Studio")
    logger.info(f"Running on http://localhost:5000")
    logger.info(f"Download folder: {Config.DOWNLOAD_FOLDER}")
    logger.info(f"Supported APIs: OpenAI, Stability AI")
    logger.info("=" * 60)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=Config.DEBUG
    )