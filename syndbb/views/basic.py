#
# Copyright (c) 2017 - 2020 Keira T (https://kei.info.gf). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb
from flask import send_from_directory, make_response
from syndbb.models.users import d2_user, check_session_by_id, check_ban_by_id
import syndbb.models.time
import syndbb.models.activity
import syndbb.models.version

@syndbb.app.route("/")
def home():
    dynamic_js_footer = ["js/inline.js", "js/bootbox.min.js"]
    return syndbb.render_template('home.html', title="Community", subheading=[""], dynamic_js_footer=dynamic_js_footer)

@syndbb.app.route('/robots.txt')
def robotstxt():
    return send_from_directory(syndbb.app.static_folder, syndbb.request.path[1:])

@syndbb.app.route('/favicon.ico')
def faviconico():
    return send_from_directory(syndbb.app.static_folder, syndbb.request.path[1:])

@syndbb.app.route("/activity")
def activity():
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

@syndbb.app.route("/rules-and-terms/")
def rules_and_terms():
    return syndbb.render_template('rules_and_terms.html', title="Rules & Terms of Service", subheading=[""])

@syndbb.app.route("/info/")
def site_info():
    return syndbb.render_template('info.html', title="Information", subheading=[""])

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
            if check_ban_by_id(user.user_id):
                style = "color: #FF0000 !important; text-decoration: line-through !important;"
        else:
            style = "color: #397FEF !important; font-weight bold !important;"
        usercss += "."+user.username+"{"+style+"}\n"
    response = make_response(usercss)
    response.headers['Content-Type'] = 'text/css'
    return response
