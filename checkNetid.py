import os
import json
import base64
import requests
import urllib.parse

ACCESS_TOKEN_URL = 'https://api.princeton.edu:443/token'
BASE_URL = 'https://api.princeton.edu:443/active-directory/1.0.5'

ENDPOINT = '/users'
# ENDPOINT = '/users/basic'
# ENDPOINT = '/users/full'

CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']

# fetch a name from a given netid
def main(netid):
    # Use the CONSUMER_KEY and CONSUMER_SECRET to get an access token.

    auth_header = CONSUMER_KEY + ":" + CONSUMER_SECRET
    auth_header = bytes(auth_header, 'utf-8')
    auth_header = base64.b64encode(auth_header)
    auth_header = auth_header.decode('utf-8')
    auth_header = 'Basic ' + auth_header
    response = requests.post(
        ACCESS_TOKEN_URL,
        data={'grant_type': 'client_credentials'},
        headers={'Authorization': auth_header})
    response_json_doc = json.loads(response.text)
    access_token = response_json_doc['access_token']

    # Use the access token to get the data.

    auth_header = 'Bearer ' + access_token
    print('Access token:', access_token)
    data_url = BASE_URL + ENDPOINT
    netid = urllib.parse.quote_plus(netid)
    response = requests.get(
        data_url,
        params={'uid': netid},
        headers={'Authorization': auth_header})
    response_json_doc = json.loads(response.text)

    # Pretty-print the data.
    if response_json_doc:
        name = response_json_doc[0]['displayname']
        return name
    return 