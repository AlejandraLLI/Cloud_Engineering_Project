# Cloud Engineering Meeting Minutes

## Meeting: May 25th, 2023

### Discussion
- API is updated to final version
- The pipeline currently just stores the best model. We need to change the pipeline so that it saves the 3 models to s3 directly. 
- There is a draft for the ppt. Need to get images of the architecture and cost. 
- Saturday: 
	- Meet at 9:30 am
	- Need to figure out how to deploy. Maybe split in two teams: pipeline & API. 
	- Finish the ppt 

### Task for Saturday 27th, 2023
- Save the 3 models to S3 bucket (Ruben)
- Make sure containers work with changes(Ale)
- Keep drafting ppt (ALL)
- Review project requirements (ALL)

## Meeting: May 18th, 2023

### Discussion
- Discussed on how we should upload artifacts to the S3 bucket.
- Containers for pipeline and tests are ready.
- Need to improve on the tests and API.

### Task for next week
- Fix AWS readings from previous step artifact (Ale). 
- Include more tests for feature generation (Ruben)
- Save more models (Ruben)
- Add drop down for model prediction in API (Boss)
- Add more models to endpoint (Sam)
- Start drafting presentation 
- Try to deploy API in AWS (Anyone available)


## Meeting: May 11th, 2023

### Discussion
- Updated raw_data and clean_data to read data from and upload to S3 bucket. Used profile_name option in boto3 session to handle different profiles but it is not needed if you export the profile name as environment variable in each session. 
- Added tests for clean_data module. Tried to add git actions for tests but something not working. Need to ask Ashish. 
- Modules for generating features and modelling are ready but need to add logging and testing and connection to S3 bucket. 
- Revised first version of the web page for the API. Might be good idea not to include flight code and duration as inputs from the user. 

### Task for next week
- Remove the profile_name option in aws functions (Ale)
- Complete development of features and training: logging, testing, upload to s3 (Ruben)
- Cost Estimation (Boss)
- Try to update API so that the user don't input flight code and duration. (See picture in Slack). 
- Show Ashish what we have so far and ask if we can run the whole pipeline in EC2 or if we need to split in the AWS services. 
- Build Docker container for pipeline (Ale).
- Start report and presentation. 


## Meeting: May 4th, 2023

### Discussion

- Diagram seems to be correct. We will wait to hear back from Michael to know if we need to include API gateway and Lambda into webapp. 
- Checked scripts for aquiring, creating and cleaning data. Need to fix the zip downloading. Need to ask about how the pipeline will run and might need to create a function to upload directly to S3. 
- We took a look at the models. Linear regression is too high and we have a lot of features (OHE). Need to double check. So far XGBoost is the best model, but not by much. 
- We have a first version of the API runing in Flask. 

### Tasks for next week 

- Build a function to upload to S3. Ask about how to have multiple users configured in my machine. (ALE)
- Build source modules for generating features and modelling (Ruben)
- Cost Estimation (Boss)
- Build app interface (Boss)
- Setup API endpoint on EC2 (Sam) 


## Meeting: April 26th, 2023

### Discussion

- Data cleaning: discussed if we would bucket hours of arrival and departure or numerical values. The team voted for leaving the buckets. 
	
- Diagram: 
	- AWS SQS processing que: might not need it. Ask Ashish and/or Michael how to trigger Lambda if there is not an SQS. 
	- Debate if we need an EDA between raw and cleanning & if we want to store the EDA in an S3 bucket. 
	- Training data: Is there a difference between ECS & ECS-Fargate? 
	- Ask about how to generate plots for the Webapp. Connect AWS S3 directly to fargate or call a Lambda function to run a Python script and save images.
	
	Ask if this should be just for the project or if its from buisness perspective. 

### Tasks for next week
- Convert cleaning to python script. Use pep8, typing hints etc... (ALLI)
- Create a second version of the diagram incorporating discussion and ask questions (BOSS). 
- Upload clean data to S3 bucket (ALLI). 
- Build ML models: linear regression, RF, and others (Ruben)
- Start building API (Sam). 


## Meeting: April 19th, 2023

### Discussion

- Review EDA: decided to log price of ticket, not transform duration.  
- Augment data: we don't think we need to augment data for this project. 
- Add date to the data set from original flight. Beware that we might have some wrong dates associated to the clean data. 
- Get a first draft of the architecture diagram. 

### Tasks for next week

- Go to original data set and get a raw and clean version of our own (ALE) 
- Architecture diagram in Draw.Io and complete deployment (Boss)
- Create AWS account and profiles (Ruben)
- Learn about pipe implementation & auotmation in AWS (Sam)

## Meeting: April 13th, 2023

### Discussion

Asteriod

	- Pros: 
		- intersting problem, well defined, applicable
		- "simple" data set
		- Sample notebooks for inspiration
		- 31 features, ?? rows.

	- Cons: 
		- Difficult problem to solve, high knowledge to understand. 
		- "Fancy API" would be more difficult to achieve

	- Problem: predict asteriod diameter


Driving Behavior 

	- Pros: 
		- well defined, applicable
		- many notebooks 

	- Cons: 
		- Few columns (8)
		- 2000 rows

	- Problem: 
		- classify driving (slow, normal, agressive) by using smartphone data from sensors 


Flight Prices: 
	- Pros:
		- Eassy problem, well defined 
		- Could build a nice API
		-  rows, 12 features

	- Cons:
		- Too many categoricals, but can use only Random Forest

	- Problem: 
		- Predict fight prices. 


- We decided to use flight prices problem. Asteriods is the back up project. 
- Business problem: predict ticket price 
- Discuss the two datasets with Ashish. He said the flight prices problem is ok. Although he taught we had a time series in the begining. 

### Tasks for next week

- Draft of cloud architecture
- Start code for tasks in weeks 4 & 5 of his timeline: data ingestion and data cleaning


## Meeting: April 6th, 2023

### Discussion

Data Options:
 
	- Asteriod 
	https://www.kaggle.com/datasets/basu369victor/prediction-of-asteroid-diameter

	- Soccer FIFA
	https://www.kaggle.com/datasets/stefanoleone992/fifa-22-complete-player-dataset?select=players_22.csv

	- Driving Behavior
	https://www.kaggle.com/datasets/outofskills/driving-behavior

	- Flight Prices
	https://www.kaggle.com/datasets/shubhambathwal/flight-price-prediction

### Tasks for next week
- Check the 4 data sets options for Cloud Engineering.


