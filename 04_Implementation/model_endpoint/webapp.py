import streamlit as st
st.set_page_config(layout="wide")
from PIL import Image
import requests
import json

# -------TITLE----------
st.markdown("""<h1 style='text-align: center; color: white;'>
            How much do I need to pay for the flight?</h1>""",
            unsafe_allow_html=True)
with st.columns(3)[1]:
    image = Image.open("04_Implementation/model_endpoint/plane.jpg")
    st.image(image)

# -------INPUTS--------

# airline
airline = st.selectbox(
    "What's the airline?",
    ("Air India", "AirAsia", "GO FIRST", "Indigo",
     "Spicejet", "StarAir", "Trujet", "Vistra")
)

# flight number
flight_number = st.text_input(
    "What's your flight number?"
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
arrival_time = st.selectbox(
    "What time do you arrive?",
    ("Early_Morning", "Morning", "Afternoon",
     "Evening", "Night", "Late_Night"),
    index=1
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

# flight duration
duration = st.text_input(
    "How long is your flight in hours?"
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
    # TODO: validate flight number
    # seat
    if "seat" not in st.session_state:
        warnings.append("Please select a seat type.")
    # origin and destination should be different
    if origin == destination:
        warnings.append("Origin and destination cities must be different.")
    # duration must exist
    if duration == "":
        warnings.append("Please specify the duration of your flight.")
    # duration must be positive
    elif float(duration) <= 0:
        warnings.append("Duration of you flight must be a positive number.")
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

def predict():
    
    # validate input before making prediction
    if validate_input():
        url = "http://127.0.0.1:5000/predict"
        
        input_data = {
            'airline': airline,
            'flight': flight_number,
            'class': st.session_state["seat"],
            'departure_time': departure_time,
            'origin': origin,
            'duration': duration,
            'stops': st.session_state["stop"],
            'arrival_time': arrival_time,
            'destination': destination
        }
        try:
            response = requests.post(url, json=input_data)
            response.raise_for_status()  # Check if the request was successful
            try:
                predicted_price = json.loads(response.text)['prediction']
            except json.JSONDecodeError:
                st.error("Error: Invalid JSON response received.")
                st.error("Response text:", response.text)
            except KeyError:
                st.error("Error: 'prediction' key not found in the JSON response.")
                st.error("Response text:", response.text)
            else:
                st.success(f"Predicted Price: {round(predicted_price, 2)} Rupees")
        except requests.exceptions.RequestException as e:
            st.error("Error: Request failed.")
            raise e
    else:
        pass

st.button("Predict", on_click=predict)