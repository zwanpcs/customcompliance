import requests
import json
import os
import sys
import argparse

def send_api_request(payload, auth_token, saas_path, action):
    if action == 'add':
        url = f"{saas_path}custom-compliance"
    elif action == 'delete':
        url = f"{saas_path}custom-compliance/{payload['_id']}"

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {auth_token}'
    }

    method = "PUT" if action == 'add' else "DELETE"

    try:
        response = requests.request(method, url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        print(f"Successfully {action}ed item with ID: {payload['_id']}")
    except requests.RequestException as e:
        print(f"Failed to {action} item with ID: {payload['_id']}. Error: {e}")
        return False
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", nargs='?', help="Path to the compliance JSON file", default=None)
    parser.add_argument("-action", help="Action to perform: add or delete", choices=['add', 'delete'], default='add')
    args = parser.parse_args()

    action = args.action
    json_file = args.json_file

    auth_token = os.environ.get('auth_token')
    saas_path = os.environ.get('saas_path')
    delete_list = os.environ.get('delete_list')

    if auth_token is None or saas_path is None:
        print("Environment variables auth_token and saas_path must be set.")
        return

    failed_ids = []

    if action == 'add':
        if json_file is None:
            print("Please provide the path to the compliance.json file.")
            return

        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Failed to read JSON file. Error: {e}")
            return

        for item in data:
            if not send_api_request(item, auth_token, saas_path, action):
                failed_ids.append(item['_id'])
    else:
        if delete_list is None:
            print("Environment variable delete_list must be set for delete action.")
            return

        ids_to_delete = delete_list.split(",")
        for id_str in ids_to_delete:
            item = {"_id": int(id_str.strip())}
            if not send_api_request(item, auth_token, saas_path, action):
                failed_ids.append(item['_id'])

    if failed_ids:
        print(f"Failed to process items with IDs: {failed_ids}")
    else:
        print("Successfully processed all items.")

if __name__ == "__main__":
    main()
