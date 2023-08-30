import requests
import json

# Send a POST request to the login endpoint
response = requests.post('http://127.0.0.1:8000/login', json={
    "username": "username",
    "password": "password",
    "application": "apc application"
})
response_json = response.json()
token = response_json.get('token')


# Send a GET request to the root endpoint with the Authorization header
response = requests.get('http://127.0.0.1:8000/', headers={
    'Authorization': f'Bearer {token}'
})
print(response.text)