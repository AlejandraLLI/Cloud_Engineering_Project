# Libraries 
import pandas as pd
from pathlib import Path
import zipfile

def create_data(source_file: Path) -> pd.DataFrame:
    """
    DOCUMENT FUNCTION
    """
    # --- Read csv file directly from the zip ---
    # TO DO: CHANGE THIS TO DOWNLOAD DIRECTLY FROM KAGLE
    archive = zipfile.ZipFile(source_file, 'r')
    files = archive.namelist()

    # --- Load data sets --- 
    # Business class 
    with archive.open(files[1]) as csvfile:   
        df_business = pd.read_csv(csvfile)
        df_business["class"] = "Business"
        
    # Economy class 
    with archive.open(files[2]) as csvfile:   
        df_economy = pd.read_csv(csvfile)
        df_economy["class"] = "Economy"
        
    # --- Bind business and economy class --- 
    df_raw = pd.concat([df_business,df_economy], axis = 0)

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