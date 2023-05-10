# Libraries 
import numpy as np
import pandas as pd


from typing import Tuple

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer







def define_preprocessor(config: dict) -> ColumnTransformer:

    # Define preprocessor
    preprocessor = ColumnTransformer(transformers=[
        ('num', StandardScaler(), config.get('numerical_features', [])),
        ('cat', OneHotEncoder(handle_unknown='ignore'), config.get('categorical_features', []))
    ])

    return preprocessor


def define_models(config: dict) -> dict:

    # Define mapping between model names and model classes
    models_mapping: dict = {
                            'LinearRegression': LinearRegression,
                            'RandomForestRegressor': RandomForestRegressor,
                            'XGBRegressor': XGBRegressor
                            }   

    # Initialize dictionary for storing model instances
    models: dict = {}

    # Loop through models in config file and create model instances
    for model_name, model_info in config['models'].items():
        ModelClass = models_mapping[model_info['class']]
        model_instance = ModelClass(**model_info['parameters'])
        models[model_name] = model_instance

    return models
