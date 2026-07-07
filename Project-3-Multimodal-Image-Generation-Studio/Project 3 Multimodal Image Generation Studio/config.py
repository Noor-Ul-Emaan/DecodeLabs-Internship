import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    STABILITY_API_KEY = os.getenv('STABILITY_API_KEY')
    
    # Flask Settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Image Settings
    MAX_IMAGE_SIZE = int(os.getenv('MAX_IMAGE_SIZE', 10485760))
    DOWNLOAD_FOLDER = 'downloads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    
    # API Settings
    REQUEST_TIMEOUT = (3.05, 60)  # (connection, read)
    MAX_RETRIES = 3
    
    # Generation Settings
    SUPPORTED_ASPECT_RATIOS = {
        '16:9': {'width': 1344, 'height': 768, 'description': 'Landscape'},
        '1:1': {'width': 1024, 'height': 1024, 'description': 'Square'},
        '9:16': {'width': 768, 'height': 1344, 'description': 'Vertical'},
        '3:2': {'width': 1344, 'height': 896, 'description': 'Classic'},
        '2:3': {'width': 896, 'height': 1344, 'description': 'Portrait'},
        '21:9': {'width': 1792, 'height': 768, 'description': 'Ultrawide'}
    }
    
    # Aesthetic Quality Threshold
    AESTHETIC_THRESHOLD = 7.0  # out of 10