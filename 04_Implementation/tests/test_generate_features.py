import pytest
import pandas as pd
import numpy as np
import src.generate_features as gf


# create a fixture that provides the DataFrame
@pytest.fixture
def sample_df():
    return pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': [100, 200, 300, 400, 500]
    })


# Test for log_transform function
def test_log_transform(sample_df):
    # Happy test
    result = gf.log_transform(sample_df.copy(), ['A', 'B'])
    assert result['A'].equals(sample_df['A'].apply(np.log)), "Happy test failed for column A"
    assert result['B'].equals(sample_df['B'].apply(np.log)), "Happy test failed for column B"
    
    # Unhappy test
    with pytest.raises(ValueError):
        gf.log_transform(sample_df.copy(), ['C'])


# Test for drop_columns function
def test_drop_columns(sample_df):

    # Happy test
    result = gf.drop_columns(sample_df.copy(), ['A'])
    assert 'A' not in result.columns, "Happy test failed, column A is not dropped"
    assert 'B' in result.columns, "Happy test failed, column B is missing"

    # Unhappy test
    with pytest.raises(KeyError):
        gf.drop_columns(sample_df.copy(), ['C'])
