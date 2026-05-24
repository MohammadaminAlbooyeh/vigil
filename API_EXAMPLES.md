# API Usage Examples

Complete guide with examples for using the Income Prediction API.

## Table of Contents

- [Getting Started](#getting-started)
- [cURL Examples](#curl-examples)
- [Python Examples](#python-examples)
- [JavaScript Examples](#javascript-examples)
- [Error Handling](#error-handling)
- [Batch Predictions](#batch-predictions)

## Getting Started

### Starting the API Server

```bash
# Start the API
python -m src.api

# API will be available at http://localhost:8000
# Interactive API documentation: http://localhost:8000/docs
```

### Base URL

```
http://localhost:8000
```

### Authentication

Currently, the API does not require authentication. For production, implement API key authentication.

## cURL Examples

### 1. Health Check

```bash
curl -X GET "http://localhost:8000/health"
```

**Response:**
```json
{
  "status": "healthy",
  "message": "Income Prediction API is running"
}
```

### 2. Make a Prediction

**Request:**
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 35,
    "workclass": "Private",
    "fnlwgt": 200000,
    "education": "Bachelors",
    "education_num": 13,
    "marital_status": "Married-civ-spouse",
    "occupation": "Exec-managerial",
    "relationship": "Husband",
    "race": "White",
    "sex": "Male",
    "capital_gain": 15000,
    "capital_loss": 0,
    "hours_per_week": 40,
    "native_country": "United-States"
  }'
```

**Response:**
```json
{
  "prediction": "1",
  "prediction_label": ">50K"
}
```

### 3. Get Prediction Probabilities

```bash
curl -X POST "http://localhost:8000/predict_proba" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 35,
    "workclass": "Private",
    "fnlwgt": 200000,
    "education": "Bachelors",
    "education_num": 13,
    "marital_status": "Married-civ-spouse",
    "occupation": "Exec-managerial",
    "relationship": "Husband",
    "race": "White",
    "sex": "Male",
    "capital_gain": 15000,
    "capital_loss": 0,
    "hours_per_week": 40,
    "native_country": "United-States"
  }'
```

**Response:**
```json
{
  "probabilities": {
    "<=50K": 0.00006365776,
    ">50K": 0.99993634224
  }
}
```

### 4. Invalid Input Handling

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 35,
    "workclass": "InvalidWorkclass",
    "fnlwgt": 200000,
    "education": "Bachelors",
    "education_num": 13,
    "marital_status": "Married-civ-spouse",
    "occupation": "Exec-managerial",
    "relationship": "Husband",
    "race": "White",
    "sex": "Male",
    "capital_gain": 15000,
    "capital_loss": 0,
    "hours_per_week": 40,
    "native_country": "United-States"
  }'
```

**Response (422):**
```json
{
  "detail": {
    "error": "Input validation failed",
    "details": [
      "workclass must be one of {'Private', 'Self-emp-not-inc', ...}, got 'InvalidWorkclass'"
    ]
  }
}
```

## Python Examples

### 1. Using the Requests Library

```python
import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000"

# Prediction request data
data = {
    "age": 35,
    "workclass": "Private",
    "fnlwgt": 200000,
    "education": "Bachelors",
    "education_num": 13,
    "marital_status": "Married-civ-spouse",
    "occupation": "Exec-managerial",
    "relationship": "Husband",
    "race": "White",
    "sex": "Male",
    "capital_gain": 15000,
    "capital_loss": 0,
    "hours_per_week": 40,
    "native_country": "United-States"
}

# Make prediction
response = requests.post(f"{BASE_URL}/predict", json=data)
result = response.json()

print(f"Prediction: {result['prediction_label']}")
print(f"Confidence: {result.get('confidence', 'N/A')}")
```

### 2. Get Probabilities

```python
import requests

BASE_URL = "http://localhost:8000"

data = {
    "age": 35,
    "workclass": "Private",
    "fnlwgt": 200000,
    "education": "Bachelors",
    "education_num": 13,
    "marital_status": "Married-civ-spouse",
    "occupation": "Exec-managerial",
    "relationship": "Husband",
    "race": "White",
    "sex": "Male",
    "capital_gain": 15000,
    "capital_loss": 0,
    "hours_per_week": 40,
    "native_country": "United-States"
}

response = requests.post(f"{BASE_URL}/predict_proba", json=data)
proba = response.json()

print(f"P(<=50K): {proba['probabilities']['<=50K']:.4f}")
print(f"P(>50K): {proba['probabilities']['>50K']:.4f}")
```

### 3. Error Handling

```python
import requests
from requests.exceptions import RequestException

def make_prediction(data, max_retries=3):
    """Make prediction with error handling."""
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "http://localhost:8000/predict",
                json=data,
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.HTTPError as e:
            if response.status_code == 422:
                print(f"Validation error: {response.json()}")
                return None
            elif response.status_code == 500:
                print(f"Server error: {response.json()}")
                if attempt < max_retries - 1:
                    print(f"Retrying... ({attempt + 1}/{max_retries})")
                    continue
                return None
        
        except RequestException as e:
            print(f"Request failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying... ({attempt + 1}/{max_retries})")
                continue
            return None
    
    return None

# Use the function
data = {
    "age": 35,
    "workclass": "Private",
    # ... other fields
}

result = make_prediction(data)
if result:
    print(f"Prediction: {result['prediction_label']}")
```

### 4. Batch Predictions

```python
import requests
import pandas as pd

def batch_predict(predictions_data):
    """Make predictions for multiple records."""
    results = []
    
    for i, record in enumerate(predictions_data):
        try:
            response = requests.post(
                "http://localhost:8000/predict",
                json=record,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                result['record_id'] = i
                results.append(result)
            else:
                print(f"Record {i}: Error {response.status_code}")
        
        except Exception as e:
            print(f"Record {i}: Failed - {e}")
    
    return pd.DataFrame(results)

# Example data
data = [
    {
        "age": 35, "workclass": "Private", "fnlwgt": 200000,
        "education": "Bachelors", "education_num": 13,
        "marital_status": "Married-civ-spouse", "occupation": "Exec-managerial",
        "relationship": "Husband", "race": "White", "sex": "Male",
        "capital_gain": 15000, "capital_loss": 0,
        "hours_per_week": 40, "native_country": "United-States"
    },
    {
        "age": 25, "workclass": "Private", "fnlwgt": 150000,
        "education": "Some-college", "education_num": 10,
        "marital_status": "Never-married", "occupation": "Tech-support",
        "relationship": "Own-child", "race": "White", "sex": "Female",
        "capital_gain": 0, "capital_loss": 0,
        "hours_per_week": 35, "native_country": "United-States"
    }
]

# Make batch predictions
results_df = batch_predict(data)
print(results_df)
```

## JavaScript Examples

### 1. Using Fetch API

```javascript
// Make a prediction
async function makePrediction() {
  const data = {
    age: 35,
    workclass: "Private",
    fnlwgt: 200000,
    education: "Bachelors",
    education_num: 13,
    marital_status: "Married-civ-spouse",
    occupation: "Exec-managerial",
    relationship: "Husband",
    race: "White",
    sex: "Male",
    capital_gain: 15000,
    capital_loss: 0,
    hours_per_week: 40,
    native_country: "United-States"
  };

  try {
    const response = await fetch("http://localhost:8000/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      const error = await response.json();
      console.error("Error:", error);
      return;
    }

    const result = await response.json();
    console.log(`Prediction: ${result.prediction_label}`);
  } catch (error) {
    console.error("Request failed:", error);
  }
}

// Call the function
makePrediction();
```

### 2. Using Axios

```javascript
const axios = require('axios');

const data = {
  age: 35,
  workclass: "Private",
  fnlwgt: 200000,
  education: "Bachelors",
  education_num: 13,
  marital_status: "Married-civ-spouse",
  occupation: "Exec-managerial",
  relationship: "Husband",
  race: "White",
  sex: "Male",
  capital_gain: 15000,
  capital_loss: 0,
  hours_per_week: 40,
  native_country: "United-States"
};

axios.post("http://localhost:8000/predict", data)
  .then(response => {
    console.log(`Prediction: ${response.data.prediction_label}`);
  })
  .catch(error => {
    console.error("Error:", error.response.data);
  });
```

## Error Handling

### Common Error Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Prediction successful |
| 422 | Validation Error | Invalid input values |
| 500 | Server Error | Model loading failed, prediction error |

### Error Response Format

```json
{
  "detail": {
    "error": "Error description",
    "details": ["Specific error 1", "Specific error 2"]
  }
}
```

### Valid Feature Values

**Categorical Features:**
- `workclass`: Private, Self-emp-not-inc, Self-emp-inc, Federal-gov, Local-gov, State-gov, Without-pay, Never-worked
- `education`: Bachelors, Some-college, 11th, HS-grad, Prof-school, Assoc-acdm, Assoc-voc, 9th, 7th-8th, 12th, Masters, 1st-4th, 10th, Doctorate, 5th-6th, Preschool
- `marital-status`: Married-civ-spouse, Divorced, Never-married, Separated, Widowed, Married-spouse-absent, Married-AF-spouse
- `occupation`: Tech-support, Craft-repair, Other-service, Sales, Exec-managerial, Prof-specialty, Handlers-cleaners, Machine-op-inspct, Adm-clerical, Farming-fishing, Transport-moving, Priv-house-serv, Protective-serv, Armed-Forces
- `relationship`: Wife, Own-child, Husband, Not-in-family, Other-relative, Unmarried
- `race`: White, Asian-Pac-Islander, Amer-Indian-Eskimo, Other, Black
- `sex`: Female, Male

**Numeric Ranges:**
- `age`: 18-100
- `fnlwgt`: 1-1,500,000
- `education-num`: 1-16
- `capital-gain`: 0-999,999
- `capital-loss`: 0-999,999
- `hours-per-week`: 1-99

## Batch Predictions

### Using pandas DataFrame

```python
import pandas as pd
import requests

# Load data from CSV
df = pd.read_csv('predictions.csv')

results = []
for idx, row in df.iterrows():
    data = row.to_dict()
    response = requests.post("http://localhost:8000/predict", json=data)
    
    if response.status_code == 200:
        result = response.json()
        result['id'] = idx
        results.append(result)

# Save results
results_df = pd.DataFrame(results)
results_df.to_csv('predictions_results.csv', index=False)
```

## Interactive API Documentation

Access Swagger UI with interactive API explorer:
```
http://localhost:8000/docs
```

Try out endpoints directly in your browser with automatic documentation!
