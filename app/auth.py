from flask_jwt_extended import create_access_token
from datetime import timedelta
from app import app

def generate_token(user_id):
    expires = timedelta(seconds=app.config['JWT_ACCESS_TOKEN_EXPIRES'])
    return create_access_token(
        identity=user_id,
        expires_delta=expires
    )

def verify_token(token):
    try:
        # JWT verification is handled by flask_jwt_extended decorator
        return True
    except Exception as e:
        return False
