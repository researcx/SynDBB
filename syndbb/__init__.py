#
# Copyright (c) 2017 - 2020 Keira T (https://kei.info.gf). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import uuid, time, os, time, re, signal, json
import pkg_resources, platform
import humanize, logging as logging
from datetime import datetime, timedelta

#import flask_monitoringdashboard as dashboard
from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash
from flask import Flask
from flask.views import MethodView
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
logger = logging.getLogger('werkzeug')


# loading config
core_config = ""
config_path = "config.json"

try:
     with open(config_path) as config_file:
          core_config = json.load(config_file)
except:
     logger.info(f"*** Could not load the config from {config_path}.")
     os.kill(os.getpid(), signal.SIGTERM)
else:
     logger.info(f"* Successfully loaded the config from {config_path}.")
app = Flask(__name__)
# App config
app.config.update(dict(
    SQLALCHEMY_DATABASE_URI=core_config['server']['database'],
    SQLALCHEMY_TRACK_MODIFICATIONS="false",
    SECRET_KEY=core_config['server']['secret']
))
app.jinja_env.cache = {}

# LDAP config
if core_config['ldap']['enabled'] :
     from flask_ldapconn import LDAPConn
     LDAP_BASEDN  = core_config['ldap']['base_dn'] 
     app.config.update(dict(
     LDAP_SERVER  = core_config['ldap']['host'] ,
     LDAP_PORT  = core_config['ldap']['port'] ,
     LDAP_CONNECT_TIMEOUT = core_config['ldap']['timeout'],
     LDAP_USE_TLS = core_config['ldap']['tls'],
     LDAP_BINDDN  = core_config['ldap']['user'] ,
     LDAP_SECRET = core_config['ldap']['password']
     ))
     ldap = LDAPConn(app)

# Caching config
if core_config['cache']['type'] == "redis":
     print(" * Cache: Redis")
     cache = Cache(app, config={
          'CACHE_TYPE': 'redis',
          'CACHE_KEY_PREFIX': core_config['redis']['prefix'],
          'CACHE_REDIS_HOST': core_config['redis']['host'],
          'CACHE_REDIS_PORT': core_config['redis']['port'],
          'CACHE_REDIS_URL': core_config['redis']['url']
     })
else:
     print(" * Cache: " + core_config['cache']['type'])
     cache = Cache(app,config={'CACHE_TYPE': core_config['cache']['type']})

# HCaptcha config
if core_config['hcaptcha']['enabled']:
     from flask_hcaptcha import hCaptcha
     hcaptcha = hCaptcha(app)

db = SQLAlchemy(app)
#dashboard.bind(app)
print(" * Initializing...")
import syndbb.initialize
