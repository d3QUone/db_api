__author__ = 'vladimir'

# Helper func to remove " ' etc ...

def wrap(string):
    return string.replace("\"", "&quot;").replace("'", "&amp;")


def safe_injection(func):
    def wrapper(cls, jsondata):
        # print cls.__class__
        if not isinstance(jsondata, dict):
            raise Exception("WTF do you send there???")
        for key in jsondata.keys():
            jsondata[key] = wrap(jsondata[key])
        return jsondata
    return wrapper
