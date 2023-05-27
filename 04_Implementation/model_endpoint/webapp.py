import json
import logging.config
import argparse
import os
from io import StringIO
import streamlit as st
from PIL import Image
from aggregate_data import get_flight_number, get_avg_duration, get_arrival
import requests
import pandas as pd
import yaml
import boto3
from boto3.exceptions import Boto3Error

st.set_page_config(layout="wide")

# read configuration file
with open("04_Implementation/model_endpoint/config/logging/webapp_log.yaml", "r") as f:
    log_cfg = yaml.safe_load(f.read())
logging.config.dictConfig(log_cfg)
logger = logging.getLogger("webapp")

parser = argparse.ArgumentParser(
    description="Acquire, clean, and create features from clouds data"
)
parser.add_argument(
    "--config", default="04_Implementation/model_endpoint/config/webapp.yaml",
    help="Path to configuration file"
)
args = parser.parse_args()

# Load configuration file for parameters and run config
with open(args.config, "r") as f:
    try:
        config = yaml.load(f, Loader=yaml.FullLoader)
    except yaml.error.YAMLError as e:
        logger.error("Error while loading configuration from %s", args.config)
    else:
        logger.info("Configuration file loaded from %s", args.config)

try:
    # Connect to S3
    session = boto3.Session()
    logger.info("Successfully connected to boto3 session")
except Boto3Error as e:
    logger.error("Failed to connect to boto3 session: %s", str(e))
    raise e

# environment variables for aws
BUCKET_NAME = os.getenv("BUCKET_NAME", config["aws"]["bucket_name"])
PREFIX = os.getenv("PREFIX", config["aws"]["prefix"])

# -------TITLE----------
st.markdown(f"""<h1 style='text-align: center; color: white;'>
            {config["message"]["header"]}</h1>""",
            unsafe_allow_html=True)
with st.columns(3)[1]:
    image = Image.open(config["path"]["image_path"])
    st.image(image)

# -------INPUTS--------

# airline
airline = st.selectbox(
    config["message"]["airline_input"],
    config["inputs"]["airline"]
)
logger.info("User selected %s airline", airline)

# seat type
st.write(config["message"]["seat_input"])
col1, col2 = st.columns(2)
with col1:
    if st.button("Economy", use_container_width=True):
        st.session_state["seat"] = "economy"
        logger.info("User selected %s seat", st.session_state["seat"])
with col2:
    if st.button("Business", use_container_width=True):
        st.session_state["seat"] = "business"
        logger.info("User selected %s seat", st.session_state["seat"])

# depart and arrive time
departure_time = st.selectbox(
    config["message"]["depart_time_input"],
    config["inputs"]["depart_time"]
)
logger.info("User selected %s departure time", departure_time)

# origin and destination
origin = st.selectbox(
    config["message"]["origin_input"],
    config["inputs"]["origin"]
)
logger.info("User selected %s as a flight origin", origin)

destination = st.selectbox(
    config["message"]["destination_input"],
    config["inputs"]["destination"],
    index=1
)
logger.info("User selected %s as a flight destination", destination)

# number of stops
st.write(config["message"]["stop_input"])
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("0", use_container_width=True):
        st.session_state["stop"] = 0
        logger.info("User selected %s stop", st.session_state["stop"])
with col2:
    if st.button("1", use_container_width=True):
        st.session_state["stop"] = 1
        logger.info("User selected %s stop", st.session_state["stop"])
with col3:
    if st.button("2", use_container_width=True):
        st.session_state["stop"] = 2
        logger.info("User selected %s stops", st.session_state["stop"])

# --------VALIDATE INPUT------------
def validate_input():
    warnings = []
    # seat
    if "seat" not in st.session_state:
        warnings.append("Please select a seat type.")
        logger.info("User did not select seat type")
    # origin and destination should be different
    if origin == destination:
        warnings.append("Origin and destination cities must be different.")
        logger.info("User gets warning on having the same city for origin and destination")
    # stop
    if "stop" not in st.session_state:
        warnings.append("Please specify how many stops is your travel.")
        logger.info("User did not select number of stops")
    # combine warnings
    if warnings:
        for warning in warnings:
            st.warning(warning)
        return False
    return True


# --------PREDICTION-------------

# read data to interpolate some inputs
@st.cache_data
def load_data(_session: boto3.Session, bucket_name: str, prefix: str) -> pd.DataFrame:
    """Load original cloud csv data from S3 bucket to create min and max for sliders.

    Args:
        _session (boto3.Session): boto3 session to connect to AWS resources (S3 in this case)
        bucket_name (str): S3 bucket name that we want to access
        prefix (str): S3 key prefix for the reseource we want to access

    Returns:
        pd.DataFrame: csv data in pandas dataframe format
    """
    try:
        s3_boto3 = _session.resource("s3")
        # data are the same in both predix -- choosing rf prefix
        obj = s3_boto3.Object(bucket_name, key=f"{prefix}/clean_data.csv")
        df = pd.read_csv(StringIO(obj.get()["Body"].read().decode("utf-8")))
        logger.info("Successfully retrieved data from S3 bucket.")
        return df
    except Boto3Error as e:
        logger.error("Failed to retrieve data from S3 bucket: %s", str(e))
        raise e

df = load_data(session, BUCKET_NAME, PREFIX)

# model type
model_type = st.sidebar.selectbox(config["message"]["model_input"],
                                 ("XGBoost", "Random Forest", "Linear Regression"))

model_dict = {
    "XGBoost": "xgboost",
    "Random Forest": "random_forest",
    "Linear Regression": "linear"
}

def predict():
    # validate input before making prediction
    if validate_input():
        url = config["path"]["flask_url"]

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
                logger.info("Successfully call API")
                try:
                    prices.append(float(json.loads(response.text)['prediction']))
                except json.JSONDecodeError:
                    st.error("Error: Invalid JSON response received.")
                    st.error("Response text:", response.text)
                    logger.error("Error: Invalid JSON response received.")
                except KeyError:
                    st.error("Error: 'prediction' key not found in the JSON response.")
                    st.error("Response text:", response.text)
                    logger.error("Error: 'prediction' key not found in the JSON response.")
            predicted_price = sum(prices) / len(prices)
            st.success(f"Predicted Price: {round(predicted_price, 2)} Rupees")
            logger.info("Show prediction price: %f Rupees", round(predicted_price, 2))
        except requests.exceptions.RequestException as e:
            st.error("Error: Request failed.")
            logger.error("Error: Request failed.")
            raise e
    else:
        pass

st.button("Predict", on_click=predict)
