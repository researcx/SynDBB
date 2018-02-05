#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb
from syndbb.models.time import unix_time_current, display_time, cdn_path

### General Functions ###
#Check if a session is valid
def checkSession(sessionid):
    if syndbb.session:
        sessioncookie = str(syndbb.session['logged_in'])
        if sessioncookie == sessionid:
            sessioncheck = d2_ip.query.filter(d2_ip.sessionid == sessionid).filter_by(ip=syndbb.request.remote_addr).first()
            if sessioncheck:
                bancheck = is_banned(sessioncheck.user_id)
                if bancheck:
                    return 0
                else:
                    return sessioncheck.user_id
    syndbb.session.pop('logged_in', None)
    return 0


#Check if user is logged in, has a valid session and then get user info for displaying on the site.
@syndbb.app.context_processor
def inject_user():
    if 'logged_in' in syndbb.session:
        user_session = d2_ip.query.filter_by(sessionid=syndbb.session['logged_in']).filter_by(ip=syndbb.request.remote_addr).first()
        if user_session:
            user = d2_user.query.filter_by(user_id=user_session.user_id).first()
            if user and user.user_id:
                user.last_activity = unix_time_current()
                syndbb.db.session.commit()

                my_ip = syndbb.request.remote_addr
                ipcheck = d2_ip.query.filter_by(ip=my_ip).filter_by(user_id=user.user_id).filter_by(sessionid=user_session.sessionid).first()
                if ipcheck:
                    ipcheck.time = unix_time_current()
                    ipcheck.page = syndbb.request.path
                    syndbb.db.session.commit()

                bancheck = is_banned(user.user_id)
                if bancheck:
                    return {'user': user, 'user_session': user_session, 'bancheck': bancheck}
                else:
                    return {'user': user, 'user_session': user_session}
            else:
                syndbb.session.pop('logged_in', None)
    user = {'user_id': 0, 'username': "Guest", 'rank': 0}
    user_session = {'sessionid': 0}
    return {'user': user, 'user_session': user_session}

#Get status updates
@syndbb.app.template_filter('get_all_status_updates')
@syndbb.cache.memoize(timeout=60)
def get_all_status_updates():
    statuses = []
    users = d2_user.query.filter(d2_user.status != "").order_by(d2_user.status_time.desc()).limit(7).all()
    for user in users:
        statuses.append([user.status_time, user.status, user.username, user.user_id])
    statuses.sort(reverse=True)
    return statuses

syndbb.app.jinja_env.globals.update(get_all_status_updates=get_all_status_updates)

#Get user avatar by ID
@syndbb.app.template_filter('get_avatar')
def get_avatar(user_id):
    default_avatar = '/images/default_avatar.png'
    root_path = syndbb.app.static_folder
    user = d2_user.query.filter_by(user_id=user_id).first()
    if user.user_id:
        avatar_path = '/data/avatars/{}.png'.format(user.user_id)
        if syndbb.os.path.isfile(root_path+avatar_path):
            return cdn_path() + avatar_path + "?v=" +  str(user.avatar_date)
        else:
            return cdn_path() + default_avatar
    else:
        return default_avatar
syndbb.app.jinja_env.globals.update(get_avatar=get_avatar)

#Get user avatar source by ID
@syndbb.app.template_filter('get_avatar_source')
def get_avatar_source(user_id):
    root_path = syndbb.app.static_folder
    user = d2_user.query.filter_by(user_id=user_id).first()
    if user.user_id:
        avatar_path = '/data/avatars/{}-src.png'.format(user.user_id)
        if syndbb.os.path.isfile(root_path+avatar_path):
            return cdn_path() + avatar_path + "?v=" +  str(user.avatar_date)
        else:
            return ""
    else:
        return ""
syndbb.app.jinja_env.globals.update(get_avatar_source=get_avatar_source)

#Get username by ID
@syndbb.app.template_filter('get_name')
@syndbb.cache.memoize(timeout=180)
def get_name(user_id):
    user = d2_user.query.filter_by(user_id=user_id).first()
    if user and user.user_id:
        return user.username
    else:
        return "Guest"
syndbb.app.jinja_env.globals.update(get_name=get_name)

