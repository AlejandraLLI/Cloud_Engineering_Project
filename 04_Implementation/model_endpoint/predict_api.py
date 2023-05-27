# Import necessary libraries
import pandas as pd
import numpy as np
import logging
import joblib
import boto3
from flask import Flask, request, jsonify
from io import BytesIO

# Create a Flask app instance
app = Flask(__name__)

# Set up logging configuration
logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

# Set up AWS S3 client
s3 = boto3.client('s3')
bucket_name = 'msia423-models'  # replace with your bucket name

@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint for making predictions using a trained model"""
    try:
        # Retrieve JSON data from the request
        data = request.get_json()
        logging.debug('Received JSON data: %s', data)

        # Verify that 'Data' and 'Model' keys are present in the request data
        if 'Data' not in data or 'Model' not in data:
            return jsonify({'error': 'Data and Model keys are required in the request body'}), 400

        # Retrieve model name from data
        model_name = data['Model']
        logging.debug('Model name: %s', model_name)

        # Load model based on provided model name
        try:
            response = s3.get_object(Bucket=bucket_name, Key=f'{model_name}_model.pkl')
            model = joblib.load(BytesIO(response['Body'].read()))
            preprocessor = model.named_steps['preprocessor']
            estimator = model.named_steps['model']
            logging.debug('Model and preprocessor loaded successfully.')
        except Exception as e:
            return jsonify({'error': f'Model not found: {model_name}, error: {str(e)}'}), 400

        # Convert JSON data into a pandas DataFrame
        X = pd.DataFrame(data['Data'], index=[0])
        logging.debug('Converted JSON data to DataFrame.')

        # Apply preprocessor to input data
        X_processed = preprocessor.transform(X)
        logging.debug('Preprocessing applied successfully.')

        try:
            # Make a prediction using the trained model
            prediction = estimator.predict(X_processed)
            logging.debug('Prediction made successfully.')
        except Exception as e:
            logging.exception("Error occurred during prediction!")
            return jsonify({'error': 'Error during prediction: {}'.format(e)}), 500

        # Create a response containing the prediction
        response = {
            'prediction': float(np.exp(prediction[0]))  # Revert the log transformation and convert to float
        }

        return jsonify(response)

    except Exception as e:
        logging.exception("Error occurred in prediction!")
        return jsonify({'error': str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
