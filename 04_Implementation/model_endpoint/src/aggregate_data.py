import pandas as pd
import numpy as np
import logging
import yaml

with open("04_Implementation/model_endpoint/config/webapp.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

logger = logger = logging.getLogger("aggregate_data")

def get_flight_number(df: pd.DataFrame, airline: str) -> list:
    """Get all the possible flight number from the database, given the airline

    Args:
        df (pd.DataFrame): Clean data in pandas dataframe format
        airline (str): The selected airline

    Returns:
        list: List of possible flight numbers for the selected airline
    """
    
    if airline not in config["inputs"]["airline"]:
        logger.error("The selected airline is not in our dataset.")
        raise ValueError("The selected airline is not in our dataset.")
    
    df = df[df["airline"] == airline]
    lst = list(df["flight"].unique())
    logger.info("Successfully retrieved all possible flight number for %s airline", airline)
    
    return lst

def get_avg_duration(df: pd.DataFrame, airline: str, origin: str, destination: str) -> float:
    """Given airline, origin, and destination, find the average duration of the flight

    Args:
        df (pd.DataFrame): Clean data in pandas dataframe format
        airline (str): The selected airline
        origin (str): The selected origin city
        destination (str): The selected destination city

    Returns:
        float: Average duration
    """
    
    if airline not in config["inputs"]["airline"]:
        logger.error("The selected airline is not in our dataset.")
        raise ValueError("The selected airline is not in our dataset.")
    
    if origin not in config["inputs"]["origin"]:
        logger.error("The selected origin is not in our dataset.")
        raise ValueError("The selected origin is not in our dataset.")
    
    if destination not in config["inputs"]["destination"]:
        logger.error("The selected destination is not in our dataset.")
        raise ValueError("The selected destination is not in our dataset.")
    
    df_sliced = df[(df["airline"] == airline)
                & (df["origin"] == origin)
                & (df["destination"] == destination)]
    
    avg_duration = df_sliced["duration"].mean()
    
    # if no data, we use simple imputation method
    if avg_duration is np.nan:
        logger.info("Get average duration of the entire data (no data from the specific inputs)")
        return df["duration"].mean()

    logger.info("Get average duration of the %s airline, %s origin, and %s destination",
                airline, origin, destination)
    
    return avg_duration

def get_arrival(df: pd.DataFrame, airline: str, origin: str, destination: str, depart: str) -> str:
    """Given airline, origin, destination, and departure time, find the most likely arrival time (find mode)

    Args:
        df (pd.DataFrame): Clean data in pandas dataframe format
        airline (str): The selected airline
        origin (str): The selected origin city
        destination (str): The selected destination city
        depart (str): The selected departure time

    Returns:
        str: The most likely arrival time
    """
    
    if airline not in config["inputs"]["airline"]:
        logger.error("The selected airline is not in our dataset.")
        raise ValueError("The selected airline is not in our dataset.")
    
    if origin not in config["inputs"]["origin"]:
        logger.error("The selected origin is not in our dataset.")
        raise ValueError("The selected origin is not in our dataset.")
    
    if destination not in config["inputs"]["destination"]:
        logger.error("The selected destination is not in our dataset.")
        raise ValueError("The selected destination is not in our dataset.")
    
    if depart not in config["inputs"]["depart_time"]:
        logger.error("The selected departure time is not in our dataset.")
        raise ValueError("The selected departure time is not in our dataset.")
    
    df_sliced = df[(df["airline"] == airline)
                & (df["origin"] == origin)
                & (df["destination"] == destination)
                & (df["departure_time"] == depart)]

    # if no data, we use simple imputation method
    if df_sliced.empty:
        df_sliced = df[(df["origin"] == origin)
                    & (df["destination"] == destination)
                    & (df["departure_time"] == depart)]
    logger.info("Get most frequent arrival time of the %s airline, %s origin, %s destination, and %s departure time",
                airline, origin, destination, depart)
    
    return df_sliced["arrival_time"].value_counts().index[0]
