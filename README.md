# Cloud_Engineering Final Project
## Predicting Airline Prices 
## Developed by: 
- Alejandra Lelo de Larrea Ibarra ali8110
- Bannasorn Paspanthong
- Ruben Nakano
- Samuel Swain

This project develops a model to classify clouds into one of two types based on features generated from cloud images.

<br/>

## Table of Contents 
- [Buisness Problem](#id-BusinessProblem)
- [Project Description](#id-ProjectDesc)
- [Cloning the Repository](#id-CloneRepo)
- [Running Locally](#id-RunLocal)
- [Running Docker Container](#id-RunContainer)
- [AWS Implementation](#id-Implementation)
- [Model Deployment](#id-Deployment)

<br/><div id='id-BuisnessProblem'/>

## Business Problem

TO DO: WRITE ABOUT BUSINESS PROBLEM HERE

## Data description 

TO DO: WRITE ABOUT RAW DATA HERE. MENTION RAW DATA IS UPLOADED MANUALLY TO S3 BUCKET.

<br/><div id='id-ProjectDesc'/>

## Project Description

The project develops the following steps: 

- `src/raw_data.py` module: Read the multiple csv files from the source data in the S3 bucket and concateneate them into a single dataframe ready to be processed. 
- `src/clean_data.py` module: Clean/normalize the data
- `src/generate_features.py` module: generate features by dorpping specific columns, filtering selected airlines and log_transforming some features. 
- `src/train_model.py` module: split data in train and test, train selected ML models, score the model on the test setand calculate performance metrics on test set.

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
docker build -t airlines-pipeline -f dockerfiles/Dockerfile.pipeline_main .
```

### Run the entire model pipeline

Note that for this step, you need to have an existing AWS account with an sso configuration.

```bash
# Login to refresh credentials 
aws sso login --profile <sso_profile_name_here>

# Verify your identity 
aws sts get-caller-identity --profile <sso_profile_name_here>

# Run docker image passing your sso configuration 
docker run -v ~/.aws:/root/.aws -e AWS_PROFILE=<sso_profile_name_here> airlines-pipeline
```

Note: The artifacts generated in the pipeline are "written to disk" inside the container. If you wish to have a copy of the artifacts in your local machine you need to mount the artifacts volume to the container. This can be run by replacing the last command with the following: 

```bash
docker run -v ~/.aws:/root/.aws -v "$(pwd)"/artifacts/:/app/artifacts/ -e AWS_PROFILE=<sso_profile_name_here> airlines-pipeline
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

TO DO: DESCRIBE IMPLEMENTATION IN AWS

<br/><div id='id-Deployment'/>

## Model Deployment

This project utilizes a Flask application, predict_api.py, to serve the trained model as a RESTful API. The Flask application is responsible for receiving incoming HTTP POST requests, processing the request data, making predictions using the trained model, and responding with the prediction results.

The model endpoint is hosted on an Amazon Web Services (AWS) EC2 instance. After the EC2 instance is configured and launched, the Flask application is deployed onto it, providing a publicly accessible IP address and port at which the model can be accessed. This makes the model accessible from anywhere and scalable to accommodate potential increases in requests. The server listens on port 5000 and accepts POST requests at the /predict endpoint.

The request to the API should include a JSON body with two keys: 'Data' and 'Model'. The 'Data' key should contain the features for which a prediction is required, and the 'Model' key should specify the name of the trained model to use. The API then preprocesses the incoming data, loads the specified model from the S3 bucket, and uses it to generate a prediction. The prediction is then returned in the response.