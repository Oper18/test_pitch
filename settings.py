# coding: utf-8

import os


LOCAL_SALT = os.getenv('SERVER_SALT', '2b886d169a244f9cb760e6d70e3aa17c')
SERVER_SECRET = os.getenv('SERVER_SECRET', '2b886d169a244f9cb760e6d70e3aa17c')
ACCESS_TOKEN_LIFETIME = 24*60*60
REFRESH_TOKEN_LIFETIME = 24*60*60*60

BASEDIR = os.path.dirname(os.path.abspath(__file__))