#Get title from ID
@syndbb.app.template_filter('get_user_title')
@syndbb.cache.memoize(timeout=180)
def get_user_title(user_id):
    user = d2_user.query.filter_by(user_id=user_id).first()
    if user:
        if user.rank >= 900:
            return "Administrator"
        elif user.rank >= 500:
            return "Operator"
        elif user.rank >= 100:
            return "Half-Operator"
        elif user.rank >= 50:
            return "Gold Member"
        else:
            return "Member"
    else:
        return "Member"
syndbb.app.jinja_env.globals.update(get_user_title=get_user_title)

#Get banned state
@syndbb.app.template_filter('is_banned')
def is_banned(id):
    user = d2_user.query.filter_by(user_id=id).first()
    
    if user and user.rank <= 500:
        bans = d2_bans.query.order_by(d2_bans.time.desc()).all()
        for ban in bans:
            if (int(ban.length) is 0) or (int(ban.expires) >= unix_time_current()):
                if ban.banned_id == user.user_id:
                    ips = d2_ip.query.filter_by(user_id=ban.banned_id).all()
                    for ipad in ips:
                        if syndbb.request.remote_addr == ipad.ip:
                            return {'ban': ban, 'banduration': "NEVER"}
                        
    if user and user.rank >= 500:
        return 0
    else:
        ban = d2_bans.query.filter_by(banned_id=id).order_by(d2_bans.time.desc()).first()
        if ban:
            if int(ban.length) is not 0:
                if int(ban.expires) <= unix_time_current():
                    return 0
                else:
                    return {'ban': ban, 'banduration': display_time(ban.length)}
            else:
                return {'ban': ban, 'banduration': "NEVER"}
        else:
            return 0
syndbb.app.jinja_env.globals.update(is_banned=is_banned)


#User group color from user ID
@syndbb.app.template_filter('get_group_style_from_id')
@syndbb.cache.memoize(timeout=180)
def get_group_style_from_id(user_id):
    user = d2_user.query.filter_by(user_id=user_id).first()
    if user:
        if is_banned(user.user_id):
            return "banned"
        if user.rank >= 900:
            return "admin"
        elif user.rank >= 500:
            return "operator"
        elif user.rank >= 100:
            return "halfop"
        elif user.rank >= 50:
            return "goldmember"
        else:
            return "member"
    else:
        return "member"
syndbb.app.jinja_env.globals.update(get_group_style_from_id=get_group_style_from_id)

#User group color
# @syndbb.app.template_filter('get_group_style')
# @syndbb.cache.memoize(timeout=180)
# def get_group_style(group_name, banned=0):
#     if banned:
#         return "color: #FF0000; text-decoration: line-through;"
#     if group_name == "Administrator":
#         return "color: #DB0003; font-weight: bold;"
#     elif group_name == "Operator":
#         return "color: #AC15F2; font-weight: bold;"
#     elif group_name == "Half-Operator":
#         return "color: #00BC1F; font-weight: bold;"
#     elif group_name == "Gold Member":
#         return "color: #B56236; font-weight: bold;"
#     else:
#         return "color: #397FEF; font-weight bold;"
# syndbb.app.jinja_env.globals.update(get_group_style=get_group_style)

