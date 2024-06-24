#!/bin/bash

# Initialize the database
airflow db init

# Create the user
/usr/local/bin/create_user.sh

# Start Airflow webserver in the background
airflow webserver --host 0.0.0.0 --port 8080 &

# Start Airflow scheduler
exec airflow scheduler
