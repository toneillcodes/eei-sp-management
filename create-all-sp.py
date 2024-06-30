import os
import requests
from requests.auth import HTTPBasicAuth

host = input("Carbon Console Hostname/Port: ")

admin = input("Carbon Console Admin: ")
password = input("Carbon Console Password: ")
basic = HTTPBasicAuth(admin, password)

upload_dir = input("XML Upload Directory: ")

successful_loads = 0
failed_loads = 0

for filename in os.listdir(upload_dir):
    if filename.endswith(".xml"):
        print("Processing " + filename)
        fullpath = upload_dir + '\\' + filename
        upload_file = {'file': open(fullpath,'rb')}
        req_url = 'https://' + host + '/t/carbon.super/api/server/v1/applications/import'
        upload_response = requests.post(req_url, auth=basic, verify=False, files=upload_file)
        print(upload_response.status_code)
        if(upload_response.status_code == 200 or upload_response.status_code == 201):
            ##print(upload_response.text)
            ## if this condition is true, then we got the Carbon login page
            if("WSO2 Management Console" in upload_response.text):
                print("Failed, Carbon Console login page detected, double check the URL and EEI > 5.10.0")
                print("URL: " + req_url)
                failed_loads += 1
            else:
                successful_loads += 1
        else:
            print("Failed to load " + filename + ". Maybe the application exists??")
            print("Response code:" + str(upload_response.status_code))
            failed_loads += 1
print("Import complete, stats below")
print("Successful Loads: " + str(successful_loads))
print("Failed Loads: " + str(failed_loads))