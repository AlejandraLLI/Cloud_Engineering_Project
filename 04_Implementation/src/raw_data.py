"""
This module provides functions for reading the original data sources and creating a raw
data frame.   
"""
# Libraries 
import pandas as pd
from pathlib import Path
import zipfile
import src.aws_utils as aws
import logging
import io
import sys

# Set logger
logger = logging.getLogger(__name__)

def raw_data(sso_profile: str, bucket_name: str, file_key: str) -> pd.DataFrame:
    """
    This function reads multiple csv files from a zip file stored in an AWS S3 bucket,
    concatenates them into a single DataFrame, and returns it.

    Parameters:
        sso_profile (str): The AWS profile name.
        bucket_name (str): The name of the S3 bucket.
        file_key (str): The key of the zip file (i.e., its path within the bucket).

    Returns:
        df_raw (pd.DataFrame): A DataFrame containing the data from all csv files.
    """
    # --- Read csv file directly from the zip ---
    
    # Download zip file from S3
    source_file = aws.get_data_s3(sso_profile, bucket_name, file_key)

    # Un zip and get list of files
    try:
        archive = zipfile.ZipFile(io.BytesIO(source_file), 'r')
    except zipfile.BadZipFile:
        logger.error("Error while trying to unzip the source_file. Process can't continue")
        sys.exit(1)
    
    # Get list of files
    files = archive.namelist()
    logger.debug("Files in zip file: %s", files)

    # --- Load data sets --- 
    df_raw = pd.DataFrame()
    for file in files[1:]:
        try: 
            with archive.open(file) as csvfile:
                df_temp = pd.read_csv(csvfile) 
        except pd.errors.ParserError as err:
            logger.error("Error while reading csv file %s. Error: %s", file, err)
        else:
            df_temp["class"] = file.replace(".csv", "")  
            df_raw = pd.concat([df_raw, df_temp])
            logger.debug("File %s appended to raw dataframe.", file)

    # Check rawdata shape. 
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