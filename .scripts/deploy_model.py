import sys
from common import *

tm1_database_name = "MiniSData"
tm1_service_root_url = "http://7-anwendertag-demo.tm1-code.io:4444/7-anwendertag/api/v1"
tm1_service_username = "github-actions@example.com"
tm1_service_password = "apple"

# Setup session and authentication
session = setup_session(tm1_service_username, tm1_service_password)

databases_endpoint = "Databases"
database_endpoint = f"{databases_endpoint}('{tm1_database_name}')"

def cleanup():
    # Remove the database
    status_code, response = send_delete_request(session, tm1_service_root_url, database_endpoint)
    if status_code != 204:
        log_output(f"Deletion of database {tm1_database_name} failed!", status_code, response)
        sys.exit(1)
    log_output(f"Database {tm1_database_name} deleted!")

# Create the database on our target TM1 service instance
database_create_payload = {
    "Name": f"{tm1_database_name}"
}
status_code, response = send_post_request(session, tm1_service_root_url, databases_endpoint, database_create_payload)
if status_code != 201:
    log_output(f"Creation of database {tm1_database_name} failed!", status_code, response)
    sys.exit(1)
log_output(f"Database {tm1_database_name} created successfully!", response_json=response)

# Initialize the connection to the GIT repository
git_init_payload = {
    "URL": "https://github.com/Hubert-Heijkers/tm1-model-MiniSData.git",
    "Deployment": "Development"
}
status_code, response = send_post_request(session, tm1_service_root_url, f"{database_endpoint}/GitInit", git_init_payload)
if status_code != 201:
    log_output(f"Initializing GIT failed!", status_code, response)
    cleanup()
    sys.exit(1)
log_output("GIT initialized successfully!", response_json=response)

# Pull the latest version of the sources from the main branch
git_pull_payload = {
    "Branch": "main"
}
status_code, response = send_post_request(session, tm1_service_root_url, f"{database_endpoint}/GitPull", git_pull_payload)
if status_code != 201:
    log_output(f"Creating Pull from GIT failed!", status_code, response)
    cleanup()
    sys.exit(1)
git_pull_id = response['ID']
log_output(f"GIT Pull plan {git_pull_id} created!", response_json=response)

# Execute the Pull plan
status_code, response = send_post_request(session, tm1_service_root_url, f"{database_endpoint}/GitPlans('{git_pull_id}')/tm1.Execute", {})
if status_code != 204:
    log_output(f"Execution of Pull plan failed!", status_code, response)
    cleanup()
    sys.exit(1)
log_output("Model deployed successfully!")
