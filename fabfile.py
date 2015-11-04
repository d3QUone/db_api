__author__ = 'vladimir'

import os

from fabric.api import *


env.user = "root"
env.host = [""]


'''
https://www.digitalocean.com/community/tutorials/how-to-create-a-new-user-and-grant-permissions-in-mysql

$ mysql -e 'create database forumdb DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;'

$ mysql --user=root mysql

mysql> create user 'vladimir'@'localhost' identified by 'mail.ru@Password';
mysql> GRANT ALL PRIVILEGES ON *.* TO 'vladimir'@'localhost';
----------------------------------

$ mysql -D forumdb -u root < schema.sql

'''
