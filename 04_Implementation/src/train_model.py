# Libraries 
import yaml
from pathlib import Path
import logging
import numpy as np
import pandas as pd
from typing import Tuple
import pickle

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer


# Set logger
logger = logging.getLogger(__name__)

def train_and_evaluate(features: pd.DataFrame, config: dict) -> Tuple[pd.DataFrame, pd.DataFrame, dict, dict]:
    """
    Trains and evaluates models.

    Args:
        features (pandas.DataFrame): Data set with features.
        config (dict): Configuration dictionary for training and evaluation.

    Returns:
        dict: Evaluation results.
        dict: Details of trained models.
    """
        
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
    
    logger.debug("Data split into training and test sets with test size %s", split_config.get("test_size", 0.2))

    for name, model in models.items():
        best_model = train_model(preprocessor, model, X_train, y_train)
        y_pred = best_model.predict(X_test)
        model_results = calculate_metrics(y_test, y_pred)

        trained_models[name] = best_model
        results[name] = model_results
        logger.info("Model %s trained and evaluated", name)

    # Add target variable to training and test sets
    train: pd.DataFrame = pd.concat([X_train, y_train], axis=1)
    test: pd.DataFrame = pd.concat([X_test, y_test], axis=1)

    return train, test, results, trained_models


def define_preprocessor(config: dict) -> ColumnTransformer:
    """
    Defines a preprocessor for the model.

    Args:
        config (dict): Configuration dictionary for training and evaluation.

    Returns:
        sklearn ColumnTransformer: Preprocessor for the model.
    """

    # Define preprocessor
    preprocessor = ColumnTransformer(transformers=[
        ('num', StandardScaler(), config.get('numerical_features', [])),
        ('cat', OneHotEncoder(handle_unknown='ignore'), config.get('categorical_features', []))
    ])

    logger.debug("Preprocessor defined")
    return preprocessor


def define_models(config: dict) -> dict:
    """
    Defines models for the pipeline.

    Args:
        config (dict): Configuration dictionary for training and evaluation.

    Returns:
        dict: Dictionary of model instances.
    """

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

    logger.debug("Models defined")
    return models


def train_model(preprocessor, model, X_train, y_train):
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
    mse = float(mean_squared_error(y_test, y_pred))
    mae = float(mean_absolute_error(y_test, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_test, y_pred))

    return {'MSE': mse, 'MAE': mae, 'RMSE': rmse, 'R2': r2}


def save_results(results: dict, save_path: Path):
    """
    Saves evaluation results to a yaml file.

    Args:
        results (dict): Evaluation results.
        save_path (Path): Path to save the results.

    Returns:
        None
    """

    try:
        with open(save_path, 'w') as file:
            yaml.dump(results, file)
    except yaml.YAMLError:
        logger.error("Error while saving results to %s", save_path)
    else:
        logger.info("Results saved to %s", save_path)

# Not being used right now, but could be useful in the future
def save_best_model(results: dict, trained_models: dict, file_path: Path) -> None:
    """
    Saves the best model to a pickle file.

    Args:
        results (dict): Evaluation results.
        trained_models (dict): Dictionary of trained model instances.
        file_path (Path): Path to save the model.

    Returns:
        None
    """
    
    # Find the name of the model with the highest R2 score
    best_model_name = max(results, key=lambda model: results[model]['R2'])

    logger.info("Best model: %s", best_model_name)
    
    # Get the best model
    best_model = trained_models[best_model_name]
    
    # Save the best model as a pickle file
    with open(file_path, 'wb') as file:
        try:
            pickle.dump(best_model, file)
        except pickle.PicklingError:
            logger.error("Error while saving model to %s", file_path)
        except FileNotFoundError:
            logger.error("Error while saving model to %s", file_path)
        except Exception as e:
            logger.error("Error while saving model to %s", file_path)
        else:
            logger.info("Model saved to %s", file_path)


def save_all_models(trained_models: dict, file_path: Path) -> None:
    """
    Saves all trained models to individual pickle files.

    Args:
        trained_models (dict): Dictionary of trained model instances.
        file_path (Path): Directory path to save the models.

    Returns:
        None
    """
    
    # Iterate over all models
    for model_name, model in trained_models.items():

        # Define specific path for each model
        specific_file_path = file_path / f"{model_name}.pkl"
        
        logger.info("Saving model: %s", model_name)
        
        # Save the model as a pickle file
        with open(specific_file_path, 'wb') as file:
            try:
                pickle.dump(model, file)
            except pickle.PicklingError:
                logger.error("Error while saving model to %s", specific_file_path)
            except FileNotFoundError:
                logger.error("Error while saving model to %s", specific_file_path)
            except Exception as e:
                logger.error("Error while saving model to %s", specific_file_path)
            else:
                logger.info("Model saved to %s", specific_file_path)
