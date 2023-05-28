"""
This module provides functions for cleaning the raw data by applying different transformations.
"""
# Libraries
import re
import logging
import numpy as np
import pandas as pd


# Set logger
logger = logging.getLogger(__name__)

def get_duration(text: str) -> float:
    """
    Extracts the duration of an event in hours from a given string. The function assumes that 
    the input string contains information about the duration in a format like "5.30h m" or "5h 30m".

    Args:
        text (str): The string containing the duration information.

    Returns:
        float: The duration in hours, rounded to two decimal places.
    """
    pattern = re.match(r'[0-9]+\.[0-9]{1,2}h m', text)
    if pattern is not None:
        # Extract hours
        hours = re.search(r'^[0-9]+\.', text)
        hours = int(hours.group().replace('.', ''))

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
    Extracts the number of stops from a given string using the provided regular expression 
    pattern. The function then uses a provided dictionary to map the extracted string to 
    an integer.

    Args:
        text (str): The string containing the stops information.
        pattern (str): The regular expression pattern to extract the stops information from
                       the text.
        stop_dict (dict): A dictionary mapping the stops information (as string) to integers.

    Returns:
        int: The number of stops as an integer.
    """
    # Regex for number of stops
    try:
        match = re.search(pattern, text)
        stops = match.group()
    except AttributeError:
        logger.debug('The input string "%s" does not contain valid stops info. Returning NA', text)
        return np.nan

    for current_cat, new_cat in stop_dict.items():
        if stops == current_cat:
            n_stops = new_cat

    # Function output
    return n_stops


def bucket_hours(time: str, hour_buckets: dict) -> str:
    """
    Maps a given time to a specific hour bucket. The function uses a provided dictionary to map
    each hour to a specific bucket.

    Args:
        time (str): The string containing the time information.
        hour_buckets (dict): A dictionary mapping each hour to a specific bucket.

    Returns:
        str: The name of the bucket to which the hour of the provided time belongs.
    """
    # Regex for hour of the day
    pattern = re.search(r'^[0-2][0-9]\:', time)
    hour = int(pattern.group().replace(":",""))

    # Check bucket according to configuration
    for block_name, limits in hour_buckets.items():
        if limits["min"] <= hour < limits["max"]:
            bucket = block_name

    return bucket


def clean_data(raw_data: pd.DataFrame, clean_config: dict) -> pd.DataFrame:
    """
    The function downloads a raw data file from an S3 bucket, cleans and transforms the data
    according to the provided configuration, and returns a cleaned pandas DataFrame.

    Args:
        raw_data (pd.DataFrame): A pandas dataframe with the raw data to be cleaned
        clean_config (dict): Configuration for cleaning and transforming the data. 
        Should have the following keys:
            - "rename_cols": A dictionary mapping old column names to new ones.
            - "concat_cols": A dictionary specifying pairs of columns to concatenate.
            - "bucket_time_cols": A dictionary specifying columns to be bucketed into time blocks.
            - "bucket_hours": A dictionary specifying the start and end hours for each time block.
            - "time_to_hours": A dictionary specifying columns to convert from time to hours.
            - "stops_cols": A dictionary specifying columns with number of stops information.
            - "get_stops": A dictionary specifying the pattern to match in the stops column and a 
                           dictionary to map the current stop categories to new categories.
            - "price_cols": A dictionary specifying columns with price information and their 
                            corresponding pattern to remove and its replacement before converting
                            to integer.
            - "selected_features": A list of column names to include in the final cleaned DataFrame.

    Returns:
        A cleaned pandas DataFrame.
    """
    # Create clean dataframe
    df_clean = raw_data.copy()

    # Rename columns
    df_clean.rename(columns = clean_config["rename_cols"], inplace=True)
    logger.debug("Columns have been renamed.")

    # Concatenate columns
    for new_col, concat_cols in clean_config["concat_cols"].items():
        # Get columns to multiply from dict
        col1 = concat_cols["col1"]
        col2 = concat_cols["col2"]

        # Create new feature by concatenating columns
        df_clean[new_col] = raw_data[col1] + "-" + raw_data[col2].astype(concat_cols["col_type"])

        # debug info
        logger.debug("New column %s created conatenating columns %s and %s", new_col, col1, col2)


    # Bucket time
    for new_col, bucket_col in clean_config["bucket_time_cols"].items():
        df_clean[new_col] = raw_data[bucket_col]\
                            .apply(lambda x: bucket_hours(x, clean_config["bucket_hours"]))
        # debug info
        logger.debug("New column %s created bucketing column %s", new_col, bucket_col)


    # Convert time take to hours
    for new_col, time_col in clean_config["time_to_hours"].items():
        df_clean[new_col] = raw_data[time_col].apply(lambda x: get_duration(x))
        logger.debug("New column %s created converting column %s to hours.", new_col, time_col)


    # Get number of stops
    for new_col, stop_col in clean_config["stops_cols"].items():
        df_clean[new_col] = raw_data[stop_col]\
                            .apply(lambda x: get_stops(x, **clean_config["get_stops"]))
        logger.debug("New column %s created from column %s", new_col, stop_col)


    # Convert prices to numeric
    for price_col, pattern_dict in clean_config["price_cols"].items():
        # Create new feature by mulitplying columns
        df_clean[price_col] = raw_data[price_col].str.replace(pattern_dict["pattern"],
                                                         pattern_dict["replacement"]).astype(int)
        logger.debug("%s column converted to numeric.", price_col)


    # Select features
    df_clean = df_clean[clean_config["selected_features"]]
    logger.info("Clean data created succeesfully.")
    logger.debug("Clean data shape: %s", df_clean.shape)

    # Function output
    return df_clean
