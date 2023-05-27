import pytest
import pandas as pd
import numpy as np
import src.generate_features as gf


# Create a fixture that provides the DataFrame
@pytest.fixture
def sample_df():
    return pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': [100, 200, 300, 400, 500]
    })


#------Test for log_transform function------#

def test_log_transform(sample_df):
    # Happy test
    result = gf.log_transform(sample_df.copy(), ['A', 'B'])
    assert result['A'].equals(sample_df['A'].apply(np.log)), "Happy test failed for column A"
    assert result['B'].equals(sample_df['B'].apply(np.log)), "Happy test failed for column B"
    
    # Unhappy test
    with pytest.raises(KeyError):
        gf.log_transform(sample_df.copy(), ['C'])


#------Test for drop_columns function------#

def test_drop_columns(sample_df):

    # Happy test
    result = gf.drop_columns(sample_df.copy(), ['A'])
    assert 'A' not in result.columns, "Happy test failed, column A is not dropped"
    assert 'B' in result.columns, "Happy test failed, column B is missing"

    # Unhappy test
    with pytest.raises(KeyError):
        gf.drop_columns(sample_df.copy(), ['C'])

def test_drop_multiple_columns(sample_df):
    # Happy test
    result = gf.drop_columns(sample_df.copy(), ['A', 'B'])
    assert 'A' not in result.columns, "Happy test failed, column A is not dropped"
    assert 'B' not in result.columns, "Happy test failed, column B is not dropped"


#------Test for filter_airlines function------#

@pytest.fixture
def mock_df():
    return pd.DataFrame({
        'airline': ['A', 'A', 'A', 'B', 'B'],
    })

def test_filter_airlines(mock_df):
    # Happy test
    result = gf.filter_airlines(mock_df, 3)
    assert 'B' not in result['airline'].values, "Happy test failed, airline B should not be in the result"
    result = gf.filter_airlines(mock_df, 5)
    assert result.empty, "Happy test failed, the result should be an empty DataFrame"

    # Unhappy test
    with pytest.raises(TypeError):
        gf.filter_airlines(mock_df, 'C')

def test_filter_airlines_no_airlines():
    # Creating a DataFrame without an 'airline' column
    data_no_airline = pd.DataFrame()

    # Unhappy test
    with pytest.raises(KeyError):
        gf.filter_airlines(data_no_airline, 3)
