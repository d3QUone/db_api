__author__ = 'vladimir'

import ujson

from flask import Blueprint

from database import BaseORM, safe_injection


class PostBase(BaseORM):
    db_table = "Post_t"
    base_url = "/post"


post_manager = PostBase()

post_blueprint = Blueprint("post", __name__)

@post_blueprint.route(post_manager.base_url + "/create", methods=["GET"])
def create():
    return ujson.dumps({"success": True})
