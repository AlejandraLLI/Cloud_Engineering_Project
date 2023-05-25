# Libraries 
import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

def generate_features(clean_data: pd.DataFrame, feature_config: dict) -> pd.DataFrame:
    """
    This function generates features from the cleaned data set by calling sub-functions.

    Args:
    --------------------------------------------
        clean_data: Cleaned data set
        feature_config: Configuration dictionary for feature generation

    Returns:
    --------------------------------------------
        features: Data set with generated features
    """

    features = clean_data.copy()

    # Drop specified columns
    try:
        features = drop_columns(features, feature_config.get('drop_columns', []))
    except KeyError:
        logger.error("Error while dropping columns: %s", feature_config.get('drop_columns', []))
    else:
        logger.debug("Dropped columns: %s", feature_config.get('drop_columns', []))

    # Drop airlines with less than 'min_flights' flights
    try:
        features = filter_airlines(features, feature_config.get('filter_airlines', 1000))
    except KeyError:
        logger.error("Error while filtering airlines")
    else:
        logger.debug("Filtered airlines with less than %s flights", feature_config.get('filter_airlines', 1000))

    # Log transform specified columns
    try:
        features = log_transform(features, feature_config.get('log_transform', []))
    except KeyError:
        logger.error("Error while log transforming columns: %s", feature_config.get('log_transform', []))
    else:
        logger.debug("Log transformed columns: %s", feature_config.get('log_transform', []))

    logger.info("Generated features from cleaned data set")

    return features


def drop_columns(data: pd.DataFrame, columns: list) -> pd.DataFrame:
    """Drop specified columns from the DataFrame."""
    return data.drop(columns, axis=1)

def filter_airlines(data: pd.DataFrame, min_flights: int) -> pd.DataFrame:
    """Drop airlines with less than 'min_flights' flights."""
    try:
        df = data.groupby('airline').filter(lambda x: len(x) > min_flights)
    except TypeError:
        logger.error("The 'min_flights' argument must be an integer")
        raise
    else:
        return df

def log_transform(data: pd.DataFrame, columns: list) -> pd.DataFrame:
    """Apply log transformation to specified columns."""

    for column in columns:
        data[column] = np.log(data[column])

    return data