__author__ = 'vladimir'

import traceback

# import ujson
import json as ujson
from flask import Blueprint, request

from . import *
from .database import update_query, select_query


post_blueprint = Blueprint("post", __name__, url_prefix="post")


@post_blueprint.route("/create/", methods=["POST"])
def create():
    try:
        params = request.json
        # print "*"*50, "\nPost.Create got params: {0}\n".format(repr(params)), "*"*50
    except Exception:
        print "post.create params exception:\n{0}".format(traceback.format_exc())
        return ujson.dumps({"code": c_BAD_REQUEST, "response": "invalid json"})
    # required
    date = params.get("date", None)
    thread = get_int_or_none(params.get("thread", None))
    message = params.get("message", None)
    user = params.get("user", None)
    forum = params.get("forum", None)
    # optional
    parent = get_int_or_none(params.get("parent", None))
    isApproved = bool(params.get("isApproved", None))
    isHighlighted = bool(params.get("isHighlighted", None))
    isEdited = bool(params.get("isEdited", None))
    isSpam = bool(params.get("isSpam", None))
    isDeleted = bool(params.get("isDeleted", None))
    if date and thread and thread > 0 and message and user and forum:
        thread_obj = select_query(
            "SELECT t.`posts` FROM `thread` t WHERE t.`id` = %s",
            (thread, ),
            verbose=False
        )
        if len(thread_obj) == 1:
            test_q = select_query(
                "SELECT * FROM `post` p WHERE p.`user` = %s AND p.`date` = %s",
                (user, date),
                verbose=False
            )
            if len(test_q) == 0:
                p_id = update_query(
                    "INSERT INTO `post` (`date`, `thread`, `message`, `user`, `forum`, `parent`, `isApproved`, `isHighlighted`, `isEdited`, `isSpam`, `isDeleted`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (date, thread, message, user, forum, parent, isApproved, isHighlighted, isEdited, isSpam, isDeleted),
                    verbose=False
                )
                post = {
                    "id": p_id,
                    "message": message,
                    "date": date,
                    "thread": thread,
                    "user": user,
                    "parent": parent,
                    "isApproved": isApproved,
                    "isDeleted": isDeleted,
                    "isEdited": isEdited,
                    "isSpam": isSpam,
                    "isHighlighted": isHighlighted,
                    "forum": forum,
                }
                # update post amount in thread ...
                thread_obj[0]["posts"] += 1
                update_query(
                    "UPDATE `thread` SET `posts` = %s WHERE `id` = %s",
                    (thread_obj[0]["posts"], thread),
                    verbose=False
                )
                code = c_OK
            else:
                post = "This post already exists"
                code = c_INVALID_REQUEST_PARAMS
        else:
            post = "No such thread"
            code = c_NOT_FOUND
    else:
        post = "Invalid parameters passed"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": post,
        "code": code,
    })


@post_blueprint.route("/update/", methods=["POST"])
def update():
    try:
        params = request.json
    except Exception:
        print "post.update params exception:\n{0}".format(traceback.format_exc())
        return ujson.dumps({"code": c_BAD_REQUEST, "response": "invalid json"})
    # required
    post_id = get_int_or_none(params.get("post", None))
    message = params.get("message", None)
    if post_id and post_id > 0 and message:
        post_query = select_query(
            "SELECT * from `post` p WHERE p.`id` = %s",
            (post_id, ),
            verbose=False
        )
        if len(post_query) == 1:
            update_query(
                "UPDATE `post` SET `message` = %s WHERE `id` = %s",
                (message, post_id),
                verbose=False
            )
            post = post_query[0]
            post["date"] = get_date(post["date"])
            post["message"] = message
            code = c_OK
        else:
            post = "This post doesn't exist"
            code = c_NOT_FOUND
    elif post_id and post_id < 0:
        post = "Not found"
        code = c_NOT_FOUND
    else:
        post = "Invalid params"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": post,
        "code": code,
    })


