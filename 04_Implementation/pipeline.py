import argparse
import datetime
import logging.config
from pathlib import Path

import yaml

# Self-built modules
import src.aquire_data as ad
import src.raw_data as rd
import src.clean_data as cd
import src.generate_features as gf

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="MSiA 423 - Final project: Airline price prediction"
    )
    parser.add_argument(
        "--config", default="config/default-config.yaml", help="Path to configuration file"
    )
    args = parser.parse_args()

    # Load configuration file for parameters and run config
    with open(args.config, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        
    run_config = config.get("run_config", {})

    # Set up output directory for saving artifacts
    now = int(datetime.datetime.now().timestamp())
    artifacts = Path(run_config.get("output", "runs")) / str(now)
    artifacts.mkdir(parents=True)

    # Save config file to artifacts directory for traceability
    with (artifacts / "config.yaml").open("w") as f:
        yaml.dump(config, f)
    
    # Acquire source data from Kaggel repository, create raw data and save to disk
    ##ad.acquire_data(run_config["data_source"], artifacts / "source_data.zip")

    # Create raw data set from source and save to csv
    raw_data = rd.create_data(**config["create_data"])
    rd.save_dataset(raw_data, artifacts / "raw_data.csv")

    # Clean raw data and save to csv
    clean_data = cd.clean_data(raw_data, config["clean_data"])
    rd.save_dataset(clean_data, artifacts / "clean_data.csv")

    features = gf.generate_features(clean_data, config["generate_features"])
    rd.save_dataset(features, artifacts / "features.csv")