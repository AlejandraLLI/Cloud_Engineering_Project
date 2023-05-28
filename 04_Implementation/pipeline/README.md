# Cloud_Engineering Final Project
## Predicting Airline Prices - Pipeline
## Developed by: 
- Alejandra Lelo de Larrea Ibarra
- Bannasorn Paspanthong
- Ruben Nakano
- Samuel Swain

This project develops the pipline to train different ML models to predict airline prices for different flight configurations.

<br/>

## Table of Contents 
- [Project Description](#id-ProjectDesc)
- [Cloning the Repository](#id-CloneRepo)
- [Running Locally](#id-RunLocal)
- [Running Docker Container](#id-RunContainer)
- [AWS Implementation](#id-Implementation)
- [Model Deployment](#id-Deployment)


<br/><div id='id-ProjectDesc'/>

## Project Description

The pipeline develops the following steps: 

- `src/raw_data.py` module: Read the multiple csv files stores as zip file from the source data in the S3 bucket and concateneate them into a single dataframe ready to be processed. 
- `src/clean_data.py` module: Clean/normalize the data
- `src/generate_features.py` module: generate features by dorpping specific columns, filtering selected airlines and log_transforming some features. 
- `src/train_model.py` module: split data in train and test, train three different ML models (linear regression, random forest and xgboost), scores each model on the test set and calculate performance metrics on test set.

All the parameters needed to run the pipeline are setup in the `default-config.yaml` file under the `config` folder and are automatically loaded when running the pipeline. Parameters are listed by module to facilitate the interpretation and understanding. You can edit any of the input parameters to adjust the pipeline for specific experiments. Specific information on each parameter can be found in the function documentation of each module. 

Note that all key "artifacts" are saved to disk under the `artifacts` folder (which will be created automatically if it does not exist) and logs are automatically printed to the `config/logging` folder under the `pipeline.log` file. The logging level is set to INFO by default, but the log configuration can also be customized in the `local.conf` file. 

Additionally, as a final functionality, the process allows the upload of all generated artifacts into a specific S3 bucket. To this end, you need to set the following variables in the `default-config.yaml` file: 

- `upload`: indicates if files in the artifacts folder should be uploaded to an AWS S3 bucket. By default it is set to `False`. 
- `bucket_name`: name of the S3 to which to upload the artifacts. Default is `clouds-ali8110`.
- `prefix`: name of the folder to create inside S3 bucket to upload artifacts. Default is set to `experiments`.

The process uses "default credential chain" in order to be able to upload the artifacts directly to the AWS S3 bucket. Therefore, to be able to use this functionality of the process you need to: 

1. Have an existing AWS account with an sso configuration and an active session. 
Note: Refer to [AWS documentation](https://docs.aws.amazon.com/singlesignon/latest/userguide/useraccess.html) to setup your account and sso configuration. 

2. Have the specified S3 bucket already created in your account. If the bucket does not exist, the process will not be able to upload any files. 

Finally, the project contains tests for the generate features module under the `tests\test_generate_features.py` file. 

<br/><div id='id-CloneRepo'/>

## Cloning the repository

To be able to run this project, you first need to clone this repo as follows: 

1. Open a terminal and navigate to the location where you want to clone the repo. 

2. Clone the repository:

    ```bash
    git clone git@github.com:AlejandraLLI/Cloud_Engineering_Project.git
    ```
3. Navigate into the cloned repository and into the 04_Implementation/pipeline folder: 

    ```bash
    cd Cloud_Engineering_Project/04_Implementation/pipeline
    ```

<br/><div id='id-RunLocal'/>

## Running locally 

Once the repo has been cloned and you are inside the project pipeline folder, the complete pipeline can be run locally executing the following steps with a version of python >=3.9:

1. Make any changes to the `config/default-config.yaml` file and save the file. 

2. On the terminal, run the following commands to run the pipeline:

    ```bash
    # Create a python environment
    python -m venv .venv

    #Activate environment
    source .venv/bin/activate

    # Install required packages
    pip install -r requirements_main.txt

    # Run the complete pipeline 
    python pipeline.py
     ```

3. On the terminal, run the following commands to run the tests:
    ```bash
    # Deactivate previous environment 
    deactivate

    # Go to the tests folder
    cd tests

    # Create a python environment
    python -m venv .venvtests

    #Activate environment
    source .venvtests/bin/activate

    # Install required packages
    pip install -r ../requirements_tests.txt

    # Run tests 
    pytest
    ```

<br/><div id='id-RunContainer'/>

## Running Docker Container 

Additionally, for simplification and replicability purposes, two docker images were built and included with the repo under the `dockerfiles` folder: `Dockerfile.main` to run the main pipeline and `Dockerfile.tests` to run the tests. 

The following instructions detail how to build and run each of the containers. Make sure to update the `default-config.yaml` parameters before building the docker image. 

### Build he Docker Image

```bash
# Build docker image for pipeline
docker build -t airline-pipeline -f dockerfiles/Dockerfile.pipeline_main .
```

### Run the entire model pipeline

Note that for this step, you need to have an existing AWS account with an sso configuration.

```bash
# Login to refresh credentials 
aws sso login --profile <sso_profile_name_here>

# Verify your identity 
aws sts get-caller-identity --profile <sso_profile_name_here>

# Run docker image passing your sso configuration 
docker run -v ~/.aws:/root/.aws -e AWS_PROFILE=<sso_profile_name_here> airline-pipeline
```

Note: The artifacts generated in the pipeline are "written to disk" inside the container. If you wish to have a copy of the artifacts in your local machine you need to mount the artifacts volume to the container. This can be run by replacing the last command with the following: 

```bash
docker run -v ~/.aws:/root/.aws -v "$(pwd)"/artifacts/:/app/artifacts/ -e AWS_PROFILE=<sso_profile_name_here> airline-pipeline
``` 

### Build the docker image for tests

```bash
# Build docker image for test
docker build -t airlines-tests -f dockerfiles/Dockerfile.tests . 
```

### Run the tests

```bash
# Run docker image for tests
docker run airlines-tests
```

<br/><div id='id-Implementation'/>

## AWS Implementation

The complete pipeline was run in AWS using ECR to expose the airline-pipeline image and ECS Fargate to run data cleaning, feature engineering, modelling, scoring and evaluation steps. All the generated artifacts are stored in the S3 bucket https://s3.console.aws.amazon.com/s3/buckets/msia423-g7?region=us-east-2&tab=objects