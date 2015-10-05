__author__ = 'vladimir'

import ujson

from flask import Blueprint

BASE_URL = "/user"

user = Blueprint("user", __name__)


@user.route(BASE_URL + "/create", methods=["GET"])
def create():
    return ujson.dumps({"success": True})
