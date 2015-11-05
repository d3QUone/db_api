__author__ = 'vladimir'

import traceback

import ujson
from flask import Blueprint, request

from database import update_query, select_query
from .user import get_user_profile


forum_blueprint = Blueprint("forum", __name__, url_prefix="forum")


@forum_blueprint.route("/create/", methods=["POST"])
def create():
    try:
        params = request.json
        # print "*"*50, "\nGot params: {0}\n".format(repr(params)), "*"*50
    except Exception:
        print "forum.create params exception:\n{0}".format(traceback.format_exc())
        return ujson.dumps({"code": 2, "response": "invalid json"})
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
            code = 0
        else:
            forum = "no such user"
            code = 1
    else:
        forum = "invalid request"
        code = 3
    return ujson.dumps({
        "response": forum,
        "code": code,
    })


@forum_blueprint.route("/details/", methods=["GET"])
def detail():
    short_name = request.args.get("forum", None)
    related = request.args.get("related", None)
    if short_name:
        if related and related == "user":
            forum_query = select_query(
                """
SELECT f.`id`, f.`name`, u.`id`, u.`username`, u.`email`, u.`name`, u.`about`, u.`isAnonymous`, flwr.`followee`, flwe.`follower` FROM `forum` f
LEFT JOIN `user` u ON u.`email` = f.`user`
LEFT JOIN `follower` flwr ON flwr.`follower` = u.`email`
LEFT JOIN `follower` flwe ON flwe.`followee` = u.`email`
WHERE f.`short_name` = %s""",
                (short_name, ),
                verbose=True
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
            forum = select_query(
                """SELECT f.`id`, f.`name` FROM `forum` f WHERE f.`short_name` = %s""",
                (short_name, ),
                verbose=False
            )
            forum["short_name"] = short_name
        code = 0
        print "="*50, "\nFORUM DETAILS: {0}\n".format(repr(forum)), "="*50
    else:
        forum = "invalid request"
        code = 3
    return ujson.dumps({
        "response": forum,
        "code": code,
    })


# ######## HELPERS ########
