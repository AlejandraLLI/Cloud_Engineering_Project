# Cloud Engineering Meeting Minutes

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


