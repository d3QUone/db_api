__author__ = 'vladimir'

import traceback
import datetime

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
        print "thread.create params exception:\n{0}".format(traceback.format_exc())
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
        p_id = update_query(
            "INSERT INTO `post` (`date`, `thread`, `message`, `user`, `forum`, `parent`, `isApproved`, `isHighlighted`, `isEdited`, `isSpam`, `isDeleted`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (date, thread, message, user, forum, parent, isApproved, isHighlighted, isEdited, isSpam, isDeleted),
            verbose=False
        )
        post = {
            "id": p_id,
            "message": message,
            "date": date,  # datetime.date.strftime()
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
        code = c_OK
    else:
        post = "Invalid parameters passed"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": post,
        "code": code,
    })


@post_blueprint.route("/details/", methods=["GET"])
def detail():
    post_id = get_int_or_none(request.args.get("post", None))
    try:
        related = request.values.get_list("related")
        print "Related == {0}".format(related)
    except:
        related = []
    if post_id:
        # simple query
        post = select_query(
            "SELECT * FROM `post` p WHERE p.`id` = %s AND p.`isDeleted` = FALSE",
            (post_id, ),
            verbose=False
        )
        if len(post) >= 1:
            post = post[0]
            post["date"] = post["date"].strftime("%Y-%m-%d %H-%M-%S")
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
