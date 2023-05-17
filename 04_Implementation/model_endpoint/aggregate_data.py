import pandas as pd
import numpy as np

def get_flight_number(df: pd.DataFrame, airline: str) -> list:
    """Get all the possible flight number from the database, given the airline

    Args:
        df (pd.DataFrame): Clean data in pandas dataframe format
        airline (str): The selected airline

    Returns:
        list: List of possible flight numbers for the selected airline
    """
    df = df[df["airline"] == airline]
    lst = list(df["flight"].unique())
    
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
    df_sliced = df[(df["airline"] == airline)
                & (df["origin"] == origin)
                & (df["destination"] == destination)]
    
    avg_duration = df_sliced["duration"].mean()
    
    # if no data, we use simple imputation method
    if avg_duration is np.nan:
        return df["duration"].mean()
    
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
    df_sliced = df[(df["airline"] == airline)
                & (df["origin"] == origin)
                & (df["destination"] == destination)
                & (df["departure_time"] == depart)]
    
    # if no data, we use simple imputation method
    if df_sliced.empty:
        df_sliced = df[(df["origin"] == origin)
                    & (df["destination"] == destination)
                    & (df["departure_time"] == depart)]
        
    return df_sliced["arrival_time"].value_counts().index[0]
