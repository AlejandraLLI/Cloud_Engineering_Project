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



def train_and_evaluate(features: pd.DataFrame, config: dict) -> Tuple[dict, dict]:
        

    # Define preprocessor and models for Pipeline
    preprocessor: ColumnTransformer = define_preprocessor(config)
    models: dict = define_models(config)

    # Separate features and target
    X: pd.DataFrame = features.drop('price', axis=1)
    y: pd.Series = features['price']

    # Initialize dictionaries for storing results and trained models
    results: dict = {}
    trained_models: dict = {}

    # Split data into training and test sets
    split_config = config.get('train_test_split', {})
    X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                                        test_size=split_config.get("test_size", 0.2),
                                                        random_state=split_config.get("random_state", 42))

    for name, (model, params) in models.items():
        best_model = train_model(preprocessor, model, params, X_train, y_train)
        y_pred = best_model.predict(X_test)
        model_results = calculate_metrics(y_test, y_pred)

        trained_models[name] = best_model
        results[name] = model_results

    return results, trained_models


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


def train_model(preprocessor, model, params, X_train, y_train):
    """
    Trains a model with or without hyperparameter tuning.

    Args:
        preprocessor (sklearn ColumnTransformer): Preprocessor for the model.
        model (sklearn model): The model to train.
        params (dict): Hyperparameters for the model.
        X_train (pandas.DataFrame): Training features.
        y_train (pandas.Series): Training target variable.

    Returns:
        sklearn model: The trained model.
    """
    pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('model', model)])

    if params:
        grid_search = GridSearchCV(pipeline, param_grid=params, scoring='neg_mean_squared_error', cv=3, n_jobs=-1)
        grid_search.fit(X_train, y_train)
        best_model = grid_search.best_estimator_
    else:
        best_model = pipeline
        best_model.fit(X_train, y_train)

    return best_model

def calculate_metrics(y_test, y_pred):
    """
    Calculates evaluation metrics.

    Args:
        y_test (pandas.Series): Test target variable.
        y_pred (pandas.Series): Predicted target variable.

    Returns:
        dict: Evaluation metrics.
    """
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)

    return {'MSE': mse, 'MAE': mae, 'RMSE': rmse, 'R2': r2}



