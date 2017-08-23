#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash
from flask import Flask
from flask.views import MethodView
from flask_sqlalchemy import SQLAlchemy
from flask_cache import Cache

import uuid, time, os, time, re, signal
import pkg_resources, platform
from datetime import datetime, timedelta
import humanize

#Configuration variables defined in the config file
db = os.environ.get('SYNDBB_DB')
secretkey = os.environ.get('SYNDBB_SECRET')
hashkey = os.environ.get('SYNDBB_HASH')
ircapi = os.environ.get('SYNDBB_IRC_API')

#IRC specific
irc_network_name = os.environ.get('IRC_NETWORK_NAME')
irc_network_address = os.environ.get('IRC_NETWORK_ADDRESS')
irc_network_port = os.environ.get('IRC_NETWORK_PORT')

#ZNC specific
znc_address = os.environ.get('ZNC_ADDRESS')
znc_port = os.environ.get('ZNC_PORT')
znc_user = os.environ.get('ZNC_USER')
znc_password = os.environ.get('ZNC_PASSWORD')

if db == None or secretkey == None or hashkey == None or ircapi == None:
    print("*** No configuration variables defined! Exiting... ***")
    os.kill(os.getpid(), signal.SIGTERM)
if db == "mysql://<user>:<password>@<host>/<database>":
    print("*** Database not configured properly! Exiting... ***")
    os.kill(os.getpid(), signal.SIGTERM)

app = Flask(__name__)
cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_KEY_PREFIX': 'fcache',
    'CACHE_REDIS_HOST': 'localhost',
    'CACHE_REDIS_PORT': '6379',
    'CACHE_REDIS_URL': 'redis://localhost:6379'
    })

app.config.update(dict(
    SQLALCHEMY_DATABASE_URI=db,
    SQLALCHEMY_TRACK_MODIFICATIONS="false",
    SECRET_KEY=secretkey
))
app.jinja_env.cache = {}

db = SQLAlchemy(app)
import syndbb.initialize
