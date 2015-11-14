__author__ = 'vladimir'

from collections import OrderedDict
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
            # print "Creating forum '{0}'".format(short_name)
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
    if short_name and check_list(related, ("user", )):
        if "user" in related:
            forum_query = select_query(
                """SELECT f.`id`, f.`name`, u.`id`, u.`username`, u.`email`, u.`name`, u.`about`, u.`isAnonymous`,
flwr.`followee`, flwe.`follower`, sub.`thread` FROM `forum` f
LEFT JOIN `user` u ON u.`email` = f.`user`
LEFT JOIN `follower` flwr ON flwr.`follower` = u.`email`
LEFT JOIN `follower` flwe ON flwe.`followee` = u.`email`
LEFT JOIN `subscription` sub ON sub.`user` = u.`email`
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
                    "subscriptions": [],
                }
            }
            for line in forum_query:
                if "followee" in line and line["followee"]:
                    forum["user"]["followers"].append(line["followee"])
                if "follower" in line and line["follower"]:
                    forum["user"]["following"].append(line["follower"])
                if "thread" in line and line["thread"]:
                    forum["user"]["subscriptions"].append(line["thread"])
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


# TODO: pass test
@forum_blueprint.route("/listUsers/", methods=["GET"])
def list_users():
    short_name = request.args.get("forum", None)
    # optional
    limit = get_int_or_none(request.args.get("limit", None))
    since_id = get_int_or_none(request.args.get("since_id", None))  # entities in interval [since_id, max_id]
    order = request.args.get("order", "desc")
    if short_name and order in ("asc", "desc"):
        SQL = """SELECT u.`id`, u.`username`, u.`email`, u.`name`, u.`about`, u.`isAnonymous`,
flwr.`followee`, flwe.`follower`, sub.`thread` FROM `user` u
LEFT JOIN `post` p ON p.`user` = u.`email`
LEFT JOIN `follower` flwr ON flwr.`follower` = u.`email`
LEFT JOIN `follower` flwe ON flwe.`followee` = u.`email`
LEFT JOIN `subscription` sub ON sub.`user` = u.`email`
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


# TODO: pass test
@forum_blueprint.route("/listPosts/", methods=["GET"])
def list_posts():
    short_name = request.args.get("forum", None)
    # optional
    limit = get_int_or_none(request.args.get("limit", None))
    since = request.args.get("since", None)
    order = request.args.get("order", "desc")
    related = request.values.getlist("related")
    if short_name and check_list(related, ("thread", "forum", "user")):
        SQL = "SELECT * FROM `post` p"
        params = (short_name, )
        if "thread" in related:
            SQL += " LEFT JOIN `thread` t ON t.`id` = p.`thread`"
        if "forum" in related:
            SQL += " LEFT JOIN `forum` f ON f.`short_name` = p.`forum`"
        if "user" in related:
            SQL += """ LEFT JOIN `user` u ON u.`email` = p.`user`
LEFT JOIN `follower` flwr ON flwr.`follower` = u.`email`
LEFT JOIN `follower` flwe ON flwe.`followee` = u.`email`
LEFT JOIN `subscription` sub ON sub.`user` = u.`email`"""
        SQL += " WHERE p.`forum` = %s"
        if since:
            SQL += " AND p.`date` >= %s"
            params += (since, )
        SQL += " ORDER BY p.`date` {0}".format(order.upper())
        if limit and limit > 0:
            SQL += " LIMIT %s"
            params += (limit, )

        posts_query = select_query(SQL, params, verbose=False)
        if len(posts_query) > 0 and len(related) > 0:
            buf = OrderedDict()
            for post in posts_query:
                if post["id"] not in buf:
                    buf[post["id"]] = {
                        "id": post["id"],
                        "message": post["message"],
                        "date": get_date(post["date"]),
                        "thread": post["thread"],
                        "user": post["user"],
                        "parent": post["parent"],
                        "isApproved": bool(post["isApproved"]),
                        "isDeleted": bool(post["isDeleted"]),
                        "isEdited": bool(post["isEdited"]),
                        "isSpam": bool(post["isSpam"]),
                        "isHighlighted": bool(post["isHighlighted"]),
                        "forum": post["forum"],
                        "likes": post["likes"],
                        "dislikes": post["dislikes"],
                        "points": post["points"],
                    }
                if "thread" in related and not isinstance(buf[post["id"]]["thread"], dict):
                    buf[post["id"]]["thread"] = {
                        "id": post["t.id"],
                        "title": post["title"],
                        "date": get_date(post["t.date"]),
                        "message": post["t.message"],
                        "forum": post["t.forum"],
                        "user": post["t.user"],
                        "isDeleted": bool(post["t.isDeleted"]),
                        "isClosed": bool(post["isClosed"]),
                        "slug": post["slug"],
                        "likes": post["t.likes"],
                        "dislikes": post["t.dislikes"],
                        "points": post["t.points"],
                        "posts": post["posts"],
                    }
                if "forum" in related and not isinstance(buf[post["id"]]["forum"], dict):
                    buf[post["id"]]["forum"] = {
                        "id": post["f.id"],
                        "name": post["name"],
                        "user": post["f.user"],
                        "short_name": post["short_name"],
                    }
                if "user" in related and not isinstance(buf[post["id"]]["user"], dict):
                    buf[post["id"]]["user"] = {
                        "id": post["id"],
                        "username": post["u.name"],
                        "email": post["email"],
                        "name": post["name"],
                        "about": post["about"],
                        "isAnonymous": bool(post["isAnonymous"]),
                        "followers": [],
                        "following": [],
                        "subscriptions": [],
                    }
                if "user" in related:
                    # flwr.`followee`, flwe.`follower`
                    if "followee" in post and post["followee"]:
                        buf[post["id"]]["user"]["followers"].append(post["followee"])
                    if "flwe.follower" in post and post["flwe.follower"]:
                        buf[post["id"]]["user"]["following"].append(post["flwe.follower"])
                    if "sub.thread" in post and post["sub.thread"]:
                        buf[post["id"]]["user"]["subscriptions"].append(post["sub.thread"])
            forum = []
            append = forum.append
            code = c_OK
            for k in buf:
                append(buf[k])
        elif len(posts_query) > 0:  # no related -> nothing to render
            forum = posts_query
            code = c_OK
        else:
            forum = "Nothing found"
            code = c_NOT_FOUND
    else:
        forum = "Invalid request"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": forum,
        "code": code,
    })


