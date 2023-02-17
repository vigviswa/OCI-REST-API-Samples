import requests
import os
import logging
import json
from requests.auth import HTTPBasicAuth
import urllib.parse

host = os.environ['HOST_ID']
client_id = os.environ['CLIENT_ID']
secret = os.environ['CLIENT_SECRET']

# Get access token

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
#     # 'Authorization': 'ZDM3YWY1YmJjOTI5NDk2Nzk0ZDRmOWE4NWE3ZWQxNTc6NWNhNzA0NmMtOGFkNi00MGY4LTliZTQtMWJjNDgxZDE2MmQ1',
#     'Authorization': secret,
#     'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
# }

def get_token(endpoint: str):

    data = {
        'grant_type' : 'client_credentials',
        'scope' : 'urn:opc:idm:__myscopes__'
    }

    endpoint_url = f'{host}/{endpoint}'
    response = requests.post(endpoint_url, auth=HTTPBasicAuth(client_id, secret), data=data)
    acc_token = json.loads(response.text)
    return acc_token['access_token']


def get_all_users(endpoint: str, token: str):

    auth = 'Bearer ' + token
    
    headers = {
        'Authorization' : auth,
        'Content-Type': 'application/json'
    }
    endpoint_url = f"{host}/{endpoint}"
    users = requests.get(endpoint_url, headers=headers)
    # print(users.json())


def create_confidential_app(endpoint: str, token: str, displayname: str):

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
app = create_confidential_app('admin/v1/Apps', access, "TestAppDisplayname1")
created_app_id = get_apps('admin/v1/Apps', access, {"filter" : "displayname eq \"" + "TestAppDisplayname1" + "\"",
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

