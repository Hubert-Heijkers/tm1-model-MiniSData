import requests
import base64
import json
import sys

database_name = "MiniSData"
if len(sys.argv) > 1:
    pr_number = sys.argv[1]
    print(f"Pull Request: #{pr_number}")
    database_name = f"{database_name}-{pr_number}"
if len(sys.argv) > 2:
    commit_hash = sys.argv[2]
    print(f"Commit Hash: {commit_hash}")
    database_name = f"{database_name}-{commit_hash[:7]}"
print(f"Datbase name: {database_name}")

tm1_service_root_url = "http://cwc-tm1-v12-demo.tm1-code.io:4444/tm1/api/v1"
tm1_service_username = "hubert@tm1-code.io"
tm1_service_password = "apple"

def setup_session():
    # Create a session object
    session = requests.Session()
    # Encode credentials for basic authentication
    credentials = f"{tm1_service_username}:{tm1_service_password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode('utf-8')
    # Set headers for all requests made by this session
    session.headers.update({
        "Authorization": f"Basic {encoded_credentials}"
    })
    return session

# Setup session and authentication
session = setup_session()

def send_post_request(endpoint, payload):
    full_url = f"{tm1_service_root_url}/{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    print(f"<<< {full_url}")
    print(json.dumps(payload, indent=4))
    response = session.post(full_url, headers=headers, json=payload)
    if response.text:
        return response.status_code, response.json()
    else:
        return response.status_code, {}

def send_delete_request(endpoint):
    full_url = f"{tm1_service_root_url}/{endpoint}"
    headers = {
        "Accept": "application/json"
    }
    response = session.delete(full_url, headers=headers)
    if response.text:
        return response.status_code, response.json()
    else:
        return response.status_code, {}

def log_output(msg, status_code, response_json):
    if status_code != None:
        if response_json != None:
            print(f">>> {msg} Status Code: {status_code} Response:")
        else:
            print(f">>> {msg} Status Code: {status_code}")
    else:
        if response_json != None:
            print(f">>> {msg} Response:")
        else:
            print(f">>> {msg}")
    if response_json != None:
        print(json.dumps(response_json, indent=4))

databases_endpoint = "Databases"
database_endpoint = f"{databases_endpoint}('{database_name}')"

def cleanup():
    # Remove the database
    status_code, response = send_delete_request(database_endpoint)
    if status_code != 204:
        log_output(f"Deletion of database {database_name} failed!", status_code, response)
        sys.exit(1)
    log_output(f"Database {database_name} deleted!", None, None)

# Create the database on our target TM1 service instance
database_create_payload = {
    "Name": f"{database_name}"
}
status_code, response = send_post_request(databases_endpoint, database_create_payload)
if status_code != 201:
    log_output(f"Creation of database {database_name} failed!", status_code, response)
    sys.exit(1)
log_output(f"Database {database_name} created successfully!", None, response)

# Initialize the connection to the GIT repository
git_init_payload = {
    "URL": "https://github.com/Hubert-Heijkers/tm1-model-MiniSData.git",
    "Deployment": "Development"
}
status_code, response = send_post_request(f"{database_endpoint}/GitInit", git_init_payload)
if status_code != 201:
    log_output(f"Initializing GIT failed!", status_code, response)
    cleanup()
    sys.exit(1)
log_output("GIT initialized successfully!", None, response)

# Pull the latest version of the sources from the main branch
git_pull_payload = {
    "Branch": "main"
}
status_code, response = send_post_request(f"{database_endpoint}/GitPull", git_pull_payload)
if status_code != 201:
    print(f"Creating Pull from GIT failed!", status_code, response)
    cleanup()
    sys.exit(1)
git_pull_id = response['ID']
log_output(f"GIT Pull plan {git_pull_id} created!", None, response)

# Execute the Pull plan
status_code, response = send_post_request(f"{database_endpoint}/GitPlans('{git_pull_id}')/tm1.Execute", {})
if status_code != 204:
    log_output(f"Execution of Pull plan failed!", status_code, response)
    cleanup()
    sys.exit(1)
log_output("GIT Pull plan executed successfully!", None, None)

# Last but not least, now that we're done testing, lets cleanup by removing the database
log_output("Model deployed successfully!", None, None)
cleanup()