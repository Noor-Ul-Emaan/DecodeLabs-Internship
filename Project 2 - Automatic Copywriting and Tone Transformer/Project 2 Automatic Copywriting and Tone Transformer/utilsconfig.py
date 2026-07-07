import os

class Config:
    """Configuration settings for the application"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = True
    
    # Gemini API settings
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = 'gemini-1.5-flash'
    
    # Application settings
    AVAILABLE_TONES = [
        'professional',
        'casual', 
        'persuasive',
        'informative',
        'emotional',
        'humorous'
    ]
    
    MAX_PROMPT_LENGTH = 500
    MAX_TEXT_LENGTH = 2000
    
    @classmethod
    def validate_config(cls):
        """Validate that all required settings are present"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required. Set it in .env file")
        return True