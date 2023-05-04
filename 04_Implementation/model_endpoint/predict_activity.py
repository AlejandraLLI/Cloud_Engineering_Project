# Import libraries
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import keras
import joblib
from flask import Flask, request, jsonify

# Create a Flask app instance
app = Flask(__name__)

# # Get model path and load model
model_path = 'LSTM.h5'
model = keras.models.load_model(model_path)

# Load encoder
encoder = LabelEncoder()
encoder_filename = "label_encoder.npy"
encoder.classes_ = np.load(encoder_filename, allow_pickle=True)

# Load scalar
scaler_filename = "scalar.save"
scaler = joblib.load(scaler_filename) 

# Set num categories
n_categories = 6

# Define columns to normalize
normalize_columns = [
    'attitude.roll', 
    'attitude.pitch', 
    'attitude.yaw',
    'gravity.x', 
    'gravity.y', 
    'gravity.z',
    'rotationRate.x', 
    'rotationRate.y', 
    'rotationRate.z',
    'userAcceleration.x', 
    'userAcceleration.y', 
    'userAcceleration.z',
    # 'attitude', 
    # 'gravity', 
    # 'rotationRate', 
    # 'userAcceleration',
    # 'weight', 
    # 'height', 
    # 'age'
]

# Store the number of features and number of timesteps back
n_features = len(normalize_columns)
n_timesteps = 50

# Buffer to store the most recent samples
data_buffer = np.zeros((n_timesteps, n_features))

def transform_data(sample, scaler, data_buffer, n_timesteps, n_features):
    # Normalize the sample while keeping it as a DataFrame
    normalized_sample = pd.DataFrame(scaler.transform(sample), columns=sample.columns)
    
    # Update the data buffer
    data_buffer[:-1] = data_buffer[1:]
    data_buffer[-1] = normalized_sample.values
    
    # Reshape the buffer to be compatible with the LSTM model
    X = data_buffer.reshape(1, n_timesteps, n_features)
    
    return X


## Flask App ##

# Define the API endpoint and request method
@app.route('/predict', methods=['POST'])
def predict():
    # Get the incoming data from the request
    data = request.get_json()

    # Convert the data into a DataFrame
    sample = pd.DataFrame(data, columns=normalize_columns)

    # Transform the data and get the prediction
    X = transform_data(sample, scaler, data_buffer, n_timesteps, n_features)
    prediction = model.predict(X, verbose=False)

    # Get the class label for the prediction
    class_label = encoder.inverse_transform(prediction.argmax(axis=-1))[0]

    # Return the prediction as JSON
    return jsonify({'prediction': class_label})

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)