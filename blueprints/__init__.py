__author__ = 'vladimir'


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