### MySQL Functions ###
class d2_user(syndbb.db.Model):
    user_id = syndbb.db.Column(syndbb.db.Integer, primary_key=True)
    username = syndbb.db.Column(syndbb.db.String(150), unique=True)
    token = syndbb.db.Column(syndbb.db.String, unique=False)
    title = syndbb.db.Column(syndbb.db.String, unique=False)
    status = syndbb.db.Column(syndbb.db.String, unique=False)
    status_time = syndbb.db.Column(syndbb.db.Integer, unique=False)
    rank = syndbb.db.Column(syndbb.db.Integer, unique=False)
    gender = syndbb.db.Column(syndbb.db.String, unique=False)
    location = syndbb.db.Column(syndbb.db.String, unique=False)
    occupation = syndbb.db.Column(syndbb.db.String, unique=False)
    bio = syndbb.db.Column(syndbb.db.String, unique=False)
    site = syndbb.db.Column(syndbb.db.String, unique=False)
    avatar_date = syndbb.db.Column(syndbb.db.Integer, unique=False)
    password = syndbb.db.Column(syndbb.db.String, unique=False)
    post_count = syndbb.db.Column(syndbb.db.Integer, unique=False)
    line_count = syndbb.db.Column(syndbb.db.Integer, unique=False)
    word_count = syndbb.db.Column(syndbb.db.Integer, unique=False)
    profanity_count = syndbb.db.Column(syndbb.db.Integer, unique=False)
    karma_positive = syndbb.db.Column(syndbb.db.Integer, unique=False)
    karma_negative = syndbb.db.Column(syndbb.db.Integer, unique=False)
    points = syndbb.db.Column(syndbb.db.Integer, unique=False)
    join_date = syndbb.db.Column(syndbb.db.Integer, unique=False)
    last_login = syndbb.db.Column(syndbb.db.Integer, unique=False)
    last_activity = syndbb.db.Column(syndbb.db.Integer, unique=False)
    ircauth = syndbb.db.Column(syndbb.db.String, unique=False)
    uploadauth = syndbb.db.Column(syndbb.db.String, unique=False)
    upload_url = syndbb.db.Column(syndbb.db.String, unique=False)


    def __init__(self, username, token, title, status, status_time, rank, gender, location, occupation, bio, site, avatar_date, password, post_count, line_count, word_count, profanity_count, karma_positive, karma_negative, points, join_date, last_login, last_activity, ircauth, uploadauth, upload_url):
        self.username = username
        self.token = token
        self.title = title
        self.status = status
        self.status_time = status_time
        self.rank = rank
        self.gender = gender
        self.location = location
        self.occupation = occupation
        self.bio = bio
        self.site = site
        self.avatar_date = avatar_date
        self.password = password
        self.post_count = post_count
        self.line_count = line_count
        self.word_count = word_count
        self.profanity_count = profanity_count
        self.karma_positive = karma_positive
        self.karma_negative = karma_negative
        self.points = points
        self.join_date = join_date
        self.last_login = last_login
        self.last_activity = last_activity
        self.ircauth = ircauth
        self.uploadauth = uploadauth
        self.upload_url = upload_url

    def __repr__(self):
        return '<User %r>' % self.username


class d2_bans(syndbb.db.Model):
    id = syndbb.db.Column(syndbb.db.Integer, primary_key=True)
    banned_id = syndbb.db.Column(syndbb.db.Integer, unique=False)
    reason = syndbb.db.Column(syndbb.db.String, unique=False)
    length = syndbb.db.Column(syndbb.db.Integer, unique=False)
    time = syndbb.db.Column(syndbb.db.Integer, unique=False)
    expires = syndbb.db.Column(syndbb.db.Integer, unique=False)
    post = syndbb.db.Column(syndbb.db.Integer, unique=False)
    banner = syndbb.db.Column(syndbb.db.Integer, unique=False)
    display = syndbb.db.Column(syndbb.db.Integer, unique=False)

def __init__(self, banned_id, reason, length, time, expires, post, banner, display):
    self.banned_id = banned_id
    self.reason = reason
    self.length = length
    self.time = time
    self.expires = expires
    self.post = post
    self.banner = banner
    self.display = display

def __repr__(self):
    return '<Banned %r>' % self.banned_id


class d2_ip(syndbb.db.Model):
    id = syndbb.db.Column(syndbb.db.Integer, primary_key=True)
    ip = syndbb.db.Column(syndbb.db.String, unique=False)
    useragent = syndbb.db.Column(syndbb.db.String, unique=False)
    user_id = syndbb.db.Column(syndbb.db.Integer, unique=False)
    time = syndbb.db.Column(syndbb.db.Integer, unique=False)
    login = syndbb.db.Column(syndbb.db.Integer, unique=False)
    page = syndbb.db.Column(syndbb.db.String, unique=False)
    sessionid = syndbb.db.Column(syndbb.db.String, unique=False)
    iphash = syndbb.db.Column(syndbb.db.String, unique=False)

    def __init__(self, ip, useragent, user_id, time, login, page, sessionid, iphash):
        self.ip = ip
        self.useragent = useragent
        self.user_id = user_id
        self.time = time
        self.login = login
        self.page = page
        self.sessionid = sessionid
        self.iphash = iphash

    def __repr__(self):
        return '<IP %r>' % self.user_id
