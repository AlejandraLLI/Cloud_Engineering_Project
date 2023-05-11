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
import src.train_model as tm
import src.aws_utils as aws

# set up logger config for some file 
logging.config.fileConfig("config/logging/local.conf")
logger = logging.getLogger("airline")

if __name__ == "__main__":

    # --- Set argparser instance to handle command line arguments ---
    # Project description 
    parser = argparse.ArgumentParser(
        description="MSiA 423 - Final project: Airline price prediction"
    )
    parser.add_argument(
        "--config", default="config/default-config.yaml", help="Path to configuration file"
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

    # Access run_config key from yaml config file. If it does not exist the
    # default is an empty dictionary.    
    run_config = config.get("run_config", {})

    # Set up output directory for saving artifacts
    now = int(datetime.datetime.now().timestamp())
    artifacts = Path(run_config.get("output", "runs")) / str(now)
    artifacts.mkdir(parents=True)

    # Save config file to artifacts directory for traceability
    with (artifacts / "config.yaml").open("w") as f:
        yaml.dump(config, f)
    
    # Acquire source data from Kaggel repository, create raw data and save to disk
    #ad.acquire_data(run_config["data_source"], artifacts / "source_data.zip")

    # Create raw data set from source, upload to S3 and save to csv
    raw_data = rd.raw_data(**{**config["aws_config"],**config["raw_data"]})
    aws.upload_csv_S3(raw_data, "raw_data.csv", **config["aws_config"])
    rd.save_dataset(raw_data, artifacts / "raw_data.csv")

    # Clean raw data and save to csv
    clean_data = cd.clean_data(**{**config["aws_config"], **config["clean_data"]})
    aws.upload_csv_S3(clean_data, "clean_data.csv", **config["aws_config"])
    rd.save_dataset(clean_data, artifacts / "clean_data.csv")

    # Generate features and save to csv
    features = gf.generate_features(clean_data, config["generate_features"])
    rd.save_dataset(features, artifacts / "features.csv")

    # Train model and save results
    results, tmo = tm.train_and_evaluate(features, config["train_model"])
    tm.save_results(results, artifacts / "results.yaml")

    # Score modes?

    # Evaluate models

    # Production?

    # Upload all artifacts to S3
    #aws_config = config.get("aws")
    #if aws_config.get("upload", False):
    #    uris = aws.upload_artifacts(artifacts, aws_config)
    #    aws.write_list_files(uris, artifacts/"list_s3_uris.txt")
    #else: 
    #    logger.info("Option to upload artifacts to S3 bucket set to false. No artifacts will be uploaded.")
