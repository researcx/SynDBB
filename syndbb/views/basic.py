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
    dynamic_css_header = ["css/fluid.css"]
    dynamic_js_footer = ["js/inline.js", "js/bootbox.min.js"]
    return syndbb.render_template('home.html', dynamic_js_footer=dynamic_js_footer, dynamic_css_header=dynamic_css_header)

@syndbb.app.route('/robots.txt')
def robotstxt():
    return send_from_directory(syndbb.app.static_folder, syndbb.request.path[1:])

@syndbb.app.route('/favicon.ico')
def faviconico():
    return send_from_directory(syndbb.app.static_folder, syndbb.request.path[1:])

@syndbb.app.route("/chat/")
def chat():
    return syndbb.render_template('chat.html', title="Chat", subheading=[""])

@syndbb.app.route("/terms/")
def terms():
    return syndbb.render_template('terms.html', title="Terms of Service", subheading=[""])

@syndbb.app.route("/rules/")
def rules():
    return syndbb.render_template('rules.html', title="Forum Rules", subheading=[""])

@syndbb.app.route("/chat-rules/")
def chat_rules():
    return syndbb.render_template('chat-rules.html', title="IRC Rules", subheading=[""])

@syndbb.app.route("/info/")
def info():
    return syndbb.render_template('info.html', title="Information", subheading=[""])

@syndbb.app.route("/discord/")
def discord():
    return syndbb.render_template('discord.html', title="Discord", subheading=[""])

@syndbb.app.route("/vidya/")
def vidya():
    title="Video Chat"
    subheading = [""]
    roomName = syndbb.request.args.get('room', '')
    room = False
    if roomName:
        if syndbb.re.match("^[A-Za-z0-9_-]*$", roomName):
            room = roomName
            subheading.append("<a href='/vidya/'>Video Chat</a>")
            title=roomName
        else:
            syndbb.flash('Room name can only contain letters and numbers.', 'danger')
    return syndbb.render_template('vidya.html', room=room, title=title, subheading=subheading)
