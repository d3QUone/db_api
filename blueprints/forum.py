__author__ = 'vladimir'

import traceback

import ujson
from flask import Blueprint, request

from . import *
from .database import update_query, select_query
from .user import get_user_profile, prepare_profiles


forum_blueprint = Blueprint("forum", __name__, url_prefix="forum")


@forum_blueprint.route("/create/", methods=["POST"])
def create():
    try:
        params = request.json
    except Exception:
        print "forum.create params exception:\n{0}".format(traceback.format_exc())
        return ujson.dumps({"code": c_BAD_REQUEST, "response": "invalid json"})
    name = params.get("name", None)
    short_name = params.get("short_name", None)
    email = params.get("user", None)
    if name and short_name and email:
        user = get_user_profile(email)
        if user:
            print "Creating forum '{0}'".format(short_name)
            forum_id = update_query(
                "INSERT INTO `forum` (`name`, `short_name`, `user`) VALUES (%s, %s, %s)",
                (name, short_name, email),
                verbose=False
            )
            forum = {
                "id": forum_id,
                "name": name,
                "short_name": short_name,
                "user": user,
            }
            code = c_OK
        else:
            forum = "no such user"
            code = c_NOT_FOUND
    else:
        forum = "invalid request"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": forum,
        "code": code,
    })


@forum_blueprint.route("/details/", methods=["GET"])
def detail():
    short_name = request.args.get("forum", None)
    related = request.values.getlist("related")
    if short_name:
        if "user" in related:
            forum_query = select_query(
                """
SELECT f.`id`, f.`name`, u.`id`, u.`username`, u.`email`, u.`name`, u.`about`, u.`isAnonymous`, flwr.`followee`, flwe.`follower` FROM `forum` f
LEFT JOIN `user` u ON u.`email` = f.`user`
LEFT JOIN `follower` flwr ON flwr.`follower` = u.`email`
LEFT JOIN `follower` flwe ON flwe.`followee` = u.`email`
WHERE f.`short_name` = %s""",
                (short_name, ),
                verbose=False
            )
            forum_buf = forum_query[0]
            forum = {
                "id": forum_buf["id"],
                "name": forum_buf["name"],
                "short_name": short_name,
                "user": {
                    "id": forum_buf["u.id"],
                    "name": forum_buf["u.name"],
                    "email": forum_buf["email"],
                    "username": forum_buf["username"],
                    "about": forum_buf["about"],
                    "isAnonymous": bool(forum_buf["isAnonymous"]),
                    "followers": [],
                    "following": [],
                    "subscriptions": [],  # TODO: update inserting subscr
                }
            }
            for line in forum_query:
                if "followee" in line and line["followee"]:
                    forum["user"]["followers"].append(line["followee"])
                if "follower" in line and line["follower"]:
                    forum["user"]["following"].append(line["follower"])
        else:
            forum_query = select_query(
                "SELECT * FROM `forum` f WHERE f.`short_name` = %s",
                (short_name, ),
                verbose=False
            )
            forum = forum_query[0]
        code = c_OK
    else:
        forum = "invalid request"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": forum,
        "code": code,
    })


@forum_blueprint.route("/listUsers/", methods=["GET"])
def list_users():
    short_name = request.args.get("forum", None)
    # optional
    limit = get_int_or_none(request.args.get("limit", None))
    since_id = get_int_or_none(request.args.get("since_id", None))  # entities in interval [since_id, max_id]
    order = request.args.get("order", "desc")
    if short_name and order in ("asc", "desc"):
        SQL = """
SELECT u.`id`, u.`username`, u.`email`, u.`name`, u.`about`, u.`isAnonymous`, flwr.`followee`, flwe.`follower` FROM `user` u
LEFT JOIN `post` p ON p.`user` = u.`email`
LEFT JOIN `follower` flwr ON flwr.`follower` = u.`email`
LEFT JOIN `follower` flwe ON flwe.`followee` = u.`email`
WHERE p.`forum` = %s"""
        params = (short_name, )
        if since_id:
            SQL += " AND u.`id` >= %s"
            params += (since_id, )
        SQL += " ORDER BY u.`name` {0}".format(order.upper())
        if limit and limit > 0:
            SQL += " LIMIT %s"
            params += (limit, )

        u_query = select_query(SQL, params, verbose=False)
        if len(u_query) > 0:
            forum = prepare_profiles(u_query)
            code = c_OK
        else:
            forum = "Nothing found"
            code = c_NOT_FOUND
    else:
        forum = "invalid request"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": forum,
        "code": code,
    })


# ######## HELPERS ########
