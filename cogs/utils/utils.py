import re
import requests
from secrets import *

GFYCAT_TOKEN = None

def is_flag(s):
    return re.search('-[a-zA-Z][a-zA-Z]*', s)


# Refreshes/gets the gfycat token using client ID/secret. Returns boolean value indicating if the request succeeded.
def refresh_gfy_token(payload=None, refresh=True):
    global GFYCAT_TOKEN
    # The params are either that of an actual gfycat request or one for token auth.
    params = payload if payload else {
        'grant_type': 'refresh' if refresh else 'client_credentials',
        'client_id': GFYCAT_ID,
        'client_secret': GFYCAT_SECRET
    }
    if refresh:
        payload['refresh_token'] = GFYCAT_TOKEN
    r = requests.get('https://api.gfycat.com/v1/oauth/token', params=params).json()
    if 'errorMessage' in r:
        return False
    GFYCAT_TOKEN = r['access_token']
    return True


# A wrapper function which attempts a request to gfycat at the given URL, args, kwargs.
# If the token has expired/was never retrieved, attempt to renew it request_count times before giving up.
def request_gfy(url, request_count=3, *args, **kwargs):
    HEADERS = {
        'Authorization': GFYCAT_TOKEN
    }
    result = requests.get(url, headers=HEADERS, *args, **kwargs)
    if result.status_code == 401:
        for i in range(0, request_count):
            if refresh_gfy_token():
                return requests.get(url, *args, **kwargs)
    else:
        return result
    return None