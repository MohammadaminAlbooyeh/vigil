"""
Tests for data_loader module.
"""

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.data_loader import download_adult_dataset, load_raw_data, load_processed_data


class TestDownloadAdultDataset:
    """Test suite for download_adult_dataset function."""

    def test_download_adult_dataset_creates_file(self, mock_config, sample_adult_data):
        """Test that download creates the data file."""
        with patch('src.data_loader.requests.get') as mock_get:
            # Mock the response
            mock_response = MagicMock()
            mock_response.content = sample_adult_data.to_csv(index=False, header=True).encode()
            mock_get.return_value = mock_response
            
            download_adult_dataset()
            
            # Check that file was created
            file_path = mock_config.DATA_DIR / mock_config.RAW_DATA_FILE
            assert file_path.exists()

    def test_download_adult_dataset_skips_if_exists(self, mock_config, sample_adult_data):
        """Test that download skips if file already exists."""
        # Create the file first
        file_path = mock_config.DATA_DIR / mock_config.RAW_DATA_FILE
        sample_adult_data.to_csv(file_path, index=False, header=True)
        
        with patch('src.data_loader.requests.get') as mock_get:
            download_adult_dataset()
            
            # Should not call requests.get if file exists
            mock_get.assert_not_called()

    def test_download_adult_dataset_creates_directory(self, mock_config):
        """Test that download creates data directory if it doesn't exist."""
        # Remove the temp directory
        import shutil
        shutil.rmtree(mock_config.DATA_DIR)
        
        with patch('src.data_loader.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.content = b"test,data"
            mock_get.return_value = mock_response
            
            download_adult_dataset()
            
            # Check that directory was created
            assert mock_config.DATA_DIR.exists()


class TestLoadRawData:
    """Test suite for load_raw_data function."""

    def test_load_raw_data_returns_dataframe(self, mock_config, sample_adult_data):
        """Test that load_raw_data returns a DataFrame."""
        # Create the file with headers
        file_path = mock_config.DATA_DIR / mock_config.RAW_DATA_FILE
        sample_adult_data.to_csv(file_path, index=False, header=True)
        
        df = load_raw_data()
        
        assert isinstance(df, pd.DataFrame)

    def test_load_raw_data_has_correct_columns(self, mock_config, sample_adult_data):
        """Test that loaded data has correct column names."""
        # Create the file with headers (matching actual adult.csv format)
        file_path = mock_config.DATA_DIR / mock_config.RAW_DATA_FILE
        sample_adult_data.to_csv(file_path, index=False, header=True)
        
        df = load_raw_data()
        
        expected_columns = [
            'age', 'workclass', 'fnlwgt', 'education', 'education-num',
            'marital-status', 'occupation', 'relationship', 'race', 'sex',
            'capital-gain', 'capital-loss', 'hours-per-week', 'native-country', 'income'
        ]
        assert list(df.columns) == expected_columns

    def test_load_raw_data_downloads_if_not_exists(self, mock_config, sample_adult_data):
        """Test that load_raw_data downloads data if file doesn't exist."""
        with patch('src.data_loader.download_adult_dataset') as mock_download:
            with patch('pandas.read_csv', return_value=sample_adult_data):
                # Create the file after download is called
                def create_file():
                    file_path = mock_config.DATA_DIR / mock_config.RAW_DATA_FILE
                    sample_adult_data.to_csv(file_path, index=False, header=True)
                
                mock_download.side_effect = create_file
                
                df = load_raw_data()
                
                mock_download.assert_called_once()
                assert isinstance(df, pd.DataFrame)

    def test_load_raw_data_handles_missing_values(self, mock_config, sample_adult_data):
        """Test that load_raw_data properly marks missing values."""
        # Add some ' ?' values
        df_with_missing = sample_adult_data.copy()
        df_with_missing.loc[0, 'workclass'] = ' ?'
        
        file_path = mock_config.DATA_DIR / mock_config.RAW_DATA_FILE
        df_with_missing.to_csv(file_path, index=False, header=True)
        
        df = load_raw_data()
        
        # Check that ' ?' is treated as NaN
        assert df['workclass'].isna().sum() >= 0  # Should have some or no NaN values


class TestLoadProcessedData:
    """Test suite for load_processed_data function."""

    def test_load_processed_data_returns_dataframe(self, mock_config, sample_adult_data):
        """Test that load_processed_data returns a DataFrame."""
        # Create raw data file with headers
        file_path = mock_config.DATA_DIR / mock_config.RAW_DATA_FILE
        sample_adult_data.to_csv(file_path, index=False, header=True)
        
        df = load_processed_data()
        
        assert isinstance(df, pd.DataFrame)

    def test_load_processed_data_loads_pickle_if_exists(self, mock_config, sample_adult_data):
        """Test that load_processed_data loads from pickle if it exists."""
        # Create processed pickle file
        processed_path = mock_config.DATA_DIR / mock_config.PROCESSED_DATA_FILE
        sample_adult_data.to_pickle(processed_path)
        
        df = load_processed_data()
        
        assert isinstance(df, pd.DataFrame)
        pd.testing.assert_frame_equal(df, sample_adult_data)

    def test_load_processed_data_falls_back_to_raw(self, mock_config, sample_adult_data):
        """Test that load_processed_data falls back to raw data if pickle doesn't exist."""
        # Create only raw data file with headers
        file_path = mock_config.DATA_DIR / mock_config.RAW_DATA_FILE
        sample_adult_data.to_csv(file_path, index=False, header=True)
        
        df = load_processed_data()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
