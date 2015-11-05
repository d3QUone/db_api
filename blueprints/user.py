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
        print "*"*50, "\nGot params: {0}\n".format(repr(params)), "*"*50
    except Exception:
        print "user.create exception:\n{0}".format(traceback.format_exc())
        return ujson.dumps({"code": 2, "response": "invalid json"})
    email = params.get("email", None)
    username = params.get("username", None)
    name = params.get("name", None)
    about = params.get("about", None)
    isAnonymous = int(bool(params.get("isAnonymous")))
    if email:
        print "Creating user {0}".format(email)
        r = get_user_porfile(email)
        if not r:
            row_id = update_query(
                "INSERT INTO `user` (`username`, `email`, `name`, `about`, `isAnonymous`) VALUES (%s, %s, %s, %s, %s)",
                (username, email, name, about, isAnonymous, ),
                verbose=True
            )
            user = {
                "id": row_id,
                "email": email,
                "username": username,
                "name": name,
                "about": about,
                "isAnonymous": isAnonymous,
                "followers": [],
                "following": [],
                "subscriptions": [],
            }
            code = 0
        else:
            user = "this user already exist"
            code = 5
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
        print "Detailing user {0}".format(email)
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
        print "Updating user {0}".format(email)
        update_query(
            "UPDATE `user` SET name = %s, about = %s WHERE email = %s",
            (name, about, email, ),
            verbose=True
        )
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


@user_blueprint.route("/follow/", methods=["POST"])
def follow():
    try:
        params = request.json
    except Exception as e:
        print traceback.format_exc()
        return ujson.dumps({"code": 2, "response": "invalid json"})
    follower = params.get("follower", None)  # it's ME :)
    followee = params.get("followee", None)
    if follower and followee:
        print "{0} following {1}".format(follower, followee)  # FOLLOWER FOLLOWS FOLLOWEE
        update_query(
            "INSERT INTO `follower` (`follower`, `followee`) VALUES (%s, %s)",
            (follower, followee, ),
            verbose=True
        )
        user = get_user_porfile(follower)
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
    r = select_query(
        """
SELECT u.`id`, u.`username`, u.`email`, u.`name`, u.`about`, u.`isAnonymous`, flwr.`followee`, flwe.`follower` FROM `user` u
LEFT JOIN `follower` flwr ON flwr.`follower` = u.`email`
LEFT JOIN `follower` flwe ON flwe.`followee` = u.`email`
WHERE `email`=%s
""",
        (email, ),
        verbose=True
    )
    if len(r) > 0:
        # print r
        user = r[0]
        user["isAnonymous"] = bool(user["isAnonymous"])
        user["followers"] = []
        user["following"] = []
        user["subscriptions"] = []
        # for line in r:
        #     user["following"].append(line)
        return user
    else:
        return None
