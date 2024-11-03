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

# Remove the database
status_code, response = send_delete_request(session, tm1_service_root_url, database_endpoint)
if status_code != 204:
    log_output(f"Deletion of database {tm1_database_name} failed!", status_code, response)
    sys.exit(1)
log_output(f"Database {tm1_database_name} deleted!")
