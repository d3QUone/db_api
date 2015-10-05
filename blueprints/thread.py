__author__ = 'vladimir'

import ujson

from flask import Blueprint

BASE_URL = "/thread"

thread = Blueprint("thread", __name__)


@thread.route(BASE_URL + "/create", methods=["GET"])
def create():
    return ujson.dumps({"success": True})
