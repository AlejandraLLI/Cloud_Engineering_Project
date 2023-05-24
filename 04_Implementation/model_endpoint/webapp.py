import streamlit as st
st.set_page_config(layout="wide")
from PIL import Image
from aggregate_data import get_flight_number, get_avg_duration, get_arrival
import requests
import json
import pandas as pd

# -------TITLE----------
st.markdown("""<h1 style='text-align: center; color: white;'>
            How much do I need to pay for the flight?</h1>""",
            unsafe_allow_html=True)
with st.columns(3)[1]:
    image = Image.open("plane.jpg")
    st.image(image)

# -------INPUTS--------

# airline
airline = st.selectbox(
    "What's the airline?",
    ("Air India", "AirAsia", "GO FIRST", "Indigo",
     "Spicejet", "StarAir", "Trujet", "Vistra")
)

# seat type
st.write("Which seat do you want?")
col1, col2 = st.columns(2)
with col1:
    if st.button("Economy", use_container_width=True):
        st.session_state["seat"] = "Economy"
with col2:
    if st.button("Business", use_container_width=True):
        st.session_state["seat"] = "Business"

# depart and arrive time
departure_time = st.selectbox(
    "What time do you depart?",
    ("Early_Morning", "Morning", "Afternoon",
     "Evening", "Night", "Late_Night")
)

# origin and destination
origin = st.selectbox(
    "What's your origin?",
    ("Bangalore", "Chennai", "Delhi",
     "Hyderabad", "Kolkata", "Mumbai")
)
destination = st.selectbox(
    "What's your destination?",
    ("Bangalore", "Chennai", "Delhi",
     "Hyderabad", "Kolkata", "Mumbai"),
    index=1
)

# number of stops
st.write("How many stops do you have?")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("0", use_container_width=True):
        st.session_state["stop"] = 0
with col2:
    if st.button("1", use_container_width=True):
        st.session_state["stop"] = 1    
with col3:
    if st.button("2", use_container_width=True):
        st.session_state["stop"] = 2
        
# --------VALIDATE INPUT------------
def validate_input():
    warnings = []
    # seat
    if "seat" not in st.session_state:
        warnings.append("Please select a seat type.")
    # origin and destination should be different
    if origin == destination:
        warnings.append("Origin and destination cities must be different.")
    # stop
    if "stop" not in st.session_state:
        warnings.append("Please specify how many stops is your travel.")
    # combine warnings
    if warnings:
        for warning in warnings:
            st.warning(warning)
        return False
    return True
    

# --------PREDICTION-------------

# read data to interpolate some inputs
df = pd.read_csv("../../02_Data/clean_data.csv")

# model type
model_type = st.sidebar.selectbox("Which model do you want to use?",
                                 ("XGBoost", "Random Forest", "Linear Regression"))

model_dict = {
    "XGBoost": "xgboost",
    "Random Forest": "random_forest",
    "Linear Regression": "linear"
}

def predict():
    # validate input before making prediction
    if validate_input():
        url = "http://127.0.0.1:5000/predict"
        
        arrival_time = get_arrival(df, airline, origin, destination, departure_time)
        duration = get_avg_duration(df, airline, origin, destination)
        flight_numbers = get_flight_number(df, airline)
        
        try:
            prices = []
            for flight_number in flight_numbers:
                input_data = {
                    "Data": {
                    'airline': airline,
                    'flight': flight_number,
                    'class': st.session_state["seat"],
                    'departure_time': departure_time,
                    'origin': origin,
                    'duration': duration,
                    'stops': st.session_state["stop"],
                    'arrival_time': arrival_time,
                    'destination': destination
                    }, "Model": model_dict[model_type]
                    }
                response = requests.post(url, json=input_data)
                response.raise_for_status()  # Check if the request was successful
                try:
                    prices.append(float(json.loads(response.text)['prediction']))
                except json.JSONDecodeError:
                    st.error("Error: Invalid JSON response received.")
                    st.error("Response text:", response.text)
                except KeyError:
                    st.error("Error: 'prediction' key not found in the JSON response.")
                    st.error("Response text:", response.text)
            predicted_price = sum(prices) / len(prices)
            st.success(f"Predicted Price: {round(predicted_price, 2)} Rupees")
        except requests.exceptions.RequestException as e:
            st.error("Error: Request failed.")
            raise e
    else:
        pass

st.button("Predict", on_click=predict)