from functools import wraps
from flask import request, jsonify
import time
from app import logger

def log_request():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            response = f(*args, **kwargs)
            duration = time.time() - start_time
            
            logger.info(
                f"Request: {request.method} {request.path} "
                f"Duration: {duration:.2f}s "
                f"Status: {response.status_code}"
            )
            return response
        return decorated_function
    return decorator
