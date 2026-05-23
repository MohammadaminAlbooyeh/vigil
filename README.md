# End-to-End Income Prediction Project

A complete machine learning project for predicting whether an individual's annual income exceeds $50,000 based on demographic and employment data from the Adult Census dataset.

## Features

- **Data Pipeline**: Automated data loading, preprocessing, and feature engineering
- **Machine Learning Model**: Random Forest classifier with hyperparameter tuning
- **Model Evaluation**: Comprehensive metrics including accuracy, precision, recall, and ROC-AUC
- **Prediction API**: Easy-to-use prediction functions for new data
- **Comprehensive Testing**: Full test suite with 68+ test cases
- **Exploratory Analysis**: Jupyter notebooks for data exploration and model evaluation
- **Modular Architecture**: Clean, maintainable code structure

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/MohammadaminAlbooyeh/end_to_end_income_prediction_project.git
cd end_to_end_income_prediction_project
```

2. Install dependencies:
```bash
pip install -e .
```

For development dependencies:
```bash
pip install -e ".[dev]"
```

## Usage

### Training the Model

Train the income prediction model:

```bash
python -m src.train
```

This will:
- Download the Adult dataset (if not present)
- Preprocess the data
- Train a Random Forest classifier
- Save the model to `models/income_model.pkl`

### Making Predictions

#### Command Line Interface

Use the installed CLI tool:

```bash
income-predict --age 35 --workclass Private --fnlwgt 200000 --education Bachelors --education-num 13 --marital-status Married-civ-spouse --occupation Exec-managerial --relationship Husband --race White --sex Male --capital-gain 0 --capital-loss 0 --hours-per-week 40 --native-country United-States
```

Output:
```
Predicted income: 0
```

#### Web API

Start the API server:

```bash
income-api
```

The API will be available at `http://localhost:8000`

**Endpoints:**
- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation
- `POST /predict` - Make prediction
- `POST /predict_proba` - Get prediction probabilities

**Example API request:**

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
       "capital_gain": 0,
       "capital_loss": 0,
       "hours_per_week": 40,
       "native_country": "United-States"
     }'
```

**Response:**
```json
{
  "prediction": "0",
  "prediction_label": "<=50K"
}
```

### Running Tests

Execute the full test suite:

```bash
pytest tests/
```

## Project Structure

```
end_to_end_income_prediction_project/
├── src/                          # Source code
│   ├── __init__.py
│   ├── config.py                 # Configuration settings
│   ├── data_loader.py            # Data loading utilities
│   ├── train.py                  # Model training script
│   ├── predict.py                # Prediction functions
│   ├── features/                 # Feature engineering
│   │   ├── __init__.py
│   │   └── feature_engineering.py
│   ├── models/                   # Model training logic
│   │   ├── __init__.py
│   │   └── model_training.py
│   └── utils/                    # Utilities
│       ├── __init__.py
│       ├── preprocessing.py
│       └── helpers.py
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_*.py                 # Individual test files
│   └── pytest.ini
├── notebooks/                    # Jupyter notebooks
│   ├── data_exploration.ipynb    # Data analysis
│   └── model_evaluation.ipynb    # Model evaluation
├── models/                       # Trained models and dataset
│   ├── adult.csv                 # Adult Census dataset (input data)
│   ├── income_model.pkl          # Trained XGBoost model
│   └── preprocessor.pkl          # Preprocessor pipeline
├── docs/                         # Documentation
├── pyproject.toml                # Project configuration
├── setup.py                      # Setup script
└── README.md                     # This file
```

## Dataset

This project uses the [Adult Census Income dataset](https://archive.ics.uci.edu/dataset/2/adult) from UCI Machine Learning Repository.

**Features:**
- Demographic: age, sex, race, native-country
- Employment: workclass, occupation, hours-per-week
- Education: education, education-num
- Financial: capital-gain, capital-loss
- Relationship: marital-status, relationship

**Target:** Income category (>50K or <=50K)

## Model

**Algorithm:** XGBoost Classifier
**Hyperparameters:**
- n_estimators: 100
- max_depth: 10
- random_state: 42

**Performance (on test set):**
- Accuracy: 86.50%
- Precision: 0.79 (for >50K class)
- Recall: 0.63 (for >50K class)
- ROC-AUC: 0.91

## Development

### Code Quality

- **Linting:** flake8
- **Formatting:** black
- **Type checking:** mypy

Run quality checks:
```bash
black src/ tests/
flake8 src/ tests/
mypy src/
```

### Testing

Run tests with coverage:
```bash
pytest --cov=src tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- UCI Machine Learning Repository for the Adult dataset
- Scikit-learn for machine learning algorithms
- Pandas and NumPy for data manipulation