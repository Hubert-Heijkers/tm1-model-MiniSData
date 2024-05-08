import requests
import base64

tm1_service_root_url = "http://cwc-tm1-v12-demo.tm1-code.io:4444/tm1/api/v1"
username = "hubert@tm1-code.io"
password = "apple"
credentials = f"{username}:{password}"
encoded_credentials = base64.b64encode(credentials.encode()).decode('utf-8')

def send_post_request(endpoint, payload):
    full_url = f"{tm1_service_root_url}/{endpoint}"
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/json"
    }
    response = requests.post(full_url, headers=headers, json=payload)
    if response.text:
        return response.status_code, response.json()
    else:
        return response.status_code, {}

def send_delete_request(endpoint):
    full_url = f"{tm1_service_root_url}/{endpoint}"
    headers = {
        "Authorization": f"Basic {encoded_credentials}"
    }
    response = requests.delete(full_url, headers=headers)
    if response.text:
        return response.status_code, response.json()
    else:
        return response.status_code, {}

database_name = "MiniSData"
databases_endpoint = "Databases"
payload = {
    "Name": f"{database_name}"
}
database_endpoint = f"{databases_endpoint}('{database_name}')"

status_code, response = send_post_request(databases_endpoint, payload)
print(f"Create database {database_name}:\nStatus Code: {status_code}\nResponse: {response}\n")

if status_code == 201 :
    status_code, response = send_delete_request(database_endpoint)
    print(f"Delete database {database_name}:\nStatus Code: {status_code}\nResponse: {response}\n")
