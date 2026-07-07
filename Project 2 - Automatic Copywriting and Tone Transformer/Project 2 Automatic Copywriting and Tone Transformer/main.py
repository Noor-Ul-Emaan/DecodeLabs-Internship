import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
from utils.transformer import ToneTransformer  # ✅ Fixed: Tome → Tone

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please create .env file with your API key")

# ✅ Fixed: These lines were inside the if block, now outside
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize tone transformer
transformer = ToneTransformer()

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_copy():
    """Generate copywriting content with tone transformation"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        tone = data.get('tone', 'professional')
        
        if not prompt:
            return jsonify({
                'success': False,
                'error': 'Please provide a prompt'
            }), 400
        
        # Generate content using Gemini
        full_prompt = f"Write copywriting content in a {tone} tone. Topic: {prompt}"
        response = model.generate_content(full_prompt)
        
        # Apply additional tone transformation
        transformed_text = transformer.transform_tone(response.text, tone)
        
        return jsonify({
            'success': True,
            'content': transformed_text,
            'tone': tone,
            'original': response.text
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/transform', methods=['POST'])
def transform_text():
    """Transform existing text to different tone"""
    try:
        data = request.json
        text = data.get('text', '')
        target_tone = data.get('tone', 'professional')
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'Please provide text to transform'
            }), 400
        
        # Transform text using Gemini
        prompt = f"Transform the following text to a {target_tone} tone:\n\n{text}"
        response = model.generate_content(prompt)
        
        return jsonify({
            'success': True,
            'transformed_text': response.text,
            'tone': target_tone
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)