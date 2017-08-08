#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb, logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify
from time import strftime
import traceback

# Core Pages
import syndbb.views.basic

# User Pages
import syndbb.views.auth
import syndbb.views.invites
import syndbb.views.profile

# Forums, upload, pastebin
import syndbb.views.forums
import syndbb.views.events
import syndbb.views.upload
import syndbb.views.pastebin
import syndbb.views.quotedb
import syndbb.views.emoticons

# Management
import syndbb.views.admin

# Miscellaneous
import syndbb.views.irc_api
import syndbb.views.xmlfeed

#Error Logging
logger = logging.getLogger('werkzeug')
logFormatStr = '[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
logging.basicConfig(format = logFormatStr, filename = "logs/global.log", level=logging.DEBUG)
formatter = logging.Formatter(logFormatStr,'%m-%d %H:%M:%S')
fileHandler = logging.FileHandler("logs/summary.log")
fileHandler.setLevel(logging.DEBUG)
fileHandler.setFormatter(formatter)
streamHandler = logging.StreamHandler()
streamHandler.setLevel(logging.DEBUG)
streamHandler.setFormatter(formatter)
syndbb.app.logger.addHandler(fileHandler)
syndbb.app.logger.addHandler(streamHandler)

@syndbb.app.errorhandler(Exception)
def exceptions(e):
    tb = traceback.format_exc()
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    logger.error('%s %s %s %s %s 5xx INTERNAL SERVER ERROR\n%s',
        timestamp, request.remote_addr, request.method,
        request.scheme, request.full_path, tb)
    return e.status_code

#Run the main app...
if __name__ == '__main__':
    syndbb.app.run()
