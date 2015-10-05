__author__ = 'vladimir'

import ujson

from flask import Blueprint

BASE_URL = "/post"

post = Blueprint("post", __name__)


@post.route(BASE_URL + "/create", methods=["GET"])
def create():
    return ujson.dumps({"success": True})
