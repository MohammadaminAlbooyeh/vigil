"""
Command Line Interface for Income Prediction.
"""

import argparse
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from predict import predict_income

logger = logging.getLogger(__name__)


def main():
    """Main CLI entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger.info("Starting income prediction CLI")

    parser = argparse.ArgumentParser(
        description="Predict income category using machine learning model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  income-predict --age 35 --workclass Private --fnlwgt 200000 --education Bachelors --education-num 13 --marital-status Married-civ-spouse --occupation Exec-managerial --relationship Husband --race White --sex Male --capital-gain 0 --capital-loss 0 --hours-per-week 40 --native-country United-States

  income-predict --help
        """
    )

    # Required arguments
    parser.add_argument('--age', type=int, required=True, help='Age of the person')
    parser.add_argument('--workclass', type=str, required=True,
                       choices=['Private', 'Self-emp-not-inc', 'Self-emp-inc', 'Federal-gov',
                               'Local-gov', 'State-gov', 'Without-pay', 'Never-worked'],
                       help='Work class')
    parser.add_argument('--fnlwgt', type=int, required=True, help='Final weight')
    parser.add_argument('--education', type=str, required=True,
                       choices=['Bachelors', 'Some-college', '11th', 'HS-grad', 'Prof-school',
                               'Assoc-acdm', 'Assoc-voc', '9th', '7th-8th', '12th', 'Masters',
                               '1st-4th', '10th', 'Doctorate', '5th-6th', 'Preschool'],
                       help='Education level')
    parser.add_argument('--education-num', type=int, required=True, help='Education number')
    parser.add_argument('--marital-status', type=str, required=True,
                       choices=['Married-civ-spouse', 'Divorced', 'Never-married', 'Separated',
                               'Widowed', 'Married-spouse-absent', 'Married-AF-spouse'],
                       help='Marital status')
    parser.add_argument('--occupation', type=str, required=True,
                       choices=['Tech-support', 'Craft-repair', 'Other-service', 'Sales',
                               'Exec-managerial', 'Prof-specialty', 'Handlers-cleaners',
                               'Machine-op-inspct', 'Adm-clerical', 'Farming-fishing',
                               'Transport-moving', 'Priv-house-serv', 'Protective-serv',
                               'Armed-Forces'],
                       help='Occupation')
    parser.add_argument('--relationship', type=str, required=True,
                       choices=['Wife', 'Own-child', 'Husband', 'Not-in-family', 'Other-relative', 'Unmarried'],
                       help='Relationship status')
    parser.add_argument('--race', type=str, required=True,
                       choices=['White', 'Asian-Pac-Islander', 'Amer-Indian-Eskimo', 'Other', 'Black'],
                       help='Race')
    parser.add_argument('--sex', type=str, required=True, choices=['Female', 'Male'], help='Sex')
    parser.add_argument('--capital-gain', type=int, required=True, help='Capital gain')
    parser.add_argument('--capital-loss', type=int, required=True, help='Capital loss')
    parser.add_argument('--hours-per-week', type=int, required=True, help='Hours worked per week')
    parser.add_argument('--native-country', type=str, required=True, help='Native country')

    args = parser.parse_args()
    logger.debug(f"CLI args parsed: age={args.age}, workclass={args.workclass}")

    # Convert args to dict
    features = {
        'age': args.age,
        'workclass': args.workclass,
        'fnlwgt': args.fnlwgt,
        'education': args.education,
        'education-num': args.education_num,
        'marital-status': args.marital_status,
        'occupation': args.occupation,
        'relationship': args.relationship,
        'race': args.race,
        'sex': args.sex,
        'capital-gain': args.capital_gain,
        'capital-loss': args.capital_loss,
        'hours-per-week': args.hours_per_week,
        'native-country': args.native_country
    }

    try:
        prediction = predict_income(features)
        label = ">50K" if prediction == 1 else "<=50K"
        logger.info(f"Prediction successful: {label}")
        print(f"Predicted income: {prediction}")
        return 0
    except Exception as e:
        logger.error(f"Prediction failed: {e}", exc_info=True)
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())