# Libraries 
import numpy as np
import pandas as pd
from pathlib import Path


def generate_features(clean_data: pd.DataFrame, feature_config: dict) -> pd.DataFrame:

    features = df_clean.copy()

    # Drop column book_date
    features.drop(['book_date'], axis=1, inplace=True)

    # Drop airlines with less than 1000 flights
    features = features.groupby('airline').filter(lambda x: len(x) > 1000)

    # Log price
    features['price'] = np.log(features['price'])

    return features