# TODO: pass test
@forum_blueprint.route("/listThreads/", methods=["GET"])
def list_threads():
    short_name = request.args.get("forum", None)
    # optional
    limit = get_int_or_none(request.args.get("limit", None))
    since = request.args.get("since", None)
    order = request.args.get("order", "desc")
    related = request.values.getlist("related")
    if short_name and check_list(related, ("forum", "user")):
        SQL = "SELECT * FROM `thread` t"
        params = (short_name, )
        if "forum" in related:
            SQL += " LEFT JOIN `forum` f ON f.`short_name` = t.`forum`"
        if "user" in related:
            SQL += """ LEFT JOIN `user` u ON u.`email` = t.`user`
LEFT JOIN `follower` flwr ON flwr.`follower` = u.`email`
LEFT JOIN `follower` flwe ON flwe.`followee` = u.`email`
LEFT JOIN `subscription` sub ON sub.`user` = u.`email`"""
        SQL += " WHERE t.`isDeleted` = FALSE AND t.`forum` = %s"
        if since:
            SQL += " AND t.`date` >= %s"
            params += (since, )
        SQL += " ORDER BY t.`date` {0}".format(order.upper())
        if limit and limit > 0:
            SQL += " LIMIT %s"
            params += (limit, )

        # TODO: rename to 'thread'
        posts_query = select_query(SQL, params, verbose=False)
        if len(posts_query) > 0 and len(related) > 0:
            buf = OrderedDict()
            for post in posts_query:
                if post["id"] not in buf:
                    buf[post["id"]] = {
                        "id": post["id"],
                        "title": post["title"],
                        "date": get_date(post["date"]),
                        "message": post["message"],
                        "forum": post["forum"],
                        "user": post["user"],
                        "isDeleted": bool(post["isDeleted"]),
                        "isClosed": bool(post["isClosed"]),
                        "slug": post["slug"],
                        "likes": post["likes"],
                        "dislikes": post["dislikes"],
                        "points": post["points"],
                        "posts": post["posts"],
                    }
                if "forum" in related and not isinstance(buf[post["id"]]["forum"], dict):
                    buf[post["id"]]["forum"] = {
                        "id": post["f.id"],
                        "name": post["name"],
                        "user": post["f.user"],
                        "short_name": post["short_name"],
                    }
                if "user" in related and not isinstance(buf[post["id"]]["user"], dict):
                    buf[post["id"]]["user"] = {
                        "id": post["id"],
                        "username": post["u.name"],
                        "email": post["email"],
                        "name": post["name"],
                        "about": post["about"],
                        "isAnonymous": bool(post["isAnonymous"]),
                        "followers": [],
                        "following": [],
                        "subscriptions": [],
                    }
                if "user" in related:
                    # flwr.`followee`, flwe.`follower`
                    if "followee" in post and post["followee"]:
                        buf[post["id"]]["user"]["followers"].append(post["followee"])
                    if "flwe.follower" in post and post["flwe.follower"]:
                        buf[post["id"]]["user"]["following"].append(post["flwe.follower"])
                    if "sub.thread" in post and post["sub.thread"]:
                        buf[post["id"]]["user"]["subscriptions"].append(post["sub.thread"])
            forum = []
            append = forum.append
            code = c_OK
            for k in buf:
                append(buf[k])
        elif len(posts_query) > 0:
            forum = posts_query
            code = c_OK
        else:
            forum = "Nothing found"
            code = c_NOT_FOUND
    else:
        forum = "Invalid request"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": forum,
        "code": code,
    })
