import requests
import base64
import json
import sys

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
        return response.status_code, json.dumps(response.json(), indent=4)
    else:
        return response.status_code, {}

def send_delete_request(endpoint):
    full_url = f"{tm1_service_root_url}/{endpoint}"
    headers = {
        "Authorization": f"Basic {encoded_credentials}"
    }
    response = requests.delete(full_url, headers=headers)
    if response.text:
        return response.status_code, json.dumps(response.json(), indent=4)
    else:
        return response.status_code, {}

database_name = "MiniSData"
databases_endpoint = "Databases"
payload = {
    "Name": f"{database_name}"
}

# Create the database on our target TM1 service instance
status_code, response = send_post_request(databases_endpoint, payload)
if status_code != 201:
    print(f">>> Creation of database {database_name} failed! Status Code: {status_code} Response:\n{response}")
    sys.exit(1)
print(f">>> Database {database_name} created successfully! Response:\n{response}")

# Compose the endpoint for the newly created database 
database_endpoint = f"{databases_endpoint}('{database_name}')"

# Last but not least, now that we're done testing, lets cleanup by removing the database
status_code, response = send_delete_request(database_endpoint)
if status_code != 204:
    print(f">>> Deletion of database {database_name} failed! Status Code: {status_code} Response:\n{response}")
    sys.exit(1)
print(f">>> Database {database_name} deleted!")
