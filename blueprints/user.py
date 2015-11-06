__author__ = 'vladimir'

import traceback

import ujson
from flask import Blueprint, request

from . import *
from .database import update_query, select_query


user_blueprint = Blueprint("user", __name__, url_prefix="user")


# actually this is get_or_create method
@user_blueprint.route("/create/", methods=["POST"])
def create():
    try:
        params = request.json
        # print "*"*50, "\nGot params: {0}\n".format(repr(params)), "*"*50
    except Exception:
        print "user.create params exception:\n{0}".format(traceback.format_exc())
        return ujson.dumps({"code": c_BAD_REQUEST, "response": "invalid json"})
    email = params.get("email", None)
    username = params.get("username", None)
    name = params.get("name", None)
    about = params.get("about", None)
    isAnonymous = int(bool(params.get("isAnonymous")))
    if email:
        print "Creating user '{0}'".format(email)
        user = get_user_profile(email)
        code = c_OK
        if not user:
            row_id = update_query(
                "INSERT INTO `user` (`username`, `email`, `name`, `about`, `isAnonymous`) VALUES (%s, %s, %s, %s, %s)",
                (username, email, name, about, isAnonymous, ),
                verbose=False
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
        else:
            user = "this user already exist"
            code = c_USER_EXISTS
    else:
        user = "invalid request"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": user,
        "code": code,
    })


@user_blueprint.route("/details/", methods=["GET"])
def detail():
    email = request.args.get("user", None)
    if email:
        print "Detailing user '{0}'".format(email)
        user = get_user_profile(email)
        code = c_OK
        if not user:
            user = "user not found"
            code = c_NOT_FOUND
    else:
        user = "invalid request"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": user,
        "code": code,
    })


@user_blueprint.route("/updateProfile/", methods=["POST"])
def update():
    try:
        params = request.json
    except Exception:
        print "user.updateProfile params exception:\n{0}".format(traceback.format_exc())
        return ujson.dumps({"code": c_BAD_REQUEST, "response": "invalid json"})
    email = params.get("user", None)
    name = params.get("name", None)
    about = params.get("about", None)
    if email and (name or about):
        print "Updating user '{0}'".format(email)
        update_query(
            "UPDATE `user` SET name = %s, about = %s WHERE email = %s",
            (name, about, email, ),
            verbose=False
        )
        user = get_user_profile(email)
        code = c_OK
        if not user:
            user = "Not found"
            code = c_NOT_FOUND
    else:
        user = "Invalid request"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": user,
        "code": code,
    })


@user_blueprint.route("/follow/", methods=["POST"])
def follow():
    try:
        params = request.json
    except Exception:
        print "user.follow params exception:\n{0}".format(traceback.format_exc())
        return ujson.dumps({"code": c_BAD_REQUEST, "response": "invalid json"})
    follower = params.get("follower", None)  # it's ME :)
    followee = params.get("followee", None)
    if follower and followee:
        print "{0} following {1}".format(follower, followee)  # FOLLOWER FOLLOWS FOLLOWEE
        update_query(
            "INSERT INTO `follower` (`follower`, `followee`) VALUES (%s, %s)",
            (follower, followee, ),
            verbose=False
        )
        user = get_user_profile(follower)
        code = c_OK
        if not user:
            user = "Not found"
            code = c_NOT_FOUND
    else:
        user = "Invalid request"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": user,
        "code": code,
    })


@user_blueprint.route("/unfollow/", methods=["POST"])
def unfollow():
    try:
        params = request.json
    except Exception:
        print "user.unfollow params exception:\n{0}".format(traceback.format_exc())
        return ujson.dumps({"code": c_BAD_REQUEST, "response": "invalid json"})
    follower = params.get("follower", None)  # it's ME :)
    followee = params.get("followee", None)
    if follower and followee:
        print "{0} unfollowing {1}".format(follower, followee)  # FOLLOWER FOLLOWS FOLLOWEE
        update_query(
            "DELETE FROM `follower` WHERE `follower`.`follower` = %s AND `follower`.`followee` = %s LIMIT 1",
            (follower, followee, ),
            verbose=False
        )
        user = get_user_profile(follower)
        code = c_OK
        if not user:
            user = "Not found"
            code = c_NOT_FOUND
    else:
        user = "Invalid request"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": user,
        "code": code,
    })


@user_blueprint.route("/listFollowers/", methods=["GET"])
def list_followers():
    email = request.args.get("user", None)
    if email:
        # LEFT JOIN `follower` fol ON fol.`followee` = u.`email`
        r = select_query(
            """
SELECT u.`id`, u.`username`, u.`email`, u.`name`, u.`about`, u.`isAnonymous`, flwr.`followee`, flwe.`follower` FROM `user` u
JOIN `follower` flwr ON flwr.`follower` = u.`email`
JOIN `follower` flwe ON flwe.`followee` = flwr.`follower`
WHERE flwe.`followee`=%s
""",
            (email, ),
            verbose=True
        )
        user = prepare_profiles(r)
        code = c_OK
    else:
        user = "Invalid request"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": user,
        "code": code,
    })


# ######## HELPERS ########

def prepare_profiles(query):
    """Render bunch of profiles from queries result"""
    buf = {}
    for user in query:
        if user["email"] not in buf:
            buf[user["email"]] = {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "name": user["name"],
                "about": user["about"],
                "isAnonymous": bool(user["isAnonymous"]),
                "followers": [],
                "following": [],
                "subscriptions": [],
            }
        else:
            if "followee" in user and user["followee"]:
                buf[user["email"]]["followers"].append(user["followee"])
            if "follower" in user and user["follower"]:
                buf[user["email"]]["following"].append(user["follower"])
    # render list
    res = []
    append = res.append
    for k in buf:
        b = {"email": k}
        b.update(buf[k])
        # TODO: check what is faster
        # b = buf[k]
        # b.update({"email": k})
        append(b)
    return res


def get_user_profile(email):
    """Return full profile + subscribers + followers + following"""
    r = select_query(
        """
SELECT u.`id`, u.`username`, u.`email`, u.`name`, u.`about`, u.`isAnonymous`, flwr.`followee`, flwe.`follower` FROM `user` u
LEFT JOIN `follower` flwr ON flwr.`follower` = u.`email`
LEFT JOIN `follower` flwe ON flwe.`followee` = u.`email`
WHERE `email`=%s
""",
        (email, ),
        verbose=False
    )
    if len(r) > 0:
        user = r[0]
        user["isAnonymous"] = bool(user["isAnonymous"])
        user["followers"] = []
        user["following"] = []
        user["subscriptions"] = []  # TODO: update inserting subscr, don't show until...
        for line in r:
            if "followee" in line and line["followee"]:
                user["followers"].append(line["followee"])
            if "follower" in line and line["follower"]:
                user["following"].append(line["follower"])
        del user["followee"]
        del user["follower"]
        # print "*"*50, "\nUserProfile: {0}\n".format(repr(user)), "*"*50
        return user
    else:
        return None