@post_blueprint.route("/remove/", methods=["POST"])
def remove():
    try:
        params = request.json
    except Exception:
        print "post.remove params exception:\n{0}".format(traceback.format_exc())
        return ujson.dumps({"code": c_BAD_REQUEST, "response": "invalid json"})
    post_id = get_int_or_none(params.get("post", None))
    if post_id and post_id > 0:
        post_query = select_query(
            "SELECT p.`thread` FROM `post` p WHERE p.`isDeleted` = 0 AND p.`id` = %s",
            (post_id, ),
            verbose=False
        )
        if len(post_query) == 1:
            update_query(
                "UPDATE `post` SET `isDeleted` = 1 WHERE `id` = %s",
                (post_id, ),
                verbose=False
            )
            # update post amount in thread ...
            thread = post_query[0]["thread"]
            thread_obj = select_query(
                "SELECT t.`posts` FROM `thread` t WHERE t.`id` = %s",
                (thread, ),
                verbose=False
            )
            thread_obj[0]["posts"] -= 1
            update_query(
                "UPDATE `thread` SET `posts` = %s WHERE `id` = %s",
                (thread_obj[0]["posts"], thread),
                verbose=False
            )
            post = {"post": post_id}
            code = c_OK
        else:
            post = "This post doesn't exist"
            code = c_NOT_FOUND
    elif post_id and post_id < 0:
        post = "Not found"
        code = c_NOT_FOUND
    else:
        post = "Invalid params"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": post,
        "code": code,
    })


@post_blueprint.route("/restore/", methods=["POST"])
def restore():
    try:
        params = request.json
    except Exception:
        print "post.restore params exception:\n{0}".format(traceback.format_exc())
        return ujson.dumps({"code": c_BAD_REQUEST, "response": "invalid json"})
    post_id = get_int_or_none(params.get("post", None))
    if post_id and post_id > 0:
        post_query = select_query(
            "SELECT p.`thread` FROM `post` p WHERE p.`isDeleted` = 1 AND p.`id` = %s",
            (post_id, ),
            verbose=False
        )
        if len(post_query) == 1:
            update_query(
                "UPDATE `post` SET `isDeleted` = 0 WHERE `id` = %s",
                (post_id, ),
                verbose=False
            )
            # update post amount in thread ...
            thread = post_query[0]["thread"]
            thread_obj = select_query(
                "SELECT t.`posts` FROM `thread` t WHERE t.`id` = %s",
                (thread, ),
                verbose=False
            )
            thread_obj[0]["posts"] += 1
            update_query(
                "UPDATE `thread` SET `posts` = %s WHERE `id` = %s",
                (thread_obj[0]["posts"], thread),
                verbose=False
            )
            post = {"post": post_id}
            code = c_OK
        else:
            post = "This post doesn't exist"
            code = c_NOT_FOUND
    elif post_id and post_id < 0:
        post = "Not found"
        code = c_NOT_FOUND
    else:
        post = "Invalid params"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": post,
        "code": code,
    })


@post_blueprint.route("/details/", methods=["GET"])
def detail():
    post_id = get_int_or_none(request.args.get("post", None))
    related = request.values.getlist("related")
    if post_id and post_id > 0 and check_list(related, ("user", "thread", "forum")):
        SQL = "SELECT * FROM `post` p"
        if "user" in related:
            SQL += " JOIN `user` u ON p.`user` = u.`email`"
        if "thread" in related:
            SQL += " JOIN `thread` t ON p.`thread` = t.`id`"
        if "forum" in related:
            SQL += " JOIN `forum` f ON p.`forum` = f.`short_name`"
        SQL += " WHERE p.`id` = %s"
        post_query = select_query(SQL, (post_id, ), verbose=False)
        if len(post_query) == 1:
            post = post_query[0]
            post["date"] = get_date(post["date"])
            if "user" in related:
                post["user"] = {
                    "id": post["u.id"],
                    "email": post["email"],
                    "username": post["username"],
                    "name": post["name"],
                    "isAnonymous": post["isAnonymous"],
                    "about": post["about"],
                }
                del post["u.id"]
                del post["email"]
                del post["username"]
                del post["name"]
                del post["isAnonymous"]
                del post["about"]
            if "thread" in related:
                post["thread"] = {
                    "id": post["t.id"],
                    "title": post["title"],
                    "date": get_date(post["t.date"]),
                    "message": post["t.message"],
                    "forum": post["t.forum"],
                    "user": post["t.user"],
                    "isDeleted": post["t.isDeleted"],
                    "isClosed": post["isClosed"],
                    "slug": post["slug"],
                    "likes": post["t.likes"],
                    "dislikes": post["t.dislikes"],
                    "points": post["t.points"],
                    "posts": post["posts"],
                }
                del post["t.id"]
                del post["title"]
                del post["t.date"]
                del post["t.message"]
                del post["t.forum"]
                del post["t.user"]
                del post["t.isDeleted"]
                del post["isClosed"]
                del post["slug"]
                del post["t.likes"]
                del post["t.dislikes"]
                del post["t.points"]
                del post["posts"]
            if "forum" in related:
                post["forum"] = {
                    "id": post["f.id"],
                    "user": post["f.user"],
                    "short_name": post["short_name"],
                    "name": post["f.name"] if "f.name" in post else "",
                }
                del post["f.id"]
                del post["f.user"]
                del post["short_name"]
                if "f.name" in post:
                    del post["f.name"]
            code = c_OK
        else:
            post = "Post not found"
            code = c_NOT_FOUND
    elif post_id and post_id < 0:
        post = "Not found"
        code = c_NOT_FOUND
    else:
        post = "Invalid params"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": post,
        "code": code,
    })


