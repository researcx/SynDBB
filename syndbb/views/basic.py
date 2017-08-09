#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb
from flask import send_from_directory
import syndbb.models.time
import syndbb.models.activity
import syndbb.models.version

@syndbb.app.route("/")
def home():
    dynamic_js_footer = ["js/inline.js", "js/bootbox.min.js"]
    return syndbb.render_template('home.html', dynamic_js_footer=dynamic_js_footer)

@syndbb.app.route('/robots.txt')
def robotstxt():
    return send_from_directory(syndbb.app.static_folder, syndbb.request.path[1:])

@syndbb.app.route('/favicon.ico')
def faviconico():
    return send_from_directory(syndbb.app.static_folder, syndbb.request.path[1:])

@syndbb.app.route("/chat/")
def chat():
    return syndbb.render_template('chat.html', title="Chat")

@syndbb.app.route("/terms/")
def terms():
    return syndbb.render_template('terms.html', title="Terms of Service")

@syndbb.app.route("/rules/")
def rules():
    return syndbb.render_template('rules.html', title="Forum Rules")

@syndbb.app.route("/chat-rules/")
def chat_rules():
    return syndbb.render_template('chat-rules.html', title="IRC Rules")

@syndbb.app.route("/info/")
def info():
    return syndbb.render_template('info.html', title="Information")
