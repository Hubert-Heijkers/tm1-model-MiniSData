import sys
from common import *

tm1_database_name = "MiniSData"
branch_name = "main"
if len(sys.argv) > 1:
    branch_name = sys.argv[1]
if len(sys.argv) > 2:
    pr_number = sys.argv[2]
    print(f"Pull Request: #{pr_number}")
    tm1_database_name = f"{tm1_database_name}-{pr_number}"
if len(sys.argv) > 3:
    commit_hash = sys.argv[3]
    print(f"Commit Hash: {commit_hash}")
    tm1_database_name = f"{tm1_database_name}-{commit_hash[:7]}"
print(f"Datbase name: {tm1_database_name}")
print(f"Sourcing from branch: {branch_name}")

tm1_service_root_url = "http://tm1-v12-demo.tm1-code.io:4444/tm1/api/v1"
tm1_service_username = "hubert@example.com"
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

def dump_file_content(file_endpoint):
    # Pull the content from the endpoint
    status_code, response = send_get_request(session, tm1_service_root_url, f"{database_endpoint}/{file_endpoint}/Content")
    if status_code == 200:
        log_output(response.text)
    else:
        log_output(f"Failed to retrieve content from {file_endpoint}!", status_code, response)

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
    "Branch": f"{branch_name}"
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
log_output("GIT Pull plan executed successfully!")

# Execute the create_Y2Ksales_cube process to validate that it works
process_name = "create_Y2Ksales_cube"
status_code, response = send_post_request(session, tm1_service_root_url, f"{database_endpoint}/Processes('{process_name}')/tm1.ExecuteWithReturn?$expand=*", {})
if status_code != 201:
    log_output(f"The request to execute the {process_name} process failed!", status_code, response)
    cleanup()
    sys.exit(1)
process_execute_status_code = response['ProcessExecuteStatusCode']
process_execute_log_file_name = response['ErrorLogFile']['Filename']
match process_execute_status_code:
    case "Aborted":
        log_output(f"Process {process_name} aborted.")
        dump_file_content(f"Contents('Files')/Contents('.tmp')/Contents('{process_execute_log_file_name}')")
        cleanup()
        sys.exit(1)
    case "CompletedSuccessfully":
        log_output(f"Process {process_name} completed successfully.")
    case _:
        log_output(f"Process {process_name} returned status code: {process_execute_status_code}.")
        dump_file_content(f"Contents('Files')/Contents('.tmp')/Contents('{process_execute_log_file_name}')")

# Last but not least, now that we're done testing, lets cleanup by removing the database
log_output("Model deployed and validated successfully!")
cleanup()