@post_blueprint.route("/vote/", methods=["POST"])
def vote_post():
    try:
        params = request.json
    except Exception:
        print "post.vote params exception:\n{0}".format(traceback.format_exc())
        return ujson.dumps({"code": c_BAD_REQUEST, "response": "invalid json"})
    post_id = get_int_or_none(params.get("post", None))
    vote = get_int_or_none(params.get("vote", None))
    if post_id and post_id > 0 and vote:
        post_query = select_query(
            "SELECT * FROM `post` p WHERE p.`id` = %s",
            (post_id, ),
            verbose=False
        )
        if len(post_query) == 1:
            post = post_query[0]
            if vote == 1:
                post["likes"] += 1
                post["points"] = post["likes"] - post["dislikes"]
                update_query(
                    "UPDATE `post` p SET p.`likes` = %s, p.`points` = %s WHERE p.`id` = %s",
                    (post["likes"], post["points"], post_id),
                    verbose=False
                )
                code = c_OK
            elif vote == -1:
                post["dislikes"] += 1
                post["points"] = post["likes"] - post["dislikes"]
                update_query(
                    "UPDATE `post` p SET p.`dislikes` = %s, p.`points` = %s WHERE p.`id` = %s",
                    (post["dislikes"], post["points"], post_id),
                    verbose=False
                )
                code = c_OK
            else:
                post = "Invalid params passed"
                code = c_INVALID_REQUEST_PARAMS
        else:
            post = "Requested post not found"
            code = c_NOT_FOUND
    elif post_id and post_id < 0:
        post = "Not found"
        code = c_NOT_FOUND
    else:
        post = "Invalid params passed"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": post,
        "code": code,
    })


@post_blueprint.route("/list/", methods=["GET"])
def list_posts():
    forum = request.args.get("forum", None)
    thread = get_int_or_none(request.args.get("thread", None))
    # optional
    since = request.args.get("since", None)
    limit = get_int_or_none(request.args.get("limit", None))
    order = request.args.get("order", "desc")
    if (forum or thread) and order in ("asc", "desc"):
        post = "No posts match this request"
        code = c_NOT_FOUND
        # ensure that thread or forum exist
        if forum:
            SQL = "SELECT f.`id` FROM `forum` f WHERE f.`short_name` = %s"
            params = (forum, )
        else:
            SQL = "SELECT t.`slug` FROM `thread` t WHERE t.`id` = %s"
            params = (thread, )
        pre_query = select_query(SQL, params, verbose=False)
        if len(pre_query) == 1:
            if forum:
                SQL = "SELECT * FROM `post` p WHERE p.`forum` = %s"
            else:
                SQL = "SELECT * FROM `post` p WHERE p.`thread` = %s"
            if since:
                SQL += " AND p.`date` >= %s"
                params += (since, )
            SQL += " ORDER BY p.`date` {0}".format(order.upper())
            if limit and limit > 0:
                SQL += " LIMIT %s"
                params += (limit, )
            post = select_query(SQL, params, verbose=False)
            code = c_OK
            if len(post) > 0:
                for item in post:
                    item["date"] = get_date(item["date"])
    else:
        post = "Invalid params passed"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": post,
        "code": code,
    })
