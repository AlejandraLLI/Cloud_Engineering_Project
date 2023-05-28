"""
This module provides an API endpoint for making predictions using a trained model.
"""

import logging
from io import BytesIO

import pandas as pd
import numpy as np
import joblib
import boto3
from flask import Flask, request, jsonify

from botocore.exceptions import BotoCoreError, NoCredentialsError
from sklearn.exceptions import NotFittedError
from joblib import numpy_pickle


# Create a Flask app instance
app = Flask(__name__)

# Set up logging configuration
logging.basicConfig(
    filename="app.log",
    filemode="w",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)

# Set up AWS S3 client
s3 = boto3.client("s3")
BUCKET_NAME = "msia423-g7"  # replace with your bucket name
PREFIX = "experiments/"  # replace with your prefix

MODELS = {}  # Dictionary to hold all models


def load_models():
    """Loads all models into memory when Flask app starts"""
    models_list = ["linear_regression", "random_forest", "xgboost"]

    for model_name in models_list:
        try:
            response = s3.get_object(
                Bucket=BUCKET_NAME, Key=f"{PREFIX}{model_name}.pkl"
            )
            try:
                model = joblib.load(BytesIO(response["Body"].read()))
                MODELS[model_name] = model  # Add the model to the MODELS dictionary
                logging.debug("Model %s loaded successfully.", model_name)
            except numpy_pickle.NumpyPicklingError as pickle_error:
                logging.exception("Error occurred during loading the model!")
        except (BotoCoreError, NoCredentialsError) as s3_error:
            logging.exception("Error occurred during getting model from S3!")


# Call the function to load models
load_models()


@app.route("/predict", methods=["POST"])
def predict():
    """Endpoint for making predictions using a trained model"""
    # Retrieve JSON data from the request
    data = request.get_json()
    logging.debug("Received JSON data: %s", data)

    # Verify that 'Data' and 'Model' keys are present in the request data
    if "Data" not in data or "Model" not in data:
        return (
            jsonify({"error": "Data and Model keys are required in the request body"}),
            400,
        )

    # Retrieve model name from data
    model_name = data["Model"]
    logging.debug("Model name: %s", model_name)

    # Retrieve the model from memory
    try:
        model = MODELS[model_name]
        preprocessor = model.named_steps["preprocessor"]
        estimator = model.named_steps["model"]
        logging.debug("Model and preprocessor retrieved from memory successfully.")
    except KeyError:
        return jsonify({"error": f"Model {model_name} not found in memory"}), 400

    # Convert JSON data into a pandas DataFrame
    dataframe = pd.DataFrame(data["Data"], index=[0])
    logging.debug("Converted JSON data to DataFrame.")

    # Apply preprocessor to input data
    processed_data = preprocessor.transform(dataframe)
    logging.debug("Preprocessing applied successfully.")

    try:
        # Make a prediction using the trained model
        prediction = estimator.predict(processed_data)
        logging.debug("Prediction made successfully.")
    except NotFittedError as prediction_error:
        logging.exception("Error occurred during prediction!")
        return (
            jsonify({"error": f"Error during prediction: {str(prediction_error)}"}),
            500,
        )

    # Create a response containing the prediction
    try:
        response = {
            "prediction": float(
                np.exp(prediction[0])
            )  # Revert the log transformation and convert to float
        }
        return jsonify(response)
    except TypeError as error:
        logging.exception("Error occurred while creating response!")
        return jsonify({"error": f"Error during response creation: {str(error)}"}), 500


# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
