"""
This module provides functions for reading the original data sources and creating a raw
data frame.
"""
# Libraries
import io
import sys
import logging
from pathlib import Path
import zipfile
import pandas as pd

import src.aws_utils as aws


# Set logger
logger = logging.getLogger(__name__)

def raw_data(bucket_name: str, file_keys: list[str]) -> pd.DataFrame:
    """
    This function reads multiple csv files from a zip file stored in an AWS S3 bucket,
    concatenates them into a single DataFrame, and returns it.

    Parameters:
        bucket_name (str): The name of the S3 bucket.
        file_key (str): The key of the zip file (i.e., its path within the bucket).

    Returns:
        df_raw (pd.DataFrame): A DataFrame containing the data from all csv files.
    """
    # Empty dataframe for raw data.
    df_raw = pd.DataFrame()

    # Loop through files to download
    for file in file_keys:
        # Download file from S3
        df_temp = aws.get_data_s3(bucket_name, file)
        logger.info("File %s downloaded from %s", file, bucket_name)

        # Open as CSV
        try:
            with df_temp.open(file) as csvfile:
                df_temp = pd.read_csv(csvfile)
        except pd.errors.ParserError as err:
            logger.error("Error while reading csv file %s. Error: %s", file, err)
        else:
            logger.info("CSV file %s read successfully.")
            # Add class type
            df_temp["class"] = file.replace("_raw.csv", "")

            # Concatenate to raw dataframe
            df_raw = pd.concat([df_raw, df_temp])
            logger.debug("File %s appended to raw dataframe.", file)

    # Check rawd ata shape.
    logger.info("Raw data set successfully created from zip file.")
    logger.debug("Raw data set shape: %s", df_raw.shape)

    # Function output.
    return df_raw


def save_dataset(data: pd.DataFrame, save_path: Path) -> None:
    """
    Save dataframe as csv file to a specified path

    Args:
    --------------------------------------------
        data: Pandas dataframe to save
        save_path: Local path to write data to
    """
    # Write data into specified file
    try:
        data.to_csv(save_path, index = False)
    except FileNotFoundError:
        print(f"Error: {save_path} not found.")
    except pd.errors.ParserError:
        print(f"Error: unexpected error while writing dataframe to {save_path}")
    except Exception as err:
        print(f"Error: an error occurred when saving to file {save_path}: {err}")
