#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb
from flask import send_from_directory, make_response
from syndbb.models.users import d2_user, checkSession, is_banned
import syndbb.models.time
import syndbb.models.activity
import syndbb.models.version

@syndbb.app.route("/activity")
def activity():
    dynamic_js_footer = ["js/inline.js", "js/bootbox.min.js"]
    return syndbb.render_template('home.html', dynamic_js_footer=dynamic_js_footer, title="Activity", subheading=[""])

@syndbb.app.route('/robots.txt')
def robotstxt():
    return send_from_directory(syndbb.app.static_folder, syndbb.request.path[1:])

@syndbb.app.route('/favicon.ico')
def faviconico():
    return send_from_directory(syndbb.app.static_folder, syndbb.request.path[1:])

@syndbb.app.route("/")
def home():
    return syndbb.render_template('chat.html')

@syndbb.app.route("/chat")
def chat():
    return syndbb.render_template('chat.html')

@syndbb.app.route("/im/")
def im():
    hasRoom = syndbb.request.args.get('room', '')
    return syndbb.render_template('chat_integrated.html', hasRoom=hasRoom)

@syndbb.app.route("/im/header/")
def im_header():
    return syndbb.render_template('chat_header.html')


@syndbb.app.route("/terms/")
def terms():
    return syndbb.render_template('terms.html', title="Terms of Service", subheading=[""])

@syndbb.app.route("/rules/")
def rules():
    return syndbb.render_template('rules.html', title="Forum Rules", subheading=[""])

@syndbb.app.route("/chat-rules/")
def chat_rules():
    return syndbb.render_template('chat-rules.html', title="Chat Rules", subheading=[""])

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

@syndbb.app.route("/user-styles/")
def user_styles():
    usercss = ".nick{color: #397FEF !important; font-weight bold !important;}\n"
    style = ""
    users = d2_user.query.all()
    for user in users:
        if user:
            if user.rank >= 900:
                style = "color: #DB0003 !important; font-weight: bold !important;"
            elif user.rank >= 500:
                style = "color: #AC15F2 !important; font-weight: bold !important;"
            elif user.rank >= 100:
                style = "color: #00BC1F !important; font-weight: bold !important;"
            elif user.rank >= 50:
                style = "color: #B56236 !important; font-weight: bold !important;"
            else:
                style = "color: #397FEF !important; font-weight bold !important;"
            if is_banned(user.user_id):
                style = "color: #FF0000 !important; text-decoration: line-through !important;"
        else:
            style = "color: #397FEF !important; font-weight bold !important;"
        usercss += "."+user.username+"{"+style+"}\n"
    response = make_response(usercss)
    response.headers['Content-Type'] = 'text/css'
    return response
