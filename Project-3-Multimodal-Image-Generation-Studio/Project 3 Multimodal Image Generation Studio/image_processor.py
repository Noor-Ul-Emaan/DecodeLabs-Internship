import os
import io
import base64
import hashlib
from typing import Optional, Tuple, Dict, Any
from PIL import Image
import requests
import magic

from config import Config
from utils import logger, validate_image_size, get_file_extension, safe_filename

class ImageProcessor:
    """Handles image processing, validation, and storage."""
    
    def __init__(self):
        self.download_folder = Config.DOWNLOAD_FOLDER
        os.makedirs(self.download_folder, exist_ok=True)
    
    def download_image_from_url(
        self,
        url: str,
        timeout: Tuple[float, float] = Config.REQUEST_TIMEOUT
    ) -> Optional[bytes]:
        """
        Download image from URL with streaming and timeout.
        
        Args:
            url: Image URL
            timeout: (connection_timeout, read_timeout)
        
        Returns:
            Image bytes or None if failed
        """
        try:
            # Use streaming to handle large images efficiently
            response = requests.get(
                url,
                stream=True,
                timeout=timeout,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                logger.error(f"Not an image: {content_type}")
                return None
            
            # Stream download with chunking
            image_data = b''
            chunk_size = 65536  # 64KB chunks
            
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    image_data += chunk
                    # Validate size during download
                    if len(image_data) > Config.MAX_IMAGE_SIZE:
                        logger.error("Image size exceeds maximum limit")
                        return None
            
            return image_data
            
        except requests.exceptions.Timeout as e:
            logger.error(f"Download timeout: {str(e)}")
            return None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Download error: {str(e)}")
            return None
    
    def decode_base64_image(self, b64_string: str) -> Optional[bytes]:
        """
        Decode base64 image data.
        
        Args:
            b64_string: Base64 encoded image data
        
        Returns:
            Image bytes or None if failed
        """
        try:
            # Handle possible data URL prefix
            if b64_string.startswith('data:image'):
                b64_string = b64_string.split(',')[1]
            
            image_data = base64.b64decode(b64_string)
            return image_data
        except Exception as e:
            logger.error(f"Base64 decode error: {str(e)}")
            return None
    
    def validate_image_integrity(self, image_data: bytes) -> Tuple[bool, str]:
        """
        Thoroughly validate image integrity by attempting full decode.
        
        Args:
            image_data: Image bytes
        
        Returns:
            (is_valid, error_message)
        """
        try:
            # First try to open and verify
            with Image.open(io.BytesIO(image_data)) as img:
                # Force full decode by loading pixel data
                img.load()
                # Additional checks
                if img.width <= 0 or img.height <= 0:
                    return False, "Invalid image dimensions"
                if img.width > 4096 or img.height > 4096:
                    return False, "Image dimensions exceed maximum"
                
            return True, "Valid image"
        except Image.UnidentifiedImageError:
            return False, "Unidentified or corrupted image format"
        except OSError as e:
            if "broken data stream" in str(e):
                return False, "Truncated or corrupted image data"
            return False, f"Image processing error: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def save_image(
        self,
        image_data: bytes,
        prefix: str = 'generated'
    ) -> Optional[str]:
        """
        Save image to disk with validation.
        
        Args:
            image_data: Image bytes
            prefix: Prefix for filename
        
        Returns:
            Saved file path or None if failed
        """
        # Validate size
        if not validate_image_size(image_data, Config.MAX_IMAGE_SIZE):
            logger.error("Image size exceeds maximum")
            return None
        
        # Validate integrity
        is_valid, error_msg = self.validate_image_integrity(image_data)
        if not is_valid:
            logger.error(f"Image validation failed: {error_msg}")
            return None
        
        try:
            # Determine format and extension
            with Image.open(io.BytesIO(image_data)) as img:
                format_name = img.format.lower() if img.format else 'png'
                if format_name == 'jpeg':
                    ext = '.jpg'
                else:
                    ext = f'.{format_name}'
            
            # Generate filename
            file_hash = hashlib.md5(image_data).hexdigest()[:8]
            filename = f"{prefix}_{file_hash}{ext}"
            filepath = os.path.join(self.download_folder, filename)
            
            # Save
            with open(filepath, 'wb') as f:
                f.write(image_data)
            
            logger.info(f"Image saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Save error: {str(e)}")
            return None
    
    def process_generation_result(
        self,
        result: Dict[str, Any],
        save_to_disk: bool = True
    ) -> Dict[str, Any]:
        """
        Process generation result, download/save images.
        
        Args:
            result: Generation result from ImageGenerator
            save_to_disk: Whether to save images to disk
        
        Returns:
            Processed result with local paths
        """
        if not result.get('success'):
            return result
        
        processed_images = []
        images = result.get('images', [])
        
        for img_data in images:
            image_bytes = None
            
            # Try base64 first
            if img_data.get('b64_json'):
                image_bytes = self.decode_base64_image(img_data['b64_json'])
            
            # Try URL if no base64
            if not image_bytes and img_data.get('url'):
                image_bytes = self.download_image_from_url(img_data['url'])
            
            if not image_bytes:
                processed_images.append({
                    'error': 'Failed to retrieve image data',
                    'url': img_data.get('url'),
                    'saved_path': None
                })
                continue
            
            # Save image
            if save_to_disk:
                saved_path = self.save_image(image_bytes)
            else:
                saved_path = None
            
            # Convert to base64 for display
            b64_encoded = base64.b64encode(image_bytes).decode('utf-8')
            
            processed_images.append({
                'data': b64_encoded,
                'url': img_data.get('url'),
                'saved_path': saved_path,
                'size': len(image_bytes)
            })
        
        result['processed_images'] = processed_images
        return result
    
    def clean_old_images(self, max_age_days: int = 7) -> int:
        """
        Remove images older than specified days.
        
        Args:
            max_age_days: Maximum age in days
        
        Returns:
            Number of files removed
        """
        import time
        now = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        removed_count = 0
        
        for filename in os.listdir(self.download_folder):
            filepath = os.path.join(self.download_folder, filename)
            if os.path.isfile(filepath):
                file_age = now - os.path.getmtime(filepath)
                if file_age > max_age_seconds:
                    try:
                        os.remove(filepath)
                        removed_count += 1
                    except Exception as e:
                        logger.error(f"Failed to remove {filepath}: {str(e)}")
        
        return removed_count