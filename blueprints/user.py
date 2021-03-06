__author__ = 'vladimir'

from collections import OrderedDict
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
    except Exception:
        print "user.create params exception:\n{0}".format(traceback.format_exc())
        return ujson.dumps({"code": c_BAD_REQUEST, "response": "invalid json"})
    email = params.get("email", None)
    username = params.get("username", None)
    name = params.get("name", None)
    about = params.get("about", None)
    isAnonymous = int(bool(params.get("isAnonymous")))
    if email:
        user = get_user_profile(email)
        code = c_OK
        if not user:
            print "Creating user '{0}'".format(email)
            row_id = update_query(
                "INSERT INTO `user` (`username`, `email`, `name`, `about`, `isAnonymous`) VALUES (%s, %s, %s, %s, %s)",
                (username, email, name, about, isAnonymous),
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
            (name, about, email),
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

# BUG: blocks transaction
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
        # print "{0} following {1}".format(follower, followee)  # FOLLOWER FOLLOWS FOLLOWEE
        test_q = select_query(
            "SELECT f.`follower`, f.`followee` FROM `follower` f WHERE f.`follower`=%s AND f.`followee`=%s",
            (follower, followee),
            verbose=False
        )
        if len(test_q) == 0:
            user = get_user_profile(follower)
            if user:
                update_query(
                    "INSERT INTO `follower` (`follower`, `followee`) VALUES (%s, %s)",
                    (follower, followee),
                    verbose=False
                )
                code = c_OK
            else:
                user = "Not found"
                code = c_NOT_FOUND
        else:
            user = "This pair already exists"
            code = c_INVALID_REQUEST_PARAMS
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
        # print "{0} unfollowing {1}".format(follower, followee)  # FOLLOWER FOLLOWS FOLLOWEE
        update_query(
            "DELETE FROM `follower` WHERE `follower`.`follower` = %s AND `follower`.`followee` = %s LIMIT 1",
            (follower, followee),
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
    # optional
    limit = get_int_or_none(request.args.get("limit", None))
    since_id = get_int_or_none(request.args.get("since_id", None))
    order = request.args.get("order", "desc")
    if email and order in ("asc", "desc"):
        SQL = """SELECT u.`id`, u.`username`, u.`email`, u.`name`, u.`about`, u.`isAnonymous`,
flwr.`followee`, flwe.`follower`, sub.`thread` FROM `user` u
LEFT JOIN `follower` flwr ON flwr.`follower` = u.`email`
LEFT JOIN `follower` flwe ON flwe.`followee` = u.`email`
LEFT JOIN `subscription` sub ON sub.`user` = u.`email`
WHERE u.`email` IN (SELECT f.`follower` FROM `follower` f WHERE f.`followee` = %s)"""
        params = (email, ),
        if since_id:
            SQL += " AND u.`id` >= %s"
            params += (since_id, )
        SQL += " ORDER BY u.`name` {0}".format(order.upper())
        if limit and limit > 0:
            SQL += " LIMIT %s"
            params += (limit, )
        r = select_query(SQL, params, verbose=False)
        code = c_OK
        if len(r) > 0:
            user = prepare_profiles(r)
        else:
            user = []
    else:
        user = "Invalid request"
        code = c_INVALID_REQUEST_PARAMS
    # print "*"*50, "\nFollowers: {0}\n".format(repr(user)), "*"*50
    return ujson.dumps({
        "response": user,
        "code": code,
    })


@user_blueprint.route("/listFollowing/", methods=["GET"])
def list_following():
    email = request.args.get("user", None)
    # optional
    limit = get_int_or_none(request.args.get("limit", None))
    since_id = get_int_or_none(request.args.get("since_id", None))
    order = request.args.get("order", "desc")
    if email and order in ("asc", "desc"):
        SQL = """SELECT u.`id`, u.`username`, u.`email`, u.`name`, u.`about`, u.`isAnonymous`,
flwr.`followee`, flwe.`follower`, sub.`thread` FROM `user` u
LEFT JOIN `follower` flwr ON flwr.`follower` = u.`email`
LEFT JOIN `follower` flwe ON flwe.`followee` = u.`email`
LEFT JOIN `subscription` sub ON sub.`user` = u.`email`
WHERE u.`email` IN (SELECT f.`followee` FROM `follower` f WHERE f.`follower` = %s)"""
        params = (email, ),
        if since_id:
            SQL += " AND u.`id` >= %s"
            params += (since_id, )
        SQL += " ORDER BY u.`name` {0}".format(order.upper())
        if limit and limit > 0:
            SQL += " LIMIT %s"
            params += (limit, )
        r = select_query(SQL, params, verbose=False)
        code = c_OK
        if len(r) > 0:
            user = prepare_profiles(r)
        else:
            user = []
    else:
        user = "Invalid request"
        code = c_INVALID_REQUEST_PARAMS
    # print "*"*50, "\nFollowing: {0}\n".format(repr(user)), "*"*50
    return ujson.dumps({
        "response": user,
        "code": code,
    })


@user_blueprint.route("/listPosts/", methods=["GET"])
def list_posts():
    email = request.args.get("user", None)
    # optional
    limit = get_int_or_none(request.args.get("limit", None))
    since = request.args.get("since", None)
    order = request.args.get("order", "desc")
    if email and order in ("asc", "desc"):
        SQL = "SELECT * FROM `post` p WHERE p.`user` = %s"
        params = (email, ),
        if since:
            SQL += " AND p.`date` >= %s"
            params += (since, )
        SQL += " ORDER BY p.`date` {0}".format(order.upper())
        if limit and limit > 0:
            SQL += " LIMIT %s"
            params += (limit, )
        user = select_query(SQL, params, verbose=False)
        code = c_OK
        if len(user) > 0:
            for item in user:
                item["date"] = get_date(item["date"])
        else:
            user = []
    else:
        user = "Invalid request"
        code = c_INVALID_REQUEST_PARAMS
    # print "*"*50, "\nUserPosts: {0}\n".format(repr(user)), "*"*50
    return ujson.dumps({
        "response": user,
        "code": code,
    })


# ######## HELPERS ########

def prepare_profiles(query, limit=None):
    """Render bunch of profiles from queries result"""
    buf = OrderedDict()
    i = 0
    while i < len(query):
        user = query[i]
        # print "user-{0} = {1}\n".format(i, user), "-"*50
        if user["email"] not in buf:
            if (limit and len(buf.keys()) < limit) or not limit:
                # print "Keys={0}".format(len(buf.keys()))
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
        if "follower" in user and user["follower"] and user["email"] in buf:
            buf[user["email"]]["followers"].append(user["follower"])
        if "followee" in user and user["followee"] and user["email"] in buf:
            buf[user["email"]]["following"].append(user["followee"])
        if "thread" in user and user["thread"] and user["email"] in buf:
            if not user["thread"] in buf[user["email"]]["subscriptions"]:
                buf[user["email"]]["subscriptions"].append(user["thread"])
        i += 1
    # render list saving the order
    res = []
    append = res.append
    for k in buf:
        b = buf[k]
        b.update({"email": k})
        append(b)
    return res


def get_user_profile(email):
    """Return full profile + subscribers + followers + following"""
    r = select_query(
        """SELECT u.`id`, u.`username`, u.`email`, u.`name`, u.`about`, u.`isAnonymous`,
flwr.`followee`, flwe.`follower`, sub.`thread` FROM `user` u
LEFT JOIN `follower` flwr ON flwr.`follower` = u.`email`
LEFT JOIN `follower` flwe ON flwe.`followee` = u.`email`
LEFT JOIN `subscription` sub ON sub.`user` = u.`email`
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
            if "follower" in line and line["follower"]:
                user["followers"].append(line["follower"])
            if "followee" in line and line["followee"]:
                user["following"].append(line["followee"])
            if "thread" in line and line["thread"]:
                user["subscriptions"].append(line["thread"])
        del user["followee"]
        del user["follower"]
        del user["thread"]
        # print "*"*50, "\nUserProfile: {0}\n".format(repr(user)), "*"*50
        return user
    else:
        return None
