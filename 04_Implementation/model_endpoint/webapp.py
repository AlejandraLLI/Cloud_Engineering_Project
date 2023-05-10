import streamlit as st
st.set_page_config(layout="wide")
from PIL import Image

st.markdown("<h1 style='text-align: center; color: white;'>How much do I need to pay for the flight?</h1>", unsafe_allow_html=True)

with st.columns(3)[1]:
    image = Image.open("04_Implementation/model_endpoint/plane.jpg")
    st.image(image)
    

airline = st.selectbox(
    "What's the airline?",
    ("Air India", "AirAsia", "GO FIRST", "Indigo",
     "Spicejet", "StarAir", "Trujet", "Vistra")
)
flight_number = st.text_input(
    "What's your flight number?"
)
st.write("Which seat do you want?")
col1, col2 = st.columns(2)
with col1:
    if st.button("Economy", use_container_width=True):
        seat = "Economy"
    
with col2:
    if st.button("Business", use_container_width=True):
        seat = "Business"
        
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

duration = st.text_input(
    "How long is your flight in hours?"
)


st.write("How many stops do you have?")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("0", use_container_width=True):
        stop = 0
    
with col2:
    if st.button("1", use_container_width=True):
        stop = 1
        
with col3:
    if st.button("2", use_container_width=True):
        stop = 2
        
