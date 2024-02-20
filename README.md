# Museum Data Pipeline
## Case Study
LMNH's core mission is 'to provide value to the Liverpool community and the wider public'. As part of this mission, the museum regularly collects data on visitor satisfaction and wellbeing, which is then used to target exhibition development and maintenance. In the past, the museum has collected this data through written surveys and online reviews, but LMNH has recently secured funding for a new project focused on gathering immediate user feedback. This project is currently being trialled in several key exhibitions.

"Smiley Face Survey Kiosks" have been placed at the exits of the exhibitions; visitors are asked to rate their experience of the exhibition on a five-point scale (from 😡 to 😀). Each kiosk features two other buttons: an "assistance" button, for general enquiries, and an "emergency" button for immediate support.

## Functionality
This project implements an ETL pipeline that includes loading the data from a Kafka stream, data transformation and storage in a cloud-based environment. AWS services, including EC2 and RDS, facilitate the cloud-based infrastructure, ensuring scalability and reliability.

## Files 🗂️

In this folder, you will find files required the run the pipeline.

- `README.md`
    - This is the file you are currently reading.
- `pipeline.py`
    - This file contains the pipeline script - the process that extracts, transforms and loads the data into a database.
    - The pipeline script can be run using "python3 main.py"
    - If you want to log any invalid data, run "python3 main.py -log"
- `test_pipeline.py`
    - This file contains the tests for the pipeline.py script.
    - To run this script, use "pytest test_main.py"
- `requirements.txt`
    - This file contains all the required modules to run the pipeline script.
    - This file can be run using "pip3 install -r requirements.txt"
- `dashboard`
    - This folder contains the dashboard wireframe for the data and a screenshot of a dashboard created using Tableau.
- `terraform`
    - This folder contains the terraform script to create all required AWS services for this pipeline.

## Installation and Requirements
It is recommended before stating any installations that you make a new virtual environment. This can be done through commands in order:
- `python3 -m venv venv `
- `source ./venv/bin/activate`

Install all requirements for the pipeline using the command:
`pip3 install -r requirements.txt `

Create a .env file using the command:
`touch .env`

Required .env variable:
- DATABASE_NAME = The name of your database.
- DATABASE_USERNAME = The username to access your database.
- DATABASE_PASSWORD = The password to access your database.
- DATABASE_PORT = The port to access your database.
- DATABASE_HOST = The host name or address of your database server.