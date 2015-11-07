__author__ = 'vladimir'

import traceback

import ujson
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
    isApproved = int(bool(params.get("isApproved", None)))
    isHighlighted = int(bool(params.get("isHighlighted", None)))
    isEdited = int(bool(params.get("isEdited", None)))
    isSpam = int(bool(params.get("isSpam", None)))
    isDeleted = int(bool(params.get("isDeleted", None)))
    if date and thread and thread > 0 and message and user and forum:
        thread_obj = select_query(
            "SELECT t.`posts` FROM `thread` t WHERE t.`id` = %s",
            (thread, ),
            verbose=False
        )
        if len(thread_obj) == 1:
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
            "SELECT p.`thread` FROM `post` p WHERE p`isDeleted` = FALSE AND p.`id` = %s",
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
            "SELECT p.`thread` FROM `post` p WHERE p`isDeleted` = 1 AND p.`id` = %s",
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
    if post_id and post_id > 0:
        # simple query
        post_query = select_query(
            "SELECT * FROM `post` p WHERE p.`id` = %s",  # AND p.`isDeleted` = FALSE
            (post_id, ),
            verbose=False
        )
        if len(post_query) == 1:
            post = post_query[0]
            post["date"] = get_date(post["date"])
            code = c_OK
        else:
            post = "Post not found"
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
                update_query(
                    "UPDATE `post` p SET p.`likes` = %s WHERE p.`id` = %s",
                    (post["likes"], post_id, ),
                    verbose=False
                )
                code = c_OK
            elif vote == -1:
                post["dislikes"] += 1
                update_query(
                    "UPDATE `post` p SET p.`dislikes` = %s WHERE p.`id` = %s",
                    (post["dislikes"], post_id, ),
                    verbose=False
                )
                code = c_OK
            else:
                post = "Invalid params passed"
                code = c_INVALID_REQUEST_PARAMS
        else:
            post = "Requested post not found"
            code = c_NOT_FOUND
    else:
        post = "Invalid params passed"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": post,
        "code": code,
    })
