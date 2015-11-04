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
    except Exception as e:
        print traceback.format_exc()
        return ujson.dumps({"code": 2})
    email = params.get("email", None)
    username = params.get("username", None)
    name = params.get("name", None)
    about = params.get("about", None)
    isAnonymous = int(bool(params.get("isAnonymous")))
    if email and username and name and about:
        print "Selecting user..."
        r = select_query("""
SELECT u.`username`, u.`email`, u.`name`, u.`about`, u.`isAnonymous` FROM `user` u WHERE `email`='{0}'
""".format(email))
        if len(r) == 0:
            row_id = update_query("""
    INSERT INTO `user` (`username`, `email`, `name`, `about`, `isAnonymous`) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')
    """.format(username, email, name, about, isAnonymous))
            user = {
                "id": row_id,
                "email": email,
                "username": username,
                "name": name,
                "about": about,
                "isAnonymous": isAnonymous,
            }
            code = 5
        else:
            user = r[0]
            code = 0
        return ujson.dumps({
            "response": user,
            "code": code,
        })
    else:
        return ujson.dumps({"code": 3})


