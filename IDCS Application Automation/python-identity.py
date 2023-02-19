################################################################################
# This code is provided on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND.
# It is intended as a demonstration and should not be used for any other purposes.

#
# Note: This code is intended as a simple example of how to
# make REST API calls to OCI's IDCS. It has little to no Error checking and will throw
# exceptions the underlying layer throws when it encounters a problem.
# 
################################################################################


################################################################################

# Goal:

# This python script automates the creation of confidential applications in IDCS.

# Confidential Applications are required in IDCS to exchange OAuth token between IDCS and your desired application.
# Moreover, confidential applications allow Oracle apps such as Essbase, EPM, ERP, etc. utilize IDCS as the Identity Layer.

# Traditionally, users would have to create applications manually within IDCS. This script aims to eliminate manual effort
# and allows IDCS application creation. This in turn allows creation of identity layers for your apps which may have been automated through
# IaC technologies like Terraform


################################################################################


################################################################################

# PRE-REQUISITES to running this Automation Script:

'''

1) Review IDCS REST APIs here: https://docs.oracle.com/en/cloud/paas/identity-cloud/rest-api/index.html 

2) Review the creation of the Client Application for the Bearer Access Token as mentioned in the Readme.md

    a) Copy the Client ID, Client Secret of your created application

    b) Copy the Base URL of IDCS. Format: https://idcs-<id>.identity.oraclecloud.com

3) Test out APIs operations by connecting with Postman. Steps to configure Postman: https://www.oracle.com/webfolder/technetwork/tutorials/obe/cloud/idcs/idcs_rest_postman_obe/rest_postman.html 

4) Keep the confidential applications config values handy, such as Logout URL, Application URL, etc.

5) Copy the Client ID, Client Secret of your created application

'''

################################################################################


# Importing the required Libraries

# The logging library can be used for tracking the API responses

import requests
import os
import logging
import json
from requests.auth import HTTPBasicAuth
import urllib.parse

# Store the Host ID, Client ID, Client Secret in environment variables

host = os.environ['HOST_ID']
client_id = os.environ['CLIENT_ID']
secret = os.environ['CLIENT_SECRET']

# Required for API request tracking

################################################################################

# from http.client import HTTPConnection  # py3

# log = logging.getLogger('urllib3')
# log.setLevel(logging.DEBUG)

# # logging from urllib3 to console
# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)
# log.addHandler(ch)

# # print statements from `http.client.HTTPConnection` to console/stdout
# HTTPConnection.debuglevel = 1


# headers = {
#     # 'Authorization': '',
#     'Authorization': secret,
#     'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
# }

################################################################################


def get_token(endpoint: str) -> str:

    '''

        Configures your Oauth application in the script.
        API call to generate Oauth Access Token.

    '''


    data = {
        'grant_type' : 'client_credentials',
        'scope' : 'urn:opc:idm:__myscopes__'
    }

    endpoint_url = f'{host}/{endpoint}'
    response = requests.post(endpoint_url, auth=HTTPBasicAuth(client_id, secret), data=data)
    acc_token = json.loads(response.text)
    return acc_token['access_token']


def get_all_users(endpoint: str, token: str):

    '''

        Gets all users in your IDCS Stripe. 

        Prints the Json Response of all users. 

        Filter the required user, by the filter parameter in the API

    '''

    auth = 'Bearer ' + token
    
    headers = {
        'Authorization' : auth,
        'Content-Type': 'application/json'
    }

    endpoint_url = f"{host}/{endpoint}"
    users = requests.get(endpoint_url, headers=headers)
    print(users.json())


def create_confidential_app(endpoint: str, token: str, displayname: str):


    '''

        Creates the Confidential Application for the given DisplayName

        Change the URIs as needed

    '''

    auth = 'Bearer ' + token

    headers = {
        'Authorization' : auth,
        'Content-Type': 'application/json'
    }

    body = {

        "schemas": ["urn:ietf:params:scim:schemas:oracle:idcs:App"],
        "basedOnTemplate": { "value": "CustomWebAppTemplateId" },
        "displayName": displayname,
        "description": "Confidential client application for testing purposes",
        "clientType": "confidential",
        "active": True,
        "isUnmanagedApp": True,
        "isOAuthClient": True,
        "allowedGrants": ["authorization_code","client_credentials","refresh_token","urn:ietf:params:oauth:grant-type:jwt-bearer"],
        "redirectUris": ["https://www.essbase.com/callback"],
        "logoutUri": "https://www.myapp.com/logout",
        "postLogoutRedirectUris": ["https://www.myapp.com/"]

    }
    endpoint_url = f"{host}/{endpoint}"
    users = requests.post(endpoint_url, headers=headers, json=body)


def get_apps(endpoint: str, token: str, params):

    '''

        Gets information of a specific IDCS application.

        Use this function to check configuration, get the App ID of an App, etc.

    '''

    auth = 'Bearer ' + token

    headers = {
        'Authorization' : auth,
        'Content-Type': 'application/json'
    }

    endpoint_url = f"{host}/{endpoint}"

    if params:
        endpoint_url += "?" + urllib.parse.urlencode( params )
    
    print(endpoint_url)
    response = requests.get(endpoint_url, headers=headers)
    # print(response.json())
    return (response.json()["Resources"][0]["id"])


def get_approle_for_app(endpoint:str, token: str, params):

    '''

        Function is used to get the AppRole ID of a specific AppRole Grant

    '''

    auth = 'Bearer ' + token

    headers = {
        'Authorization' : auth,
        'Content-Type': 'application/json'
    }

    endpoint_url = f"{host}/{endpoint}"

    if params:
        endpoint_url += "?" + urllib.parse.urlencode( params )

    
    response = requests.get(endpoint_url, headers=headers)
    print(response.json()["Resources"][0]["id"])




access = get_token('oauth2/v1/token')
users = get_all_users('admin/v1/Users', access)
app = create_confidential_app('admin/v1/Apps', access, "ScriptAppDeployed")
created_app_id = get_apps('admin/v1/Apps', access, {"filter" : "displayname eq \"" + "ScriptAppDeployed" + "\"",
                                "attributes" : "id"})

print(created_app_id)

client_app_id = get_apps('admin/v1/Apps', access, {"filter" : "displayname eq \"" + "Postman" + "\"",
                                "attributes" : "id"})

print(client_app_id)

get_approle_for_app('admin/v1/AppRoles', access, {"filter" : "displayname co \"" + "Identity Domain Administrator" + "\"",
})


# token_url = "oauth2/v1/token"

# endpoint_url = f'{host}/{token_url}'

# # endpoint_url = f"{host}/{token_url}"
# # endpoint_url = "https://idcs-8d3160e43b1c4592b041b8b93a417830.identity.oraclecloud.com/oauth2/v1/token"

# response = requests.post(endpoint_url, auth=HTTPBasicAuth(client_id, secret), data=data)

# acc_token = json.loads(response.text)
# print(acc_token['access_token'])

# # token = acc_token['access_token']
# # auth = 'Bearer ' + token

# # print(auth)
# # # acc_token = str(acc_token)
# # # print(type(acc_token))


# # # author = 'Bearer' + acc_token
# # # print(author)
# # # data = {'scope' : 'urn:opc:idm:__myscopes__'}
# # headers = {
# #     'Authorization' : auth,
# #     'Content-Type': 'application/json'}
# # endpoint_url = "https://idcs-8d3160e43b1c4592b041b8b93a417830.identity.oraclecloud.com/admin/v1/Users"

# # users = requests.get(endpoint_url, headers=headers)

# # print(users.json())

