"""
Setup script for income-prediction package.

This setup.py is kept for backward compatibility but the actual configuration
is in pyproject.toml for modern Python packaging.
"""

from setuptools import setup

# Read the long description from README.md if it exists
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = ""

setup(
    name="income-prediction",
    version="0.1.0",
    author="Income Prediction Team",
    author_email="team@example.com",
    description="End-to-end income prediction project using machine learning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/username/income-prediction",
    package_dir={"": "src"},
    packages=["src"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.5.0",
        "scikit-learn>=1.2.0",
        "joblib>=1.2.0",
        "requests>=2.28.0",
        "numpy>=1.21.0",
        "xgboost>=1.7.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.20.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.12.0",
        "scipy>=1.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
)
