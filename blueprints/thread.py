__author__ = 'vladimir'

import ujson

from flask import Blueprint

from database import BaseORM, safe_injection


class ThreadBase(BaseORM):
    db_table = "Thread_t"
    base_url = "/thread"


thread_manager = ThreadBase()

thread_blueprint = Blueprint("thread_blueprint", __name__)

@thread_blueprint.route(thread_manager.base_url + "/create", methods=["GET"])
def create():
    return ujson.dumps({"success": True})
