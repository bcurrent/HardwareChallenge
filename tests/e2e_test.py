import requests
import time
import logging
from datetime import datetime

# Configure logging with more detail
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:5000"

def test_health_check():
    logger.info("Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data and data["status"] == "healthy"
        assert "timestamp" in data
        logger.info("✓ Health check test passed")
    except Exception as e:
        logger.error(f"❌ Health check test failed: {str(e)}")
        raise

def test_submission_process():
    logger.info("Testing submission process...")
    try:
        # Test valid submission
        valid_data = {
            "gpu_utilization": 85.5,
            "memory_usage": 90.2,
            "power_efficiency": 88.7,
            "completion_time": 45.3,
            "accuracy": 95.1
        }

        logger.debug(f"Sending valid submission: {valid_data}")
        response = requests.post(f"{BASE_URL}/submit_qualification", json=valid_data)
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response content: {response.text}")

        assert response.status_code == 200
        data = response.json()
        assert "success" in data and data["success"] is True
        assert "score" in data
        assert "submission_id" in data
        logger.info("✓ Valid submission test passed")

        # Test invalid submission
        invalid_data = {
            "gpu_utilization": 150,  # Invalid value > 100
            "memory_usage": -10,     # Invalid negative value
            "power_efficiency": 88.7,
            "completion_time": 45.3,
            "accuracy": 95.1
        }

        logger.debug(f"Sending invalid submission: {invalid_data}")
        response = requests.post(f"{BASE_URL}/submit_qualification", json=invalid_data)
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response content: {response.text}")

        assert response.status_code == 400
        logger.info("✓ Invalid submission test passed")
    except Exception as e:
        logger.error(f"❌ Submission test failed: {str(e)}")
        logger.error(f"Last response: {getattr(response, 'text', 'No response')}")
        raise

def test_rate_limiting():
    logger.info("Testing rate limiting...")
    try:
        valid_data = {
            "gpu_utilization": 85.5,
            "memory_usage": 90.2,
            "power_efficiency": 88.7,
            "completion_time": 45.3,
            "accuracy": 95.1
        }

        # Send requests until rate limit is hit
        responses = []
        for i in range(12):  # Try to exceed the 10/hour limit
            logger.debug(f"Sending request {i+1}/12")
            response = requests.post(f"{BASE_URL}/submit_qualification", json=valid_data)
            responses.append(response.status_code)
            logger.debug(f"Response {i+1}: status {response.status_code}")

        # Verify rate limiting
        assert 429 in responses, "Rate limiting not working"
        logger.info("✓ Rate limiting test passed")
    except Exception as e:
        logger.error(f"❌ Rate limiting test failed: {str(e)}")
        raise

def test_leaderboard():
    logger.info("Testing leaderboard...")
    try:
        response = requests.get(f"{BASE_URL}/leaderboard")
        logger.debug(f"Leaderboard response: {response.text}")
        assert response.status_code == 200
        data = response.json()

        # Verify leaderboard structure
        assert "leaderboard" in data
        assert isinstance(data["leaderboard"], list)

        # Verify entries are properly sorted
        if len(data["leaderboard"]) > 1:
            scores = [entry["score"] for entry in data["leaderboard"]]
            assert all(scores[i] >= scores[i+1] for i in range(len(scores)-1)), "Leaderboard not properly sorted"

        # Verify slot allocation
        assert "current_slot" in data
        logger.info("✓ Leaderboard test passed")
    except Exception as e:
        logger.error(f"❌ Leaderboard test failed: {str(e)}")
        raise

def run_all_tests():
    try:
        logger.info("Starting end-to-end tests...")
        test_health_check()
        test_submission_process()
        test_rate_limiting()
        test_leaderboard()
        logger.info("✅ All tests passed successfully!")
    except AssertionError as e:
        logger.error(f"❌ Test failed: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    run_all_tests()