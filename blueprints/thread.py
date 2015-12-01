__author__ = 'vladimir'

import traceback

import ujson
from flask import Blueprint, request

from . import *
from .database import update_query, select_query
from .user import get_user_profile


thread_blueprint = Blueprint("thread_blueprint", __name__, url_prefix="thread")


@thread_blueprint.route("/create/", methods=["POST"])
def create():
    try:
        params = request.json
        # print "*"*50, "\nThread.Create got params: {0}\n".format(repr(params)), "*"*50
    except Exception:
        print "thread.create params exception:\n{0}".format(traceback.format_exc())
        return ujson.dumps({"code": c_BAD_REQUEST, "response": "invalid json"})
    # required
    forum_short_name = params.get("forum", None)
    title = params.get("title", None)
    isClosed = int(bool(params.get("isClosed")))
    user_email = params.get("user", None)
    date = params.get("date", None)
    message = params.get("message", None)
    slug = params.get("slug", None)
    # optional
    isDeleted = int(bool(params.get("isDeleted")))
    if forum_short_name and title and user_email and date and message and slug:
        # check if do not exists
        test_q = select_query(
            "SELECT t.`id` FROM `thread` t WHERE t.`title` = %s",
            (title, ),
            verbose=False
        )
        if len(test_q) == 0:
            th_id = update_query(
                "INSERT INTO `thread` (`forum`, `title`, `isClosed`, `user`, `date`, `message`, `slug`, `isDeleted`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (forum_short_name, title, isClosed, user_email, date, message, slug, isDeleted),
                verbose=False
            )
            thrd = {
                "id": th_id,
                "forum": forum_short_name,
                "title": title,
                "isClosed": isClosed,
                "user": user_email,
                "date": date,
                "message": message,
                "slug": slug,
                "isDeleted": isDeleted,
            }
            code = c_OK
        else:
            thrd = "This thread already exists"
            code = c_INVALID_REQUEST_PARAMS
    else:
        thrd = "Invalid params"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": thrd,
        "code": code,
    })


@thread_blueprint.route("/update/", methods=["POST"])
def update():
    try:
        params = request.json
    except Exception:
        print "thread.update params exception:\n{0}".format(traceback.format_exc())
        return ujson.dumps({"code": c_BAD_REQUEST, "response": "invalid json"})
    th_id = get_int_or_none(params.get("thread", None))
    message = params.get("message", None)
    slug = params.get("slug", None)
    if th_id and th_id > 0 and message and slug:
        thread_query = select_query(
            "SELECT * FROM `thread` t WHERE t.`id` = %s",
            (th_id, ),
            verbose=False
        )
        if len(thread_query) == 1:
            update_query(
                "UPDATE `thread` SET `slug` = %s, `message` = %s WHERE `id` = %s",
                (slug, message, th_id),
                verbose=False
            )
            thrd = thread_query[0]
            thrd["slug"] = slug
            thrd["message"] = message
            code = c_OK
        else:
            thrd = "Thread not found"
            code = c_NOT_FOUND
    elif th_id and th_id < 0:
        thrd = "Not found"
        code = c_NOT_FOUND
    else:
        thrd = "Invalid params"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": thrd,
        "code": code,
    })


@thread_blueprint.route("/details/", methods=["GET"])
def details():
    th_id = get_int_or_none(request.args.get("thread", None))
    related = request.values.getlist("related")
    if th_id and th_id > 0 and check_list(related, ("user", "forum")):
        if "forum" in related:
            thread = select_query(
                "SELECT * FROM `thread` t LEFT JOIN `forum` f ON f.`short_name` = t.`forum` WHERE t.`id` = %s",
                (th_id, ),
                verbose=False
            )
        else:
            thread = select_query(
                "SELECT * FROM `thread` t WHERE t.`id` = %s",  # t.`isDeleted` = FALSE AND
                (th_id, ),
                verbose=False
            )
        if len(thread) > 0:
            code = c_OK
            thrd = thread[0]
            thrd["date"] = get_date(thrd["date"])
            if "forum" in related:
                thrd["forum"] = {
                    "id": thrd["f.id"],
                    "user": thrd["f.user"],
                    "name": thrd["name"],
                    "short_name": thrd["short_name"],
                }
                del thrd["f.id"]
                del thrd["f.user"]
                del thrd["name"]
                del thrd["short_name"]
            if "user" in related:
                user = get_user_profile(thrd["user"])
                if user:
                    thrd["user"] = user
                else:
                    code = c_NOT_FOUND
            # hack
            if bool(thrd["isDeleted"]):
                thrd["posts"] = 0
        else:
            thrd = "Thread not found"
            code = c_NOT_FOUND
    elif th_id and th_id < 0:
        thrd = "Not found"
        code = c_NOT_FOUND
    else:
        thrd = "Invalid params"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": thrd,
        "code": code,
    })


