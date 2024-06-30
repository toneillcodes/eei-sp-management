import json
import requests
from requests.auth import HTTPBasicAuth
host = input("Carbon Console Hostname/Port: ")

admin = input("Carbon Console Admin: ")
password = input("Carbon Console Password: ")
basic = HTTPBasicAuth(admin, password)

download_dir = input("XML Download Directory: ")

## try to retrieve the first 30 applications
print("Performing intial query")
req_url = 'https://' + host + '/t/carbon.super/api/server/v1/applications'  
app_check = requests.get(req_url, auth=basic, verify=False)
print(app_check.status_code)
if(app_check.status_code == 200 or app_check.status_code == 201):
    #print(app_check.text)
    ## if this condition is true, then we got the Carbon login page
    if("WSO2 Management Console" in app_check.text):
        print("Failed, Carbon Console login page detected, double check the URL and EEI > 5.10.0")
        print("URL: " + req_url)
    else:
        ## might have a valid response, let's try parsing the JSON
        app_list_json = json.loads(app_check.text)
        #print(app_list_json)

        ## total number of applications
        app_count = app_list_json['totalResults']
        print(app_list_json['totalResults'])
        if(app_count is None):
            print("Failed, unable to determine the app count")
        else:
            print("Querying the full application list")
            ## query the full list of applications using the totalResults from our first request as the limit
            full_app_list = requests.get('https://' + host + '/t/carbon.super/api/server/v1/applications?limit=' + str(app_count), auth=basic, verify=False)
            #print(full_app_list.text)
            full_app_list_json = json.loads(full_app_list.text)
            app_list = full_app_list_json['applications']
            print(app_list)
            for app in app_list:
                print("Parsing " + app['name'])
                if(app['name'] == 'User Portal' or app['name'] == 'wso2carbon-local-sp'):
                    print("Skipping default app: " + app['name'])
                else:
                    res_export = requests.get('https://' + host + '/t/carbon.super/api/server/v1/applications/' + app['id'] + '/export', auth=basic, verify=False)
                    print(res_export.status_code)
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