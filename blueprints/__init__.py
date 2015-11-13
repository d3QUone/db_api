__author__ = 'vladimir'

import datetime


c_OK = 0
c_NOT_FOUND = 1
c_BAD_REQUEST = 2
c_INVALID_REQUEST_PARAMS = 3
c_UNKNOWN_ERROR = 4
c_USER_EXISTS = 5


def get_int_or_none(num):
    try:
        num = int(num)
    except Exception:
        num = None
    return num


def get_date(d):
    return d.strftime("%Y-%m-%d %H:%M:%S")


def check_list(inp, av_params):
    for item in inp:
        if item not in av_params:
            return False
    return True
