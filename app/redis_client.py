import os
import redis
from app import logger
import time
from redis.connection import ConnectionPool

# Configure Redis connection pool
def create_redis_pool():
    """Create a Redis connection pool with retry logic"""
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = int(os.getenv('REDIS_PORT', 6379))

    return ConnectionPool(
        host=redis_host,
        port=redis_port,
        db=0,
        decode_responses=True,
        max_connections=10,
        socket_timeout=5,
        socket_connect_timeout=5,
        retry_on_timeout=True
    )

def get_redis_client():
    """Get Redis client with connection retry logic"""
    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            # Use connection pool for better resource management
            client = redis.Redis(
                connection_pool=create_redis_pool(),
                health_check_interval=30
            )
            # Test connection
            client.ping()
            return client
        except redis.ConnectionError as e:
            if attempt == max_retries - 1:
                logger.error(f"Failed to connect to Redis after {max_retries} attempts: {str(e)}")
                raise
            logger.warning(f"Redis connection attempt {attempt + 1} failed, retrying in {retry_delay}s")
            time.sleep(retry_delay)

# Initialize Redis client
try:
    redis_client = get_redis_client()
    logger.info("Successfully connected to Redis")
except Exception as e:
    logger.error(f"Could not initialize Redis client: {str(e)}")
    redis_client = None

def update_leaderboard(submission_id, score):
    """Update the leaderboard with a new submission score"""
    if not redis_client:
        logger.error("Redis client not initialized")
        return False

    try:
        redis_client.zadd('gpu_leaderboard', {str(submission_id): score})
        logger.info(f"Updated leaderboard with submission {submission_id}")
        return True
    except redis.RedisError as e:
        logger.error(f"Redis error updating leaderboard: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error updating leaderboard: {str(e)}")
        return False

def get_top_submissions(limit=10):
    """Get the top N submissions from the leaderboard"""
    if not redis_client:
        logger.error("Redis client not initialized")
        return []

    try:
        # Get submission IDs and scores, sorted by score (descending)
        leaderboard = redis_client.zrevrange(
            'gpu_leaderboard',
            0,
            limit-1,
            withscores=True
        )
        return [(int(sub_id), score) for sub_id, score in leaderboard]
    except redis.RedisError as e:
        logger.error(f"Redis error fetching leaderboard: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {str(e)}")
        return []