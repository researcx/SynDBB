#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb
from geolite2 import geolite2
from syndbb.models.time import unix_time_current, display_time

### General Functions ###
#Check if a session is valid
def checkSession(sessionid):
    if syndbb.session:
        sessioncookie = str(syndbb.session['logged_in'])
        if sessioncookie == sessionid:
            sessioncheck = d2_session.query.filter(d2_session.sessionid == sessionid).first()
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
        user_session = d2_session.query.filter_by(sessionid=syndbb.session['logged_in']).first()
        if user_session:
            user = d2_user.query.filter_by(user_id=user_session.user_id).first()
            if user and user.user_id:
                user.last_activity = unix_time_current()
                syndbb.db.session.commit()


                my_ip = syndbb.request.remote_addr
                ipcheck = d2_ip.query.filter_by(ip=my_ip).filter_by(user_id=user.user_id).filter_by(login=1).first()
                if ipcheck:
                    ipcheck.time = unix_time_current()
                    syndbb.db.session.commit()
                else:
                    new_ip = d2_ip(my_ip, user.user_id, unix_time_current(), 1)
                    syndbb.db.session.add(new_ip)
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

#Get user avatar by ID
@syndbb.app.template_filter('get_avatar')
def get_avatar(user_id):
    default_avatar = '/static/images/default_avatar.png'
    root_path = syndbb.app.root_path
    user = d2_user.query.filter_by(user_id=user_id).first()
    if user.user_id:
        avatar_path = '/static/data/avatars/{}.png'.format(user.user_id)
        if syndbb.os.path.isfile(root_path+avatar_path):
            return avatar_path + "?v=" +  str(user.avatar_date)
        else:
            return default_avatar
    else:
        return default_avatar
syndbb.app.jinja_env.globals.update(get_avatar=get_avatar)

#Get username by ID
@syndbb.app.template_filter('get_name')
def get_name(user_id):
    user = d2_user.query.filter_by(user_id=user_id).first()
    if user.user_id:
        return user.username
    else:
        return "Guest"
syndbb.app.jinja_env.globals.update(get_name=get_name)

#Get title from ID
@syndbb.app.template_filter('get_user_title')
def get_user_title(title):
    if title:
        return title
    else:
        return "Member"
syndbb.app.jinja_env.globals.update(get_user_title=get_user_title)

#Get title from ID
@syndbb.app.template_filter('country_from_ip')
def country_from_ip(ip):
    if ip:
        reader = geolite2.reader()
        geo_data = reader.get(ip)
        geolite2.close()
        if geo_data and 'country' in geo_data and 'iso_code' in geo_data['country']:
            country_iso_code = geo_data['country']['iso_code']
            return country_iso_code
    return "N/A"
syndbb.app.jinja_env.globals.update(country_from_ip=country_from_ip)

#Get title from ID
@syndbb.app.template_filter('is_banned')
def is_banned(id):
    user = d2_user.query.filter_by(user_id=id).first()
    if user and user.rank >= 500:
        return 0
    else:
        ban = d2_bans.query.filter_by(banned_id=id).order_by(d2_bans.time.desc()).first()
        if ban:
            if ban.length is not 0:
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
def get_group_style_from_id(user_id):
    user = d2_user.query.filter_by(user_id=user_id).first()
    if user:
        if is_banned(user.user_id):
            return "color: #FF0000; text-decoration: line-through;"
        if user.rank >= 900:
            return "color: #DB0003; font-weight: bold;"
        elif user.rank >= 500:
            return "color: #AC15F2; font-weight: bold;"
        elif user.rank >= 100:
            return "color: #00BC1F; font-weight: bold;"
        elif user.rank >= 50:
            return "color: #B56236; font-weight: bold;"
        else:
            return "color: #397FEF; font-weight bold;"
    else:
        return "color: #397FEF; font-weight bold;"
syndbb.app.jinja_env.globals.update(get_group_style_from_id=get_group_style_from_id)

#User group color
@syndbb.app.template_filter('get_group_style')
def get_group_style(group_name, banned=0):
    if banned:
        return "color: #FF0000; text-decoration: line-through;"
    if group_name == "Administrator":
        return "color: #DB0003; font-weight: bold;"
    elif group_name == "Operator":
        return "color: #AC15F2; font-weight: bold;"
    elif group_name == "Half-Operator":
        return "color: #00BC1F; font-weight: bold;"
    elif group_name == "Gold Member":
        return "color: #B56236; font-weight: bold;"
    else:
        return "color: #397FEF; font-weight bold;"
syndbb.app.jinja_env.globals.update(get_group_style=get_group_style)

### MySQL Functions ###
class d2_session(syndbb.db.Model):
    id = syndbb.db.Column(syndbb.db.Integer, primary_key=True)
    user_id = syndbb.db.Column(syndbb.db.Integer, unique=False)
    sessionid = syndbb.db.Column(syndbb.db.String, unique=False)
    time = syndbb.db.Column(syndbb.db.Integer, unique=False)

    def __init__(self, user_id, sessionid, time):
        self.user_id = user_id
        self.sessionid = sessionid
        self.time = time

    def __repr__(self):
        return '<Session %r>' % self.sessionid


class d2_user(syndbb.db.Model):
    user_id = syndbb.db.Column(syndbb.db.Integer, primary_key=True)
    username = syndbb.db.Column(syndbb.db.String(150), unique=True)
    email = syndbb.db.Column(syndbb.db.String, unique=False)
    title = syndbb.db.Column(syndbb.db.String, unique=False)
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


    def __init__(self, username, email, title, rank, gender, location, occupation, bio, site, avatar_date, password, post_count, line_count, word_count, profanity_count, karma_positive, karma_negative, points, join_date, last_login, last_activity, ircauth, uploadauth, upload_url):
        self.username = username
        self.email = email
        self.title = title
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

def __init__(self, banned_id, reason, length, time, expires, post, banner):
    self.banned_id = banned_id
    self.reason = reason
    self.length = length
    self.time = time
    self.expires = expires
    self.post = post
    self.banner = banner

def __repr__(self):
    return '<Banned %r>' % self.banned_id


class d2_ip(syndbb.db.Model):
    id = syndbb.db.Column(syndbb.db.Integer, primary_key=True)
    ip = syndbb.db.Column(syndbb.db.String, unique=False)
    user_id = syndbb.db.Column(syndbb.db.Integer, unique=False)
    time = syndbb.db.Column(syndbb.db.Integer, unique=False)
    login = syndbb.db.Column(syndbb.db.Integer, unique=False)

    def __init__(self, ip, user_id, time, login):
        self.ip = ip
        self.user_id = user_id
        self.time = time
        self.login = login

    def __repr__(self):
        return '<IP %r>' % self.user_id
