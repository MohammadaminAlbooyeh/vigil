"""
FastAPI web service for Income Prediction.
"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn
import logging

from predict import predict_income, predict_proba_income
from utils.validation import validate_prediction_input, log_validation_errors

logger = logging.getLogger(__name__)


app = FastAPI(
    title="Income Prediction API",
    description="API for predicting income categories using machine learning",
    version="1.0.0"
)


class PredictionRequest(BaseModel):
    age: int = Field(..., ge=18, le=100, description="Age of the person")
    workclass: str = Field(..., description="Work class",
                          examples=["Private", "Self-emp-not-inc", "Federal-gov"])
    fnlwgt: int = Field(..., gt=0, description="Final weight")
    education: str = Field(..., description="Education level",
                          examples=["Bachelors", "Masters", "HS-grad"])
    education_num: int = Field(..., ge=1, le=16, description="Education number")
    marital_status: str = Field(..., description="Marital status",
                               examples=["Married-civ-spouse", "Never-married", "Divorced"])
    occupation: str = Field(..., description="Occupation",
                           examples=["Exec-managerial", "Prof-specialty", "Sales"])
    relationship: str = Field(..., description="Relationship status",
                             examples=["Husband", "Wife", "Own-child"])
    race: str = Field(..., description="Race",
                     examples=["White", "Black", "Asian-Pac-Islander"])
    sex: str = Field(..., description="Sex", examples=["Male", "Female"])
    capital_gain: int = Field(..., ge=0, description="Capital gain")
    capital_loss: int = Field(..., ge=0, description="Capital loss")
    hours_per_week: int = Field(..., ge=1, le=99, description="Hours worked per week")
    native_country: str = Field(..., description="Native country",
                               examples=["United-States", "Mexico", "Canada"])


class PredictionResponse(BaseModel):
    prediction: str = Field(..., description="Predicted income category")
    prediction_label: str = Field(..., description="Human readable prediction")


class ProbabilityResponse(BaseModel):
    probabilities: dict = Field(..., description="Prediction probabilities for each class")


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Predict income category for given features.

    Returns the predicted income category (>50K or <=50K).
    """
    try:
        logger.debug(f"Prediction request received: age={request.age}, workclass={request.workclass}")
        # Convert request to dict
        features = {
            'age': request.age,
            'workclass': request.workclass,
            'fnlwgt': request.fnlwgt,
            'education': request.education,
            'education-num': request.education_num,
            'marital-status': request.marital_status,
            'occupation': request.occupation,
            'relationship': request.relationship,
            'race': request.race,
            'sex': request.sex,
            'capital-gain': request.capital_gain,
            'capital-loss': request.capital_loss,
            'hours-per-week': request.hours_per_week,
            'native-country': request.native_country
        }

        # Validate input
        is_valid, errors = validate_prediction_input(features)
        if not is_valid:
            log_validation_errors(errors, features)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"error": "Input validation failed", "details": errors}
            )

        prediction = predict_income(features)

        # Convert numeric prediction to label
        prediction_label = ">50K" if prediction == 1 else "<=50K"
        logger.info(f"Prediction result: {prediction_label}")

        return PredictionResponse(
            prediction=str(prediction),
            prediction_label=prediction_label
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict_proba", response_model=ProbabilityResponse)
async def predict_proba(request: PredictionRequest):
    """
    Get prediction probabilities for given features.

    Returns probabilities for both income categories.
    """
    try:
        logger.debug(f"Probability request received: age={request.age}, workclass={request.workclass}")
        # Convert request to dict
        features = {
            'age': request.age,
            'workclass': request.workclass,
            'fnlwgt': request.fnlwgt,
            'education': request.education,
            'education-num': request.education_num,
            'marital-status': request.marital_status,
            'occupation': request.occupation,
            'relationship': request.relationship,
            'race': request.race,
            'sex': request.sex,
            'capital-gain': request.capital_gain,
            'capital-loss': request.capital_loss,
            'hours-per-week': request.hours_per_week,
            'native-country': request.native_country
        }

        # Validate input
        is_valid, errors = validate_prediction_input(features)
        if not is_valid:
            log_validation_errors(errors, features)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"error": "Input validation failed", "details": errors}
            )

        probabilities = predict_proba_income(features)
        logger.info(f"Probability result: <=50K={probabilities[0]:.4f}, >50K={probabilities[1]:.4f}")

        return ProbabilityResponse(
            probabilities={
                "<=50K": float(probabilities[0]),
                ">50K": float(probabilities[1])
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Probability prediction failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Probability prediction failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Income Prediction API is running"}


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Income Prediction API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


def main():
    """Entry point for running the API server."""
    uvicorn.run(app, host="0.0.0.0", port=8000)