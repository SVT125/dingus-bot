from secrets import *
import requests
import validators
import re
import os

GFYCAT_TOKEN = None


def is_flag(s):
    return re.search('-[a-zA-Z][a-zA-Z]*', s)


def is_web_url(s):
    return validators.url(s)


# Returns whether the given path is an absolute/relative path, but not just a file name.
# TODO - Use a more stringent method of checking if a given string is a path versus a file name?
def is_file_path(path):
    return "\\" in path


# Returns either a list of paths or the same path given if they match the input, be it a query or path, smartly.
def find_files(query, return_all=True):
    if is_file_path(query):
        return find_file_by_path(query)
    else:
        return find_files_by_query(query, return_all)


# Returns the file path requested if it exists, otherwise returns None.
# NOTE - This does not attempt to check whether the path resolves up above data\.
def find_file_by_path(path):
    # If the file is in the current directory or a full relative path was specified, this is a shortcut.
    path = 'data\\' + path
    if os.path.isfile(path):
        return path


# Returns all files which contain the query string.
# Use return_all to return either the first file found or all files eligible.
def find_files_by_query(query, return_all=True):
    matched_files = []
    for root, dirs, files in os.walk('data\\'):
        for file_name in files:
            if query in file_name.lower():
                matching_path = os.path.join(root, file_name)
                if not return_all:
                    return matching_path
                matched_files.append(matching_path)
                
    return matched_files


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