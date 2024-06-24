Setup Guide
------------
Step 1: Install PostgreSQL
---------------------------
Download and install PostgreSQL from the official website: PostgreSQL Downloads

Step 2: Install Docker Desktop
-----------------------------
Download and install Docker Desktop for your operating system from the official website: Docker Desktop

Step 3: Create Token on Binance
-------------------------------
Sign in to your Binance account.
Navigate to the API Management section.
Create a new API key and secret.
Ensure to keep your API key and secret secure.

Step 4: Configure Environment Variables
----------------------------------------
Replace the Databse details and binance token on .env file.


Step 5: Build Docker Image and Start Services
---------------------------------------------------
Open a terminal or command prompt.
Navigate to the directory containing your project files.
Run the following command to build the Docker image and start all services:
docker-compose up -d


Account Information for FastAPI
------------------------------------
Use the following credentials to log in to FastAPI and access the APIs:
Username: admin
Password: admin2

Additional Notes
-----------------
Ensure that PostgreSQL is running before starting the Docker services.
Verify that Docker Desktop is installed and running properly.
Double-check the correctness of the database and Binance API credentials in the .env file.

Stopping Docker Services:
-------------------------
Use the following command to stop the Docker services: 
docker-compose down

Deleting Docker Images:
--------------------------
you can delete Docker images using the following command: 
docker image rm binance-python_code binance-fastapi binance-airflow

Airflow Credentials:
------------------
Admin
adminpassword


