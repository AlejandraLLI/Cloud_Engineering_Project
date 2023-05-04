# Libraries 
from pathlib import Path
import requests
import time
import sys

def get_data(url: str, attempts: int = 4, wait: int = 3, wait_multiple: int = 2) -> str:
    """
    Acquires data from a specific URL. 

    Args:
    --------------------------------------------
    url: str with the url from where to extract data
    attempts: int number of attemps to retrive data. Defaults to 4
    wait: int seconds to wait for a response. Defaults to 3. 
    wait_multiple: int seconds to wait before retrying a request. Defaults to 2.

    Returns:
    --------------------------------------------
    str with content from url.
    """
    n_attempts = 0

    # While have some attempts left, try to download the data
    while n_attempts <= attempts:
        try:
            # Request data from url
            response = requests.get(url, stream = True, timeout = wait)
            # Raise an HTTPError exception
            response.raise_for_status()

            # Function output
            return response
        except requests.exceptions.ConnectTimeout:
            time.sleep(wait_multiple)
        except requests.exceptions.HTTPError as http_err:
            # Print HTTPError exception
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            # Print any other error
            print(f"An error occurred: {err}")

        n_attempts =+ 1


def acquire_data(url: str, save_path: Path) -> None:
    """
    Acquires data from specified URL

    Args:
    --------------------------------------------
        url: URL for where data to be acquired is stored
        save_path: Local path to write data to
    """
    # Get data
    url_contents = get_data(url)

    try:
        # Read zip file 
        with open(save_path, "wb") as f:
            for chunk in url_contents.iter_content(chunk_size=512):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)

        #logger.info("Data written to %s", save_path)
    except FileNotFoundError:
        #logger.error("Please provide a valid file location to save dataset to.")
        sys.exit(1)
    except Exception as e:
        #logger.error("Error occurred while trying to write dataset to file: %s", e)
        sys.exit(1)


