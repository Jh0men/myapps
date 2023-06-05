# Script Description:

# 1. Imports necessary libraries: tabulate, requests, types_1, and time.
# 2. Sets up the required variables, such as client_id, client_secret, and path.
# 3. Defines the get_access_token() function to send a POST request to the Bitwarden authentication server and retrieve the OAuth2 access token.
# 4. Defines the get_event_data() function to retrieve event data from the Bitwarden API using the access token.
# 5. Defines the get_users() function to retrieve user data from the Bitwarden API using the access token.
# 6. Defines the main() function that gathers the access token, event data, and user data. It then parses the event data, adds user information to
#    flagged events, and creates an output file named "Bitwarden_events.txt" containing the flagged events' details.
# 7. Executes the main() function if the script is run as the main module.

# Please note that some parts of the code refer to external modules or variables (types_1).
# To use the script, you need to make sure you have the necessary dependencies installed and provide
# valid values for the client_id and client_secret variables. By default "Bitwarden_events.txt" is saved in the src folder.


# Import necessary libraries
from tabulate import tabulate
from datetime import datetime, timedelta
import requests
import types_1
import time
# Define date information for filtering events
date_str, date_end = datetime.now() - timedelta(days=7), datetime.now()
date_format = '%Y-%m-%d'
# Bitwarden client id
client_id = ""
# Bitwarden client secret
client_secret = ""
# Path to save the output file (e.g., "C:/Users/<YOUR USER>/Desktop")
path = "."

# Function to retrieve the OAuth2 access token from the Bitwarden authentication server


def get_access_token():
    data = {
        "grant_type": "client_credentials",
        "scope": "api.organization",
        "client_id": client_id,  # Set your own client id
        "client_secret": client_secret,  # Set your own client secret
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(
        'https://identity.bitwarden.com/connect/token', data=data, headers=headers)
    json_data = response.json()
    time.sleep(5)
    try:
        return json_data['access_token']
    except:
        return json_data

# Function to retrieve event data from the Bitwarden API using the access token


def get_event_data(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(
        'https://api.bitwarden.com/public/events', headers=headers)
    return response.json()

# Function to retrieve user data from the Bitwarden API using the access token


def get_users(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(
        'https://api.bitwarden.com/public/members', headers=headers)
    return response.json()

# Main function that gathers access token, events, and users, and creates an output file from parsed events (if any)


def main():
    token = get_access_token()
    try:
        with open(f'{path}/Bitwarden_events.txt', 'w') as file:
            file.write(
                f"Error from the Bitwarden auth server: {token['error']}")
        return 0
    except:
        event_data = get_event_data(token)
        user_data = get_users(token)
        flagged_events = list()

        # Check if event type is forbidden, add event description, and append to flagged events
        for d in event_data['data']:
            if d['type'] in types_1.forbidden_events_by_type:
                d.update({"event_desc": types_1.type_description[d['type']]})
                flagged_events.append(d)

        # Parse flagged events and add user information to events
        for d in flagged_events:
            del d["object"]
            del d["itemId"]
            del d["collectionId"]
            del d["groupId"]
            del d["policyId"]
            del d["memberId"]
            del d["installationId"]
            for u in user_data['data']:
                if d['actingUserId'] == u['userId']:
                    d.update({"name": u['name'], "email": u['email'],
                             "device_type": types_1.devicetypes[d['device']]})
                    break

        # If there are flagged events, create "Bitwarden_events.txt" file and list all flagged events
        if len(flagged_events) > 0:
            with open(f'{path}/Bitwarden_events.txt', 'w') as file:
                file.write("\t\tFLAGGED EVENTS\n\n\n")
                for d in flagged_events:
                    date = datetime.strptime(
                        str(d['date']).split('T')[0], date_format)
                    # Log flagged events from the past 7 days
                    if date >= date_str and date <= date_end:
                        content = f"""
                        Event Description: {d['event_desc']}
                        Triggered By: {d['name']} / {d['email']}
                        Device Type: {types_1.devicetypes[d['device']]}
                        Device IP: {d['ipAddress']}
                        Date: {str(d['date']).split('T')[0]}
                        Time: {str(d['date']).split('T')[1]}
                        """
                        table = [[content]]
                        output = tabulate(table, tablefmt='grid')
                        file.write(output + '\n\n')


# Execute the script
if __name__ == "__main__":
    main()
