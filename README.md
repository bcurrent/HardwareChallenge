# GPU Qualification Scoring API

A high-performance Flask-based API designed to manage and evaluate GPU submissions with real-time leaderboard tracking and intelligent slot management.

## 🏗️ Architecture

<div align="center">
  <img src="architecture.svg" alt="Architecture Diagram" width="800"/>
</div>

The system consists of several key components:
- **Flask Application**: Core backend service handling HTTP requests
- **PostgreSQL Database**: Persistent storage for submissions and user data
- **Redis Cache**: High-speed caching for leaderboard and rate limiting
- **Services**: 
  - Scoring System: Evaluates GPU performance
  - Rate Limiter: Manages API usage limits
  - Slot Manager: Handles GPU slot allocation

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11 or higher
- PostgreSQL database
- Redis server
- Git (for version control)

### Step-by-Step Setup

1. **Clone the Repository**
   ```bash
   git clone <your-repository-url>
   cd gpu-qualification-api
   ```

2. **Set Up Environment Variables**
   Create a `.env` file with:
   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/dbname
   FLASK_SECRET_KEY=your-secret-key-here
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start Redis Server**
   ```bash
   redis-server
   ```

5. **Run the Application**
   ```bash
   python app.py
   ```

The server will start at `http://localhost:5000` 🎉

## 📡 API Usage Guide

### 1. Check API Health
```bash
curl http://localhost:5000/
```
Expected response:
```json
{
    "status": "healthy",
    "timestamp": "2025-01-11T16:58:19.862Z"
}
```

### 2. Submit GPU Qualification
```bash
curl -X POST http://localhost:5000/submit_qualification \
     -H "Content-Type: application/json" \
     -d '{
           "gpu_utilization": 85.5,
           "memory_usage": 90.2,
           "power_efficiency": 88.7,
           "completion_time": 45.3,
           "accuracy": 95.1
         }'
```
Expected response:
```json
{
    "success": true,
    "score": 87.65,
    "submission_id": 123
}
```

### 3. View Leaderboard
```bash
curl http://localhost:5000/leaderboard
```

## 📊 Scoring System Explained

Your GPU performance is evaluated based on five key metrics:

| Metric | Weight | What it Measures |
|--------|---------|-----------------|
| GPU Utilization | 25% | How well your GPU's computing power is used |
| Memory Usage | 20% | Efficiency of memory usage |
| Power Efficiency | 25% | Performance per watt |
| Completion Time | 15% | Speed of task completion |
| Accuracy | 15% | Correctness of results |

### Score Calculation Example
If your submission has:
- GPU Utilization: 90% (22.5 points)
- Memory Usage: 85% (17 points)
- Power Efficiency: 95% (23.75 points)
- Completion Time: 30s (~10 points)
- Accuracy: 98% (14.7 points)

Total Score = 87.95 out of 100

## 🛠️ Development Guide

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/e2e_test.py
```

### Common Issues & Solutions

1. **Database Connection Error**
   ```
   Check if PostgreSQL is running:
   $ pg_isready
   ```

2. **Redis Connection Failed**
   ```
   Verify Redis server status:
   $ redis-cli ping
   ```

3. **Rate Limit Exceeded**
   - Wait for rate limit to reset (10 submissions per hour)
   - Check current rate limit status in Redis

## 🔒 Rate Limiting

To ensure fair usage:
- 10 submissions per hour per IP
- 200 total requests per day per IP
- Leaderboard queries are not rate-limited

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. Make your changes
4. Run tests to ensure everything works
   ```bash
   python -m pytest
   ```
5. Commit your changes
   ```bash
   git commit -m "Add amazing feature"
   ```
6. Push to your branch
   ```bash
   git push origin feature/amazing-feature
   ```
7. Open a Pull Request

## 🆘 Need Help?

1. Check the [Common Issues](#common-issues--solutions) section
2. Open an issue with:
   - What you were trying to do
   - What happened instead
   - Any error messages
   - Your environment details

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
Made with ❤️ by Your Team