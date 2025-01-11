import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt_secret')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    RATELIMIT_DEFAULT = "100 per day"
    GPU_SLOT_DURATION = 24 * 60 * 60  # 24 hours in seconds
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False