@thread_blueprint.route("/list/", methods=["GET"])
def list_threads():
    email = request.args.get("user", None)
    forum = request.args.get("forum", None)
    # optional
    since = request.args.get("since", None)
    limit = get_int_or_none(request.args.get("limit", None))
    order = request.args.get("order", "desc")
    if (email or forum) and order in ("desc", "asc"):
        if email:
            SQL = "SELECT * FROM `thread` t WHERE t.`user` = %s"
            params = (email, )
        else:
            SQL = "SELECT * FROM `thread` t WHERE t.`forum` = %s"
            params = (forum, )
        
        if since:
            SQL += " AND t.`date` >= %s"
            params += (since, )
        SQL += " ORDER BY t.`date` {0}".format(order.upper())
        if limit and limit > 0:
            SQL += " LIMIT %s"
            params += (limit, )
        thrd = select_query(SQL, params, verbose=False)
        if len(thrd) > 0:
            for item in thrd:
                item["date"] = get_date(item["date"])
        code = c_OK
    else:
        thrd = "Invalid params"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": thrd,
        "code": code,
    })


# TODO: pass test
# TODO: thread.listPosts
@thread_blueprint.route("/listPosts/", methods=["GET"])
def list_posts():
    th_id = get_int_or_none(request.args.get("thread", None))
    # optional
    since = request.args.get("since", None)
    limit = get_int_or_none(request.args.get("limit", None))
    sort = request.args.get("sort", "flat")
    order = request.args.get("order", "desc")
    if th_id and th_id > 0 and sort in ("flat", "tree", "parent_tree") and order in ("asc", "desc"):
        if sort == "flat":
            # t.`isDeleted` = FALSE AND
            SQL = "SELECT p.* FROM `post` p LEFT JOIN `thread` t ON t.`id` = p.`thread` WHERE p.`thread` = %s"
            params = (th_id, )
            if since:
                SQL += " AND p.`date` >= %s"
                params += (since, )
            SQL += " ORDER BY p.`date` {0}".format(order.upper())
            if limit and limit > 0:
                SQL += " LIMIT %s"
                params += (limit, )
        elif sort == "tree":
            SQL = "SELECT p.* FROM `post` p LEFT JOIN `thread` t ON t.`id` = p.`thread` WHERE p.`thread` = %s"
            params = (th_id, )
            if since:
                SQL += " AND p.`date` >= %s"
                params += (since, )
            SQL += " ORDER BY p.`parent`, p.`date` {0}".format(order.upper())
            if limit and limit > 0:
                SQL += " LIMIT %s"
                params += (limit, )
        else:
            # TODO: parent tree sort
            SQL = None
            params = None
        thrd = select_query(SQL, params, verbose=False)  # posts query
        code = c_OK
        if len(thrd) > 0:
            for item in thrd:
                item["date"] = get_date(item["date"])
                item["isApproved"] = bool(item["isApproved"])
                item["isDeleted"] = bool(item["isDeleted"])
                item["isEdited"] = bool(item["isEdited"])
                item["isSpam"] = bool(item["isSpam"])
                item["isHighlighted"] = bool(item["isHighlighted"])
    elif th_id and th_id < 0:
        thrd = "Not found"
        code = c_NOT_FOUND
    else:
        thrd = "Invalid params"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": thrd,
        "code": code,
    })


@thread_blueprint.route("/subscribe/", methods=["POST"])
def subscribe():
    try:
        params = request.json
    except Exception:
        print "thread.close params exception:\n{0}".format(traceback.format_exc())
        return ujson.dumps({"code": c_BAD_REQUEST, "response": "invalid json"})
    th_id = get_int_or_none(params.get("thread", None))
    email = params.get("user", None)
    if th_id and th_id > 0 and email:
        user = get_user_profile(email)
        old_subs = select_query(
            "SELECT * FROM `subscription` s WHERE s.`user` = %s AND s.`thread` = %s",
            (email, th_id),
            verbose=False
        )
        if user and len(old_subs) == 0:
            update_query(
                "INSERT INTO `subscription` (`user`, `thread`) VALUES (%s, %s)",
                (email, th_id),
                verbose=False
            )
            thrd = {
                "user": email,
                "thread": th_id,
            }
            code = c_OK
        # elif user and len(old_subs) > 0:
        #     thread = "Already created"
        #     code = ?
        else:
            thrd = "No such thread"
            code = c_INVALID_REQUEST_PARAMS
    elif th_id and th_id < 0:
        thrd = "Not found"
        code = c_NOT_FOUND
    else:
        thrd = "Invalid params passed"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": thrd,
        "code": code,
    })


@thread_blueprint.route("/unsubscribe/", methods=["POST"])
def unsubscribe():
    try:
        params = request.json
    except Exception:
        print "thread.close params exception:\n{0}".format(traceback.format_exc())
        return ujson.dumps({"code": c_BAD_REQUEST, "response": "invalid json"})
    th_id = get_int_or_none(params.get("thread", None))
    email = params.get("user", None)
    if th_id and th_id > 0 and email:
        user = get_user_profile(email)
        # TODO: check if thread exists
        if user:
            update_query(
                "DELETE FROM `subscription` WHERE `subscription`.`user` = %s AND `subscription`.`thread` = %s LIMIT 1",
                (email, th_id),
                verbose=False
            )
            thrd = {
                "user": email,
                "thread": th_id,
            }
            code = c_OK
        else:
            thrd = "No such thread"
            code = c_INVALID_REQUEST_PARAMS
    elif th_id and th_id < 0:
        thrd = "Not found"
        code = c_NOT_FOUND
    else:
        thrd = "Invalid params passed"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": thrd,
        "code": code,
    })


@thread_blueprint.route("/vote/", methods=["POST"])
def vote_thread():
    try:
        params = request.json
    except Exception:
        print "thread.vote params exception:\n{0}".format(traceback.format_exc())
        return ujson.dumps({"code": c_BAD_REQUEST, "response": "invalid json"})
    th_id = get_int_or_none(params.get("thread", None))
    vote = get_int_or_none(params.get("vote", None))
    if th_id and th_id > 0 and vote:
        thread = select_query(
            "SELECT * FROM `thread` t WHERE t.`id` = %s",
            (th_id, ),
            verbose=False
        )
        if len(thread) > 0:
            thrd = thread[0]
            if vote == 1:
                thrd["likes"] += 1
                thrd["points"] = thrd["likes"] - thrd["dislikes"]
                update_query(
                    "UPDATE `thread` t SET t.`likes` = %s, t.`points` = %s WHERE t.`id` = %s",
                    (thrd["likes"], thrd["points"], th_id),
                    verbose=False
                )
                code = c_OK
            elif vote == -1:
                thrd["dislikes"] += 1
                thrd["points"] = thrd["likes"] - thrd["dislikes"]
                update_query(
                    "UPDATE `thread` t SET t.`dislikes` = %s, t.`points` = %s WHERE t.`id` = %s",
                    (thrd["dislikes"], thrd["points"], th_id),
                    verbose=False
                )
                code = c_OK
            else:
                thrd = "Invalid params passed"
                code = c_INVALID_REQUEST_PARAMS
        else:
            thrd = "Requested thread not found"
            code = c_NOT_FOUND
    elif th_id and th_id < 0:
        thrd = "Not found"
        code = c_NOT_FOUND
    else:
        thrd = "Invalid params passed"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": thrd,
        "code": code,
    })


# Similar methods goes bellow

@thread_blueprint.route("/close/", methods=["POST"])
def close():
    try:
        params = request.json
    except Exception:
        print "thread.close params exception:\n{0}".format(traceback.format_exc())
        return ujson.dumps({"code": c_BAD_REQUEST, "response": "invalid json"})
    th_id = get_int_or_none(params.get("thread", None))
    if th_id and th_id > 0:
        update_query(
            "UPDATE `thread` t SET t.`isClosed` = TRUE WHERE t.`id` = %s",
            (th_id, ),
            verbose=False
        )
        thrd = {"thread": th_id}
        code = c_OK
    elif th_id and th_id < 0:
        thrd = "Not found"
        code = c_NOT_FOUND
    else:
        thrd = "Invalid params"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": thrd,
        "code": code,
    })


@thread_blueprint.route("/open/", methods=["POST"])
def open():
    try:
        params = request.json
    except Exception:
        print "thread.open params exception:\n{0}".format(traceback.format_exc())
        return ujson.dumps({"code": c_BAD_REQUEST, "response": "invalid json"})
    th_id = get_int_or_none(params.get("thread", None))
    if th_id and th_id > 0:
        update_query(
            "UPDATE `thread` t SET t.`isClosed` = FALSE WHERE t.`id` = %s",
            (th_id, ),
            verbose=False
        )
        thrd = {"thread": th_id}
        code = c_OK
    elif th_id and th_id < 0:
        thrd = "Not found"
        code = c_NOT_FOUND
    else:
        thrd = "Invalid params"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": thrd,
        "code": code,
    })


# TODO: pass test
@thread_blueprint.route("/remove/", methods=["POST"])
def remove():
    try:
        params = request.json
    except Exception:
        print "thread.open params exception:\n{0}".format(traceback.format_exc())
        return ujson.dumps({"code": c_BAD_REQUEST, "response": "invalid json"})
    th_id = get_int_or_none(params.get("thread", None))
    if th_id and th_id > 0:
        update_query(
            # , t.`posts` = 0
            "UPDATE `thread` t SET t.`isDeleted` = TRUE WHERE t.`id` = %s",
            (th_id, ),
            verbose=False
        )
        update_query(
            "UPDATE `post` p SET p.`isDeleted` = TRUE WHERE p.`thread` = %s",
            (th_id, ),
            verbose=False
        )
        thrd = {"thread": th_id}
        code = c_OK
    elif th_id and th_id < 0:
        thrd = "Not found"
        code = c_NOT_FOUND
    else:
        thrd = "Invalid params"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": thrd,
        "code": code,
    })


# TODO: pass test
@thread_blueprint.route("/restore/", methods=["POST"])
def restore():
    try:
        params = request.json
    except Exception:
        print "thread.open params exception:\n{0}".format(traceback.format_exc())
        return ujson.dumps({"code": c_BAD_REQUEST, "response": "invalid json"})
    th_id = get_int_or_none(params.get("thread", None))
    if th_id and th_id >= 0:
        # s = select_query(
        #     "SELECT COUNT(p.`id`) AS `C` FROM `post` p WHERE p.`thread` = %s",
        #     (th_id, ),
        #     verbose=False
        # )
        # print "Count = {0}".format(s[0]) , t.`posts` = %s
        update_query(
            "UPDATE `thread` t SET t.`isDeleted` = FALSE WHERE t.`id` = %s",
            (th_id, ),
            verbose=False
        )
        update_query(
            "UPDATE `post` p SET p.`isDeleted` = FALSE WHERE p.`thread` = %s",
            (th_id, ),
            verbose=False
        )
        thrd = {"thread": th_id}
        code = c_OK
    elif th_id and th_id < 0:
        thrd = "Not found"
        code = c_NOT_FOUND
    else:
        thrd = "Invalid params"
        code = c_INVALID_REQUEST_PARAMS
    return ujson.dumps({
        "response": thrd,
        "code": code,
    })
