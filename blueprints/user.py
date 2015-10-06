__author__ = 'vladimir'

import ujson

from flask import Blueprint

from database import BaseORM, safe_injection


class UserBase(BaseORM):
    db_table = "User_t"
    base_url = "/user"


user_manager = UserBase()

user_blueprint = Blueprint("user", __name__)

@user_blueprint.route(user_manager.base_url + "/create", methods=["GET"])
def create():
    return ujson.dumps({"success": True})
