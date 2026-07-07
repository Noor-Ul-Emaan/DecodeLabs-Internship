import requests
import json
import base64
import io
from typing import Optional, Dict, Any, Tuple
from PIL import Image
import openai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import logging

from config import Config
from utils import logger, RetryContext, log_api_call

# Initialize OpenAI client
if Config.OPENAI_API_KEY:
    openai.api_key = Config.OPENAI_API_KEY

class ImageGenerator:
    """Main class for image generation using various APIs."""
    
    def __init__(self):
        self.api_type = None  # Will be set based on available keys
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            openai.APIError,
            openai.RateLimitError
        )),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    @log_api_call
    def generate_with_openai(
        self,
        prompt: str,
        aspect_ratio: str = '1:1',
        quality: str = 'hd',
        style: str = 'vivid',
        n: int = 1
    ) -> Dict[str, Any]:
        """
        Generate image using OpenAI's DALL-E API (or gpt-image).
        
        Args:
            prompt: Text description
            aspect_ratio: '1:1', '16:9', '9:16', etc.
            quality: 'standard' or 'hd'
            style: 'vivid' or 'natural'
            n: Number of images to generate
        
        Returns:
            Dictionary with image data and metadata
        """
        if not Config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
        
        # Get resolution for aspect ratio
        ratio_config = Config.SUPPORTED_ASPECT_RATIOS.get(aspect_ratio)
        if not ratio_config:
            raise ValueError(f"Unsupported aspect ratio: {aspect_ratio}")
        
        size = f"{ratio_config['width']}x{ratio_config['height']}"
        
        try:
            response = openai.images.generate(
                model="dall-e-3",  # or "gpt-image" for enterprise
                prompt=prompt,
                size=size,
                quality=quality,
                style=style,
                n=n
            )
            
            return {
                'success': True,
                'images': [{'url': img.url, 'b64_json': None} for img in response.data],
                'model': 'dall-e-3',
                'prompt': prompt,
                'aspect_ratio': aspect_ratio,
                'size': size
            }
            
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return {'success': False, 'error': str(e), 'type': 'api_error'}
        except openai.RateLimitError as e:
            logger.error(f"Rate limit exceeded: {str(e)}")
            return {'success': False, 'error': 'Rate limit exceeded. Please try again later.', 'type': 'rate_limit'}
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {'success': False, 'error': str(e), 'type': 'unknown'}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError
        )),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    @log_api_call
    def generate_with_stability(
        self,
        prompt: str,
        aspect_ratio: str = '1:1',
        style_preset: str = 'photographic',
        cfg_scale: float = 7.0,
        steps: int = 30,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate image using Stability AI's API.
        
        Args:
            prompt: Text description
            aspect_ratio: '1:1', '16:9', '9:16', etc.
            style_preset: Style preset for generation
            cfg_scale: How strictly to follow the prompt (1-20)
            steps: Number of inference steps
            seed: Random seed for reproducibility
        
        Returns:
            Dictionary with image data and metadata
        """
        if not Config.STABILITY_API_KEY:
            raise ValueError("Stability AI API key not configured")
        
        # Get resolution for aspect ratio
        ratio_config = Config.SUPPORTED_ASPECT_RATIOS.get(aspect_ratio)
        if not ratio_config:
            raise ValueError(f"Unsupported aspect ratio: {aspect_ratio}")
        
        url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
        
        headers = {
            "authorization": f"Bearer {Config.STABILITY_API_KEY}",
            "accept": "application/json"
        }
        
        data = {
            "prompt": prompt,
            "width": ratio_config['width'],
            "height": ratio_config['height'],
            "cfg_scale": cfg_scale,
            "steps": steps,
            "style_preset": style_preset
        }
        
        if seed is not None:
            data["seed"] = seed
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=Config.REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                # Check for base64 image
                if 'image' in result:
                    return {
                        'success': True,
                        'images': [{'b64_json': result['image'], 'url': None}],
                        'model': 'stable-diffusion-3',
                        'prompt': prompt,
                        'aspect_ratio': aspect_ratio,
                        'size': f"{ratio_config['width']}x{ratio_config['height']}",
                        'seed': seed
                    }
                elif 'artifacts' in result:
                    return {
                        'success': True,
                        'images': [{'b64_json': art['base64'], 'url': None} for art in result['artifacts']],
                        'model': 'stable-diffusion-3',
                        'prompt': prompt,
                        'aspect_ratio': aspect_ratio,
                        'size': f"{ratio_config['width']}x{ratio_config['height']}",
                        'seed': seed
                    }
                else:
                    return {'success': False, 'error': 'No image data in response', 'type': 'no_data'}
            else:
                error_msg = response.json().get('message', f"HTTP {response.status_code}")
                return {'success': False, 'error': error_msg, 'type': 'api_error'}
                
        except requests.exceptions.Timeout as e:
            logger.error(f"Stability API timeout: {str(e)}")
            return {'success': False, 'error': 'Request timeout. Server is busy.', 'type': 'timeout'}
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {str(e)}")
            return {'success': False, 'error': 'Connection failed. Please check your network.', 'type': 'connection'}
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {'success': False, 'error': str(e), 'type': 'unknown'}

    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = '1:1',
        api: str = 'openai',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate image using specified API.
        
        Args:
            prompt: Text description
            aspect_ratio: '1:1', '16:9', '9:16', etc.
            api: 'openai' or 'stability'
            **kwargs: Additional API-specific parameters
        
        Returns:
            Dictionary with generation results
        """
        if api == 'openai':
            return self.generate_with_openai(prompt, aspect_ratio, **kwargs)
        elif api == 'stability':
            return self.generate_with_stability(prompt, aspect_ratio, **kwargs)
        else:
            return {'success': False, 'error': f'Unsupported API: {api}', 'type': 'config'}