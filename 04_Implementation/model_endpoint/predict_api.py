# Import libraries
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from xgboost import XGBRegressor
from flask import Flask, request, jsonify
import json
import joblib

# Create a Flask app instance
app = Flask(__name__)

# Load the trained XGBoost model
model_path = 'xgboost_model.pkl'

# Load the model
model = joblib.load(model_path)

# Load preprocessor
preprocessor_path = 'preprocessor.pkl'
preprocessor = joblib.load(preprocessor_path)

# Flask App

# Define the API endpoint and request method
@app.route('/predict', methods=['POST'])
def predict():
    # Get JSON data
    data = request.get_json()

    # Convert JSON data to DataFrame
    X = pd.DataFrame(data, index=[0])

    try:
        # Manually apply preprocessing steps
        preprocessor = model.named_steps['preprocessor']
        estimator = model.named_steps['model']
        X_processed = preprocessor.transform(X)
        
        # Predict using the estimator
        prediction = estimator.predict(X_processed)
        response = {
            'prediction': float(np.exp(prediction[0]))  # Revert the log transformation and convert to float
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
