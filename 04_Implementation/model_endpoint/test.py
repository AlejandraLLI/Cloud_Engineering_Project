import pandas as pd
import requests
import json

# Read the validation dataset
validation_data = pd.read_csv(r"C:\Users\Sam\Desktop\NW Work\DATA\CDL\validation_motionsense_lstm.csv")

# Define columns to pass into api
api_columns = [
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

validation_data = validation_data[api_columns]

# Define the API endpoint URL
api_url = "http://localhost:5000/predict"

# Num rows to test
num_test_rows = 100

# Loop through the validation dataset and send requests to the API
results = []
for idx, row in validation_data.iloc[0:num_test_rows, :].iterrows():
    # Convert the row to a dictionary
    data = [row.to_dict()]
    
    # Send a POST request to the API with the data
    response = requests.post(api_url, json=data)
    
    # Parse the JSON response and store the prediction
    prediction = json.loads(response.text)['prediction']
    results.append(prediction)
    print(prediction)

# Convert the results to a DataFrame
results_df = pd.DataFrame(results, columns=['prediction'])

# Save the results to a CSV file (optional)
results_df.to_csv('api_results.csv', index=False)

# Print the results
print(results_df)
