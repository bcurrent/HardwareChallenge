import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy.orm import declarative_base

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app first
app = Flask(__name__)

# Initialize database
Base = declarative_base()
db = SQLAlchemy(model_class=Base)

# Configure database from environment variables
database_url = os.getenv('DATABASE_URL')
if not database_url:
    logger.error("DATABASE_URL environment variable not set")
    raise ValueError("DATABASE_URL environment variable is required")

# Configure Flask app
app.config.update(
    SQLALCHEMY_DATABASE_URI=database_url,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_ENGINE_OPTIONS={
        "pool_size": 5,
        "max_overflow": 2,
        "pool_timeout": 30,
        "pool_recycle": 1800,
        "pool_pre_ping": True,
    },
    SECRET_KEY=os.getenv('FLASK_SECRET_KEY', 'development-key-change-in-production'),
)

# Initialize extensions
try:
    db.init_app(app)
    logger.info("Successfully initialized database")
except Exception as e:
    logger.error(f"Failed to initialize database: {str(e)}")
    raise

# Setup rate limiter with increased storage timeout
try:
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        storage_uri="memory://",
        default_limits=["200 per day"],
        storage_options={"storage_timeout": 3600},  # 1 hour timeout for storage
        strategy="fixed-window-elastic-expiry"  # More accurate rate limiting
    )
    logger.info("Successfully initialized rate limiter")
except Exception as e:
    logger.error(f"Failed to initialize rate limiter: {str(e)}")
    raise

# Import models and create tables
try:
    with app.app_context():
        # Import models here to avoid circular imports
        from app.models import User, Submission  # noqa: F401
        db.create_all()
        logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {str(e)}")
    raise

# Import routes after app initialization to avoid circular imports
from app.routes import *  # noqa: F401, E402

logger.info("Flask application initialized successfully")