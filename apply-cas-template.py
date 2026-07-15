import json
import getpass
import urllib3
import requests
from requests.auth import HTTPBasicAuth

# prompt for hostname/port and credentials
host = input("Carbon Console Hostname/Port: ")
admin = input("Carbon Console Admin: ")
password = getpass.getpass("Carbon Console Password: ").strip()

# build authentication object from credentials
basic = HTTPBasicAuth(admin, password)

# initialize an empty app list
all_applications = []

# try to retrieve the first 30 applications
print("Performing intial query")

urllib3.disable_warnings()

payload = {
    "authenticationSequence": {
        "type": "USER_DEFINED",
        "steps": [
            {
                "id": 1,
                "options": [
                    {"authenticator": "SAMLSSOAuthenticator", "idp": "Entra ID"}
                ]
            }
        ],
        "requestPathAuthenticators": [],
        "subjectStepId": 1,
        "attributeStepId": 1,
        "script": "var onLoginRequest = function(context) {\n    executeStep(1);\n};\n"
    }
}

req_url = 'https://' + host + '/t/carbon.super/api/server/v1/applications'  
app_check = requests.get(req_url, auth=basic, verify=False)
#print(app_check.status_code)
if(app_check.status_code == 200 or app_check.status_code == 201):
    #print(app_check.text)
    ## if this condition is true, then we got the Carbon login page and it's likely the wrong URL
    if("WSO2 Management Console" in app_check.text):
        print("Failed, Carbon Console login page detected, double check the URL and EEI >= 5.10.0")
        print("URL: " + req_url)
    else:
        ## might have a valid response, let's try parsing the JSON
        app_list_json = json.loads(app_check.text)
        #print(app_list_json)

        ## total number of applications
        app_count = app_list_json['totalResults']        
        if(app_count is None):
            print("Failed, unable to determine the app count")
        else:
            #print("Count is greater than 100, running loop")
            upper_bound = 100
            # range(start, stop, step)
            # This will give us offsets: 0, 100, 200, etc.
            for lower_bound in range(0, app_count, upper_bound):
                
                url = f'https://{host}/t/carbon.super/api/server/v1/applications'
                params = {
                    'offset': lower_bound,
                    'limit': upper_bound  # Limit stays 100 to get the next "chunk"
                }
                
                response = requests.get(url, params=params, auth=basic, verify=False)
                
                if response.status_code == 200:
                    apps = response.json()
                    # Extract the list from the current page
                    current_page_apps = apps.get('applications', [])
                    
                    # Add this page's items to the master list
                    all_applications.extend(current_page_apps)
                    
                    print(f"Collected {len(all_applications)} / {app_count} apps...")
                else:
                    print(f"Error fetching data: {response.status_code}")
                    exit

            for app in all_applications:
                # 1. Filter out default system applications
                defaults = ['User Portal', 'wso2carbon-local-sp', 'Console', 'My Account']
                if app['name'] in defaults:
                    print(f"Skipping default app: {app['name']}")
                    continue # Skip to the next iteration

                # 2. Fetch application details
                api_url = f"https://{host}/t/carbon.super/api/server/v1/applications/{app['id']}"
                res_spinfo = requests.get(api_url, auth=basic, verify=False)

                if res_spinfo.status_code != 200:
                    print(f"[ERROR] Failed to retrieve data for {app['name']}")
                    continue

                print(f"Successfully retrieved data for {app['name']}")
                app_data = res_spinfo.json() 

                # 3. Protocol Detection logic
                protocols = app_data.get("inboundProtocols", [])
                
                # Using 'any' is a clean way to check for existence in a list of dicts
                uses_saml = any(p.get("type") == "samlsso" for p in protocols)
                uses_cas = any(p.get("type") == "cas" for p in protocols)

                if uses_saml:
                    print(f"Found SAML configuration. Leaving template alone.")
                elif uses_cas:
                    print(f"This is just CAS.")
                else:
                    print(f"No SAML or CAS found for {app['name']}")

            print("SP parsing complete.")
else:
    print("Failed to query app list, status code:")
    print(app_check.status_code)