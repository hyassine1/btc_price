import requests
from datetime import datetime,timedelta
# Replace these variables with your actual server URL and user credentials
BASE_URL = "http://127.0.0.1:8000"
CREATE_USER_URL = f"{BASE_URL}/Create_new_user/"
TOKEN_URL = f"{BASE_URL}/Get_token"

# User credentials
admin_user = {
    "username": "admin2",
    "password": "admin2"
}

def create_user(url, user_data, headers):
    response = requests.post(url, json=user_data, headers=headers)
    if response.status_code == 200:
        print("User created successfully:", response.json())
    else:
        print("Error creating user:", response.json())

def get_access_token(url, username, password):
    data = {
        "username": username,
        "password": password
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print("Error getting access token:", response.json())
        return None

def get_daily_prices_binance(url, start_time, end_time, headers):
    params = {
    "start_time": start_time.isoformat(),
    "end_time": end_time.isoformat()
    }

    response = requests.post(url, params=params, headers=headers)
    if response.status_code == 200:
        print("successfully saved prices:", response.json())
    else:
        print("Error getting prices:", response.json())

        
# Get an access token
token = get_access_token(TOKEN_URL, admin_user["username"], admin_user["password"])

if token:
    print("Access token:", token)

    headers = {
        'Content-Type': 'application/json',
        "Authorization": f"Bearer {token}"
        }

    new_user = {
    "username": "admin22",
    "password": "admin22"
    }
    # Create a new user
    create_user(CREATE_USER_URL, new_user, headers=headers)

today            = datetime.now()
yesterday        = today - timedelta(days=1)

start_time       = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
end_time         = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)

print(start_time)
get_daily_prices_binance ("http://127.0.0.1:8000/Save_prices_binance", start_time, end_time, headers=headers)