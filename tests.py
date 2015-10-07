__author__ = 'vladimir'

import json

from blueprints import safe_injection


@safe_injection
def t(_, s):
    return s

# TODO: move to class, add case rotators

if __name__ == "__main__":
    inp = {
        "key": "smth with ' inj",
        "related": ["1'", "2'", "3"],
        "chunks": [
            {
                "type": "a",
                "text": "smth with ' inj 2",
            },
            {
                "type": "a",
                "text": "smth with ' inj 3",
            },
            {
                "type": "chunks",
                "chunks": [
                    {
                        "type": "a",
                        "text": "smth with ' inj 4",
                    },
                ]
            },
        ],
        "name": "Vladimir",
        "last_name": "Oiaod\" or 1=1"
    }
    outp = t(None, inp)
    print "Testing wrapper:\nInput:"
    print json.dumps(inp, separators=(",", ": ", ), indent=4)
    print "-"*70, "\nOutput:"
    print json.dumps(outp, separators=(",", ": ", ), indent=4)
