from datetime import datetime, timedelta
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.sensors.time_sensor import TimeSensor
from airflow.models import Variable
import requests



today            = datetime.now()
yesterday        = today - timedelta(days=1)

start_time       = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
end_time         = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)


def get_access_token(url, username, password,**kwargs ):
    data = {
        "username": username,
        "password": password
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        ti = kwargs['ti']
        ti.xcom_push(key='token', value=response.json()["access_token"])
        return response.json()["access_token"]
    else:
        print("Error getting access token:"+ response.json())
        return None

def get_daily_prices_binance(url, start_time, end_time, **kwargs ):
    ti = kwargs['ti']
    token = ti.xcom_pull(key='token', task_ids='Get_API_token')
    if not token:
        raise ValueError("Token not found in XCom")
     
    headers = {
        'Content-Type': 'application/json',
        "Authorization": f"Bearer {token}"
        }

    params = {
    "start_time": start_time.isoformat(),
    "end_time": end_time.isoformat()
    }

    response = requests.post(url, params=params, headers=headers)
    if response.status_code == 200:
        print("successfully saved prices:", response.json())
    else:
        print("Error creating user:", response.json())

def run_prediction_model(url, **kwargs ):
    ti = kwargs['ti']
    token = ti.xcom_pull(key='token', task_ids='Get_API_token_weekly')
    if not token:
        raise ValueError("Token not found in XCom")
     
    headers = {
        'Content-Type': 'application/json',
        "Authorization": f"Bearer {token}"
        }

    params = {
    
    }

    response = requests.post(url, params=params, headers=headers)
    if response.status_code == 200:
        print("successfully run the model:", response.json())
    else:
        print("Error in running the model", response.json())



default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'retries': 2,
    'retry_delay': timedelta(seconds=60)
    
}

daily_dag = DAG(
    dag_id='Collect_Prices',
    default_args=default_args,
    description='Collect Prices for last day from Binance',
    tags=['datascientest Project', 'Predict BTC Price'],
    schedule_interval='@daily',
    catchup=False    
)

weekly_dag = DAG(
    dag_id='Run_Module',
    default_args=default_args,
    description='Run Module',
    tags=['datascientest Project', 'Predict BTC Price'],
    schedule_interval='@weekly',
    catchup=False  
)


Get_API_token = PythonOperator(
    task_id="Get_API_token",
    python_callable=get_access_token,
    op_kwargs={
        "url": "http://host.docker.internal:8000/Get_token",
        "username": "admin",
        "password": "admin2"
    },
    dag=daily_dag
)

daily_prices_binance = PythonOperator(
    task_id="daily_prices_binance",
    python_callable=get_daily_prices_binance,
    op_kwargs={
        "url": "http://host.docker.internal:8000/Save_prices_binance",
        "start_time": start_time,
        "end_time": end_time
    },
    dag=daily_dag,
    trigger_rule='all_success'
)

Get_API_token >> daily_prices_binance 


Get_API_token_weekly = PythonOperator(
    task_id="Get_API_token_weekly",
    python_callable=get_access_token,
    op_kwargs={
        "url": "http://host.docker.internal:8000/Get_token",
        "username": "admin",
        "password": "admin2"
    },
    dag=weekly_dag
)

weekly_run_model = PythonOperator(
    task_id="weekly_run_model",
    python_callable=run_prediction_model,
    op_kwargs={
        "url": "http://host.docker.internal:8000/run_model"
    },
    dag=weekly_dag,
    trigger_rule='all_success'
)


Get_API_token_weekly  >> weekly_run_model 