# Deployment Guide

Complete guide to deploy the Income Prediction application in production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [Docker Deployment](#docker-deployment)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [Monitoring and Logging](#monitoring-and-logging)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- Python 3.8+
- Docker 20.10+ (optional, for containerized deployment)
- 2GB RAM minimum
- 500MB disk space

### Required Software

- `pip` package manager
- `git` (optional, for cloning repository)

## Local Development Setup

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/MohammadaminAlbooyeh/end_to_end_income_prediction_project.git
cd end_to_end_income_prediction_project

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Install development dependencies (optional)
pip install -e ".[dev]"
```

### 2. Train the Model

The trained models (`income_model.pkl` and `preprocessor.pkl`) must exist before running the API or CLI.

```bash
# Train the model
python -m src.train

# Output:
# Model trained and saved.
# Test accuracy: 0.8650
```

Model files are saved to `models/` directory:
- `models/income_model.pkl` - Trained XGBoost classifier with preprocessing pipeline
- `models/preprocessor.pkl` - Separate preprocessor for manual transformations

### 3. Verify Installation

```bash
# Run tests
pytest tests/ -v

# Expected output: 68 passed
```

## Docker Deployment

### Build Docker Image

Create a `Dockerfile` in the project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Install package
RUN pip install -e .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run API
CMD ["python", "-m", "src.api"]
```

### Build and Run Container

```bash
# Build image
docker build -t income-prediction:latest .

# Run container
docker run -p 8000:8000 \
    -e LOG_LEVEL=INFO \
    income-prediction:latest

# Access API at http://localhost:8000
```

### Docker Compose Setup

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      LOG_LEVEL: INFO
      WORKERS: 4
    volumes:
      - ./models:/app/models
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
```

Run with Docker Compose:

```bash
docker-compose up -d
```

## Environment Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
WORKERS=4

# Model Settings
MODEL_PATH=models/income_model.pkl
PREPROCESSOR_PATH=models/preprocessor.pkl

# Application
DEBUG=False
ENVIRONMENT=production
```

### Configuration Files

Edit `src/config.py` to customize:

- Data paths
- Model hyperparameters
- Feature lists
- Test size and random state

## Running the Application

### REST API Server

```bash
# Start API server
python -m src.api

# Access interactive docs at http://localhost:8000/docs
# Health check: http://localhost:8000/health
# API root: http://localhost:8000/
```

### Command Line Interface

```bash
# Make single prediction
income-predict \
  --age 35 \
  --workclass Private \
  --fnlwgt 200000 \
  --education Bachelors \
  --education-num 13 \
  --marital-status Married-civ-spouse \
  --occupation Exec-managerial \
  --relationship Husband \
  --race White \
  --sex Male \
  --capital-gain 15000 \
  --capital-loss 0 \
  --hours-per-week 40 \
  --native-country United-States

# Output: Predicted income: 1
```

### Batch Predictions (Python)

```python
from src.predict import predict_income

# Single prediction
features = {
    'age': 35,
    'workclass': 'Private',
    'fnlwgt': 200000,
    'education': 'Bachelors',
    'education-num': 13,
    'marital-status': 'Married-civ-spouse',
    'occupation': 'Exec-managerial',
    'relationship': 'Husband',
    'race': 'White',
    'sex': 'Male',
    'capital-gain': 15000,
    'capital-loss': 0,
    'hours-per-week': 40,
    'native-country': 'United-States'
}

prediction = predict_income(features)
print(f"Prediction: {'>50K' if prediction == 1 else '<=50K'}")
```

## Monitoring and Logging

### Logging Configuration

Logging is configured in each module:

```python
import logging

logger = logging.getLogger(__name__)

# In __main__ blocks:
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Log Levels

- `DEBUG` - Detailed diagnostic information
- `INFO` - General informational messages
- `WARNING` - Warning messages for potentially harmful situations
- `ERROR` - Error messages with traceback
- `CRITICAL` - Critical errors requiring immediate attention

### Example Log Output

```
2024-05-23 13:27:46,123 - src.train - INFO - Starting model training
2024-05-23 13:27:46,124 - src.train - INFO - Loading raw data
2024-05-23 13:27:47,456 - src.train - INFO - Loaded 32560 samples with 15 features
2024-05-23 13:27:48,789 - src.train - INFO - Test accuracy: 0.8650
```

### Monitoring Production Metrics

Key metrics to monitor:

1. **Model Performance**
   - Prediction accuracy
   - False positive/negative rates
   - Model latency

2. **API Health**
   - Request/response times
   - Error rates
   - Active connections

3. **System Resources**
   - CPU usage
   - Memory consumption
   - Disk space

4. **Data Quality**
   - Missing value rates
   - Feature distributions
   - Input schema violations

## Troubleshooting

### Model Not Found Error

**Error**: `FileNotFoundError: Model file not found at models/income_model.pkl`

**Solution**:
```bash
# Retrain the model
python -m src.train
```

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
```bash
# Ensure package is installed
pip install -e .

# Or add src to Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/project"
```

### API Connection Refused

**Error**: `ConnectionRefusedError: [Errno 61] Connection refused`

**Solution**:
```bash
# Check if API is running
curl http://localhost:8000/health

# Start API if not running
python -m src.api
```

### Memory Issues

**Problem**: Out of memory errors when processing large datasets

**Solution**:
```bash
# Use batch processing for large datasets
# Process data in chunks of 1000
chunk_size = 1000
for i in range(0, len(data), chunk_size):
    chunk = data[i:i+chunk_size]
    predictions = model.predict(chunk)
```

### Model Performance Degradation

**Problem**: Accuracy drops over time

**Solution**:
1. Monitor input data distribution
2. Check for data quality issues
3. Retrain model periodically
4. Implement model versioning to track performance

## Production Checklist

- [ ] Models trained and saved to `models/` directory
- [ ] Tests pass (`pytest tests/ -v`)
- [ ] Code quality checks pass (black, flake8, mypy)
- [ ] Docker image builds successfully
- [ ] API endpoints tested and working
- [ ] Logging configured and working
- [ ] Environment variables set
- [ ] Health check endpoint responds
- [ ] Documentation updated
- [ ] Backup strategy in place for model files

## Additional Resources

- [API Documentation](README.md#features)
- [Test Suite](tests/)
- [Notebooks](notebooks/)
- [Configuration](src/config.py)
- [Model Training](src/train.py)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review application logs
3. Run tests to verify installation
4. Check GitHub issues
5. Contact the development team
