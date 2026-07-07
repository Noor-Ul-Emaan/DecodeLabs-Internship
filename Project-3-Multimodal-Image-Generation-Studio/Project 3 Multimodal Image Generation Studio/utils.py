import os
import time
import random
import logging
from datetime import datetime
from functools import wraps
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def safe_filename(filename: str) -> str:
    """Generate a safe filename with timestamp."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    name, ext = os.path.splitext(filename)
    return f"{name}_{timestamp}{ext}"

def exponential_backoff_with_jitter(
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    multiplier: float = 2.0,
    jitter: float = 0.1
) -> float:
    """
    Calculate exponential backoff delay with jitter.
    
    Args:
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        multiplier: Multiplier for each retry
        jitter: Random jitter factor (0-1)
    
    Returns:
        float: Delay in seconds
    """
    def decorator(retry_count: int) -> float:
        delay = min(base_delay * (multiplier ** retry_count), max_delay)
        # Add jitter to prevent thundering herd
        jitter_amount = delay * jitter * random.random()
        return delay + jitter_amount
    
    return decorator

class RetryContext:
    """Context manager for retry logic with exponential backoff."""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        retryable_exceptions: tuple = (Exception,)
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.retryable_exceptions = retryable_exceptions
        self.retry_count = 0
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and issubclass(exc_type, self.retryable_exceptions):
            if self.retry_count < self.max_retries:
                delay = exponential_backoff_with_jitter(
                    self.base_delay, self.max_delay
                )(self.retry_count)
                logger.warning(
                    f"Retry {self.retry_count + 1}/{self.max_retries} "
                    f"after {delay:.2f}s due to {exc_type.__name__}"
                )
                time.sleep(delay)
                self.retry_count += 1
                return True  # Retry
        return False  # Don't retry

def log_api_call(func):
    """Decorator to log API calls."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(f"Calling {func.__name__}")
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(f"{func.__name__} completed in {elapsed:.2f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"{func.__name__} failed after {elapsed:.2f}s: {str(e)}")
            raise
    return wrapper

def validate_image_size(image_data: bytes, max_size: int) -> bool:
    """Validate image size doesn't exceed maximum."""
    return len(image_data) <= max_size

def get_file_extension(content_type: str) -> str:
    """Get file extension from content type."""
    extension_map = {
        'image/png': '.png',
        'image/jpeg': '.jpg',
        'image/webp': '.webp',
        'image/bmp': '.bmp',
        'image/gif': '.gif'
    }
    return extension_map.get(content_type, '.png')