__author__ = 'vladimir'

import ujson
from flask import Blueprint

from database import update_query, select_query


post_blueprint = Blueprint("post", __name__, url_prefix="post")


@post_blueprint.route("/create/", methods=["POST"])
def create():
    return ujson.dumps({"success": True})
