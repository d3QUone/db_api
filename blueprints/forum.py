__author__ = 'vladimir'

import ujson

from flask import Blueprint

BASE_URL = "/forum"

forum = Blueprint("forum", __name__)


@forum.route(BASE_URL + "/create", methods=["GET"])
def create():
    return ujson.dumps({"success": True})
