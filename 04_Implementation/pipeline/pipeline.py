"""
This script orchestrates the entire pipeline by calling modules that 
perform each of the following steps:

    (1) Download raw data from S3 and save it locally
    (2) Clean the raw data and save it locally
    (3) Generate features from the cleaned data
    (4) Train models using the generated features
    (5) Evaluate the trained models and save the results locally
    (6) Upload all artifacts to S3

The pipeline can be configured using the file called 'default-config.yaml'
"""

import argparse
import datetime
import logging.config
from pathlib import Path

import yaml

# Self-built modules
#import src.aquire_data as ad
import src.raw_data as rd
import src.clean_data as cd
import src.aws_utils as aws
import src.train_model as tm
import src.generate_features as gf

# Set up logger config for some file
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
    with open(args.config, "r", encoding="utf-8") as f:
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

    # Create raw data set from source, upload to S3 and save to csv
    print(config["aws_config"]["bucket_name"])
    raw_data = rd.raw_data(config["aws_config"]["bucket_name"],**config["raw_data"])
    rd.save_dataset(raw_data, artifacts / "raw_data.csv")

    # Clean raw data and save to csv
    clean_data = cd.clean_data(raw_data, **config["clean_data"])
    rd.save_dataset(clean_data, artifacts / "clean_data.csv")

    # Generate features
    features = gf.generate_features(clean_data, config["generate_features"])
    rd.save_dataset(features, artifacts / "features.csv")

    # Train and evaluate models, save artifacts
    train, test, results, tmo_dict = tm.train_and_evaluate(features, config["train_model"])
    rd.save_dataset(train, artifacts / "train.csv")
    rd.save_dataset(test, artifacts / "test.csv")

    # Save results and best model
    tm.save_results(results, artifacts / "results.yaml")
    tm.save_all_models(tmo_dict, artifacts)

    # Upload all artifacts to S3
    aws_config = config.get("aws_config")
    if aws_config.get("upload", False):
        uris = aws.upload_artifacts(artifacts, aws_config)
        aws.write_list_files(uris, artifacts/"list_s3_uris.txt")
    else:
        logger.info("Upload artifacts to S3 bucket set to false. No artifacts will be uploaded.")
