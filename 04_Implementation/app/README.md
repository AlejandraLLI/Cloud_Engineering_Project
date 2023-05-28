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

This project utilizes a Flask application, predict_api.py, to serve the trained model as a RESTful API. The Flask application is responsible for receiving incoming HTTP POST requests, processing the request data, making predictions using the trained model, and responding with the prediction results.

After the EC2 instance is configured and launched, the Flask application is deployed onto it, providing a publicly accessible IP address and port from which the model can be accessed. This makes the model accessible from anywhere and scalable to accommodate potential increases in requests. The server listens on port 5000 and accepts POST requests at the /predict endpoint.

The request to the API should include a JSON body with two keys: 'Data' and 'Model'. The 'Data' key should contain the features for which a prediction is required, and the 'Model' key should specify the name of the trained model to use. The API then preprocesses the incoming data, loads the specified model from the S3 bucket, and uses it to generate a prediction. The prediction is then returned in the response.

As for the frontend, the project uses Streamlit to build the app interface. The model API is deployed AWS using ECR for exposing the image and ECS to deploy the service. The data and the models are accessed from the specified S3 bucket and then are loaded to memory and cached so that each new prediction does not keep downloading data from S3. 

<br/><div id='id-CloneRepo'/>

## Cloning the repository

To be able to run this project, you first need to clone this repo as follows: 

1. Open a terminal and navigate to the location where you want to clone the repo. 

2. Clone the repository:

    ```bash
    git clone git@github.com:AlejandraLLI/Cloud_Engineering_Project.git
    ```
3. Navigate into the cloned repository and into the 04_Implementation/app folder: 

    ```bash
    cd Cloud_Engineering_Project/04_Implementation/app
    ```

<br/><div id='id-RunLocal'/>

## Running locally 

Once the repo has been cloned and you are inside the project app folder, the complete application can be run locally executing the following steps with a version of python >=3.9:

1. On the terminal, run the following commands:

    ```bash
    # Create environment variables 
    export BUCKET_NAME=<your_bucket_name_here_with_models>
    export PREFIX=<s3_bucket_prefix_for_models>

    # Create a python environment
    python -m venv .venvapp

    #Activate environment
    source .venvapp/bin/activate

    # Install required packages
    pip install -r requirements.txt

    # Run the complete pipeline 
    streamlit run src/webapp.py
    ```

<br/><div id='id-RunContainer'/>

## Running Docker Container 

Additionally, for simplification and replicability purposes, A docker images was built and included with the repo under the `dockerfiles` folder: `Dockerfile`. 

The following instructions detail how to build and run the container. 

### Build he Docker Image

```bash
# Build docker image for pipeline
docker build -t airline-app -f dockerfiles/Dockerfile .
```

### Run the Docker Container

Note that for this step, you need to have an existing AWS account with an sso configuration.

```bash
# Login to refresh credentials 
aws sso login --profile <sso_profile_name_here>

# Verify your identity 
aws sts get-caller-identity --profile <sso_profile_name_here>

# Run docker image passing your sso configuration 
docker run -v ~/.aws:/root/.aws -e AWS_PROFILE=<sso_profile_name_here> -e BUCKET_NAME=<your_bucket_name_here> -e PREFIX=<your_prefix_for_models_here> -p 80:80 airline-app
```