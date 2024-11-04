import requests
import base64
import json

def log_output(msg, status_code=None, response_json=None):
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

def setup_session(username, password):
    # Create a session object
    session = requests.Session()
    # Encode credentials for basic authentication
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode('utf-8')
    # Set headers for all requests made by this session
    session.headers.update({
        "Authorization": f"Basic {encoded_credentials}"
    })
    return session

def send_get_request(session, service_root_url, endpoint):
    full_url = f"{service_root_url}/{endpoint}"
    print(f"<<< GET {full_url}")
    response = session.get(full_url)
    return response.status_code, response

def send_post_request(session, service_root_url, endpoint, payload):
    full_url = f"{service_root_url}/{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    print(f"<<< POST {full_url}")
    print(json.dumps(payload, indent=4))
    response = session.post(full_url, headers=headers, json=payload)
    if response.text:
        return response.status_code, response.json()
    else:
        return response.status_code, {}

def send_delete_request(session, service_root_url, endpoint):
    full_url = f"{service_root_url}/{endpoint}"
    headers = {
        "Accept": "application/json"
    }
    print(f"<<< DELETE {full_url}")
    response = session.delete(full_url, headers=headers)
    if response.text:
        return response.status_code, response.json()
    else:
        return response.status_code, {}
