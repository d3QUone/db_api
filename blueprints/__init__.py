__author__ = 'vladimir'

import datetime


c_OK = 0
c_NOT_FOUND = 1
c_BAD_REQUEST = 2
c_INVALID_REQUEST_PARAMS = 3
c_UNKNOWN_ERROR = 4
c_USER_EXISTS = 5


# returns the same obj but with all data wrapped, recursive
def wrap(string):
    if isinstance(string, list):
        i = 0
        while i < len(string):
            string[i] = wrap(string[i])
            i += 1
        return string
    elif isinstance(string, dict):
        for key in string.keys():
            string[key] = wrap(string[key])
        return string
    elif isinstance(string, str):
        return "`{0}`".format(string.replace("\"", "&quot;").replace("'", "&amp;"))


# Helper func to remove " ' and wrap in `
def safe_injection(func):

    def wrapper(cls, jsondata):
        if not isinstance(jsondata, dict):
            raise Exception("WTF do you send there???")
        for key in jsondata.keys():
            jsondata[key] = wrap(jsondata[key])
        return jsondata

    return wrapper


def get_int_or_none(num):
    try:
        num = int(num)
    except Exception:
        num = None
    return num


def get_date(d):
    return d.strftime("%Y-%m-%d %H:%M:%S")
