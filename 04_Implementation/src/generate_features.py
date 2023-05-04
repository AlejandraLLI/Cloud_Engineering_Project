# Libraries 
import numpy as np
import pandas as pd
import zipfile
import time
import re
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

def get_duration(text: str) -> float:
    """
    DOCUMENT THIS FUNCTION
    """
    pattern = re.match(r'[0-9]+\.[0-9]{1,2}h m', text)
    if(pattern != None):
        # Extract hours
        hours = re.search(r'^[0-9]+\.', text)
        hours = int(hours.group().replace('.',''))
        
        # Extract minutes
        minutes = re.search(r'\.[0-9]{1,2}h', text)
        minutes = float(minutes.group().replace('h', ''))*60
        minutes = int(round(minutes))
    else:
        # Extract hours
        hours = re.search(r'^[0-9]+h', text)
        hours = int(hours.group().replace('h',''))
        # Extract minutes
        minutes = re.search(r'[0-5][0-9]m', text)
        minutes = int(minutes.group().replace('m', ''))
    
    # Calculate duration in hours
    duration = round(hours + minutes/60,2)
    
    # Function output
    return duration


def get_stops(text: str, pattern: str, stop_dict: dict) -> int:
    """
    DOCUMENT THIS FUNCTION
    """
    # Regex for number of stops 
    pattern = re.search(pattern, text)
    stops = pattern.group()
    
    for current_cat, new_cat in stop_dict.items(): 
        if stops == current_cat:
            n_stops = new_cat
    
    # Function output
    return n_stops
    
def bucket_hours(time: str, hour_buckets: dict) -> str:
    """
    DOCUMENT THIS FUNCTION
    """
    # Regex for hour of the day
    pattern = re.search(r'^[0-2][0-9]\:', time)
    hour = int(pattern.group().replace(":",""))
    
    # Check bucket according to configuration
    for block_name, limits in hour_buckets.items(): 
        if (hour >= limits["min"] and hour < limits["max"]):
            bucket = block_name
    
    return(bucket)
    

def clean_data(df: pd.DataFrame, clean_config:dict):
    """
    DOCUMENT THIS FUNCTION
    """
    df_clean = df.copy()

    # Rename columns 
    df_clean.rename(columns = clean_config["rename_cols"], inplace=True)
   
    # Concatenate columns
    for new_col, concat_cols in clean_config["concat_cols"].items():
        # Get columns to multiply from dict
        col1 = concat_cols["col1"]
        col2 = concat_cols["col2"]

        # Create new feature by concatenating columns 
        df_clean[new_col] = df[col1] + "-" + df[col2].astype(concat_cols["col_type"])

    # Bucket time
    for new_col, bucket_col in clean_config["bucket_time_cols"].items():
        df_clean[new_col] = df[bucket_col].apply(lambda x: bucket_hours(x, clean_config["bucket_hours"]))

    # Convert time take to hours 
    for new_col, time_col in clean_config["time_to_hours"].items():
        df_clean[new_col] = df[time_col].apply(lambda x: get_duration(x))

    # Get number of stops 
    for new_col, stop_col in clean_config["stops_cols"].items():
        df_clean[new_col] = df[stop_col].apply(lambda x: get_stops(x, **clean_config["get_stops"]))

    # Convert prices to numeric
    for price_col, pattern_dict in clean_config["price_cols"].items():
        # Create new feature by mulitplying columns 
        df_clean[price_col] = df[price_col].str.replace(pattern_dict["pattern"],
                                                         pattern_dict["replacement"]).astype(int)

    # Select features
    df_clean = df_clean[clean_config["selected_features"]]

    # Function output
    return(df_clean)