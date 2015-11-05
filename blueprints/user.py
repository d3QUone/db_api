__author__ = 'vladimir'

import traceback

import ujson
from flask import Blueprint, request

from database import update_query, select_query


user_blueprint = Blueprint("user", __name__, url_prefix="user")


# actually this is get_or_create method
@user_blueprint.route("/create/", methods=["POST"])
def create():
    try:
        params = request.json
        print "*"*50
        print "Got params: {0}".format(repr(params))
        print "*"*50
    except Exception as e:
        print traceback.format_exc()
        return ujson.dumps({"code": 2, "response": "invalid json"})
    email = params.get("email", None)
    username = params.get("username", None)
    name = params.get("name", None)
    about = params.get("about", None)
    isAnonymous = int(bool(params.get("isAnonymous")))
    if email:
        print "Selecting user..."
        r = get_user_porfile(email)
        if not r:
            row_id = update_query("""
    INSERT INTO `user` (`username`, `email`, `name`, `about`, `isAnonymous`) VALUES (%s, %s, %s, %s, %s)
    """, (username, email, name, about, isAnonymous, ))
            # print "Row id = {0}".format(row_id)
            user = {
                "id": row_id,
                "email": email,
                "username": username,
                "name": name,
                "about": about,
                "isAnonymous": isAnonymous,
            }
            code = 5
        else:
            user = r
            code = 0
    else:
        code = 3
        user = "invalid request"
    return ujson.dumps({
        "response": user,
        "code": code,
    })


@user_blueprint.route("/details/", methods=["GET"])
def detail():
    email = request.args.get("user", None)
    if email:
        print "Detailing user..."
        r = get_user_porfile(email)
        if r:
            user = r
            code = 0
            print user
        else:
            code = 1
            user = "user not found"
    else:
        code = 3
        user = "invalid request"
    return ujson.dumps({
        "response": user,
        "code": code,
    })


@user_blueprint.route("/updateProfile/", methods=["POST"])
def update():
    try:
        params = request.json
    except Exception as e:
        print traceback.format_exc()
        return ujson.dumps({"code": 2, "response": "invalid json"})
    email = params.get("user", None)
    name = params.get("name", None)
    about = params.get("about", None)
    if email and (name or about):
        print "Updating user..."
        update_query("""UPDATE `user` SET name = %s, about = %s WHERE email = %s""", (email, name, about, ), verbose=True)
        user = get_user_porfile(email)
        if user:
            code = 0
        else:
            code = 1
            user = "Not found"
    else:
        code = 3
        user = "Bad request"
    return ujson.dumps({
        "response": user,
        "code": code,
    })


######## HELPERS ########

def get_user_porfile(email):
    """Return full profile + subscribers + followers + following"""
    r = select_query("""
SELECT u.`id`, u.`username`, u.`email`, u.`name`, u.`about`, u.`isAnonymous` FROM `user` u WHERE `email`='{0}'
""".format(email), verbose=True)
    if len(r) == 1:
        user = r[0]
        user["isAnonymous"] = bool(user["isAnonymous"])
        user["followers"] = []
        user["following"] = []
        user["subscriptions"] = []
        return user
    else:
        return None
