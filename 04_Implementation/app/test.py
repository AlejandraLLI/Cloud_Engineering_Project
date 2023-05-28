import requests
import json

# Define the API endpoint
url = "http://3.22.68.161:5000/predict"

# Define sample input data
input_data = {
    "Data": {
        "airline": "Vistara",
        "flight": "UK-836",
        "class": "Business",
        "departure_time": "Morning",
        "origin": "Chennai",
        "duration": 6.25,
        "stops": 1,
        "arrival_time": "Evening",
        "destination": "Bangalore"
    },
    
    "Model": "linear_regression"
}

try:
    response = requests.post(url, json=input_data)
    response.raise_for_status()  # Check if the request was successful
    try:
        predicted_price = json.loads(response.text)['prediction']
    except json.JSONDecodeError:
        print("Error: Invalid JSON response received.")
        print("Response text:", response.text)
    except KeyError:
        print("Error: 'prediction' key not found in the JSON response.")
        print("Response text:", response.text)
    else:
        print("Predicted price:", predicted_price)
except requests.exceptions.RequestException as e:
    print("Error: Request failed.")
    print(e)
