import json
import getpass
import urllib3
import requests
from requests.auth import HTTPBasicAuth

# prompt for hostname/port and credentials
host = getpass.getpass("Carbon Console Hostname/Port: ").strip()
admin = getpass.getpass("Carbon Console Admin: ").strip()
password = getpass.getpass("Carbon Console Password: ").strip()

# build authentication object from credentials
basic = HTTPBasicAuth(admin, password)

# prompt for the download directory
download_dir = input("XML Download Directory: ")

# initialize an empty app list
all_applications = []

# try to retrieve the first 30 applications
print("Performing intial query")

urllib3.disable_warnings()

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
                #print("Parsing " + app['name'])
                if(app['name'] == 'User Portal' or app['name'] == 'wso2carbon-local-sp'):
                    print("Skipping default app: " + app['name'])
                else:
                    res_export = requests.get('https://' + host + '/t/carbon.super/api/server/v1/applications/' + app['id'] + '/export', auth=basic, verify=False)
                    #print(res_export.status_code)
                    if(res_export.status_code == 200):
                        #print(res_export.text)
                        filename = download_dir + '\\' + app['name'] + '.xml'
                        f = open(filename, 'w')
                        f.write(res_export.text)
                        f.close()
                    else:
                        print("Failed to export " + app['name'])            
        print("Export complete.")
else:
    print("Failed to query app list, status code:")
    print(app_check.status_code)