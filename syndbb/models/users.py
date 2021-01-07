#
# Copyright (c) 2017 - 2020 Keira T (https://kei.info.gf). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb
from syndbb.models.time import unix_time_current, display_time, cdn_path
from syndbb.models.d2_hash import get_ip_hash
from syndbb.models.version import get_core_config
from anonymizeip import anonymize_ip

### General Functions ###
#Check if a session is valid
def check_session_by_id(sessionid):
    if syndbb.session:
        session_cookie = str(syndbb.session['logged_in'])
        if session_cookie == sessionid:
            session_check = d2_ip.query.filter(d2_ip.sessionid == sessionid).filter_by(iphash=get_ip_hash(syndbb.request.remote_addr)).first()
            if session_check:
                ban_check = check_ban_by_id(session_check.user_id)
                if ban_check:
                    return 0
                else:
                    return session_check.user_id
    syndbb.session.pop('logged_in', None)
    return 0

# anonymize ip address for GDPR compliance
def gdpr_check(addr):
    ip = addr
    syndbb.gdpr = 1
    if syndbb.gdpr:
        ip = anonymize_ip(addr)
    return ip

#Check if user is logged in, has a valid session and then get user info for displaying on the site.
@syndbb.app.context_processor
def inject_user():
    if 'logged_in' in syndbb.session:
        user_session = d2_ip.query.filter_by(sessionid=syndbb.session['logged_in']).filter_by(iphash=get_ip_hash(syndbb.request.remote_addr)).first()
        if user_session:
            user = d2_user.query.filter_by(user_id=user_session.user_id).first()
            if user and user.user_id:
                user.last_activity = unix_time_current()
                syndbb.db.session.commit()

                ip_check = d2_ip.query.filter_by(iphash=get_ip_hash(syndbb.request.remote_addr)).filter_by(user_id=user.user_id).filter_by(sessionid=user_session.sessionid).first()
                if ip_check:
                    ip_check.ip = gdpr_check(syndbb.request.remote_addr)
                    ip_check.iphash = get_ip_hash(syndbb.request.remote_addr)
                    ip_check.useragent = syndbb.request.headers.get('User-Agent')
                    ip_check.time = unix_time_current()
                    ip_check.page = syndbb.request.path
                    syndbb.db.session.commit()

                ban_check = check_ban_by_id(user.user_id)
                if ban_check:
                    return {'user': user, 'user_session': user_session, 'ban_check': ban_check}
                else:
                    return {'user': user, 'user_session': user_session}
            else:
                syndbb.session.pop('logged_in', None)
    user = {'user_id': 0, 'username': "Guest", 'rank': 0}
    user_session = {'sessionid': 0}
    return {'user': user, 'user_session': user_session}


#Get display name
@syndbb.app.template_filter('get_displayed_name_by_username')
@syndbb.cache.memoize(timeout=86400) # get_displayed_name_by_username
def get_displayed_name_by_username(username):
    user = d2_user.query.filter_by(username=username).first()
    if user:
        username = user.display_name if user.display_name else user.username
        return username
    else:
        return "[ERROR]"
syndbb.app.jinja_env.globals.update(get_displayed_name_by_username=get_displayed_name_by_username)

#Get display name
@syndbb.app.template_filter('get_displayed_name_by_id')
@syndbb.cache.memoize(timeout=86400) # get_displayed_name_by_id
def get_displayed_name_by_id(user_id):
    user = d2_user.query.filter_by(user_id=user_id).first()
    if user:
        username = user.display_name if user.display_name else user.username
        return username
    else:
        return "[ERROR]"
syndbb.app.jinja_env.globals.update(get_displayed_name_by_id=get_displayed_name_by_id)

#Get status updates
@syndbb.app.template_filter('get_all_status_updates')
@syndbb.cache.memoize(timeout=86400) # get_all_status_updates
def get_all_status_updates():
    statuses = []
    users = d2_user.query.filter(d2_user.status != "").order_by(d2_user.status_time.desc()).limit(7).all()
    for user in users:
        statuses.append([user.status_time, user.status, user.username, user.user_id, get_displayed_name_by_username(user.username)])
    statuses.sort(reverse=True)
    return statuses
syndbb.app.jinja_env.globals.update(get_all_status_updates=get_all_status_updates)


#Get user flair by ID
@syndbb.app.template_filter('get_flair_by_id')
@syndbb.cache.memoize(timeout=86400) # get_flair_by_id
def get_flair_by_id(user_id):
    flair_list = []
    flairfolder = syndbb.app.static_folder + "/data/flair/"+str(user_id)+"/"

    if not syndbb.os.path.exists(flairfolder):
        syndbb.logger.info("path does not exist, creating")
        syndbb.os.makedirs(flairfolder)
    else:
        syndbb.logger.info(flairfolder + " exists")

    for flair in syndbb.os.listdir(flairfolder):
        filepath = flairfolder + "/" + flair
        if syndbb.os.path.isfile(filepath):
            addtime = int(syndbb.os.stat(filepath).st_mtime)
            if "src" not in flair:
                flair_list.append([flair.split(".")[0], addtime])

    return flair_list
syndbb.app.jinja_env.globals.update(get_flair_by_id=get_flair_by_id)

#Get user avatar by ID
@syndbb.app.template_filter('get_avatar_by_id')
@syndbb.cache.memoize(timeout=86400) # get_avatar_by_id
def get_avatar_by_id(user_id):
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
syndbb.app.jinja_env.globals.update(get_avatar_by_id=get_avatar_by_id)

#Get user avatar source by ID
@syndbb.app.template_filter('get_avatar_source_by_id')
@syndbb.cache.memoize(timeout=86400) # get_avatar_source_by_id
def get_avatar_source_by_id(user_id):
    root_path = syndbb.app.static_folder
    user = d2_user.query.filter_by(user_id=user_id).first()
    if user.user_id:
        avatar_path = '/data/avatars/{}-src.png'.format(user.user_id)
        if syndbb.os.path.isfile(root_path+avatar_path):
            return cdn_path() + avatar_path + "?v=" +  str(user.avatar_date)
        else:
            return "[ERROR]"
    else:
        return "[ERROR]"
syndbb.app.jinja_env.globals.update(get_avatar_source_by_id=get_avatar_source_by_id)

#Get ldap variables for user
@syndbb.app.template_filter('get_ldap_by_username')
@syndbb.cache.memoize(timeout=60) # get_ldap_by_username
def get_ldap_by_username(username):
    ldap_vars = ldap_user.query.filter('cn: ' + username).first()
    if ldap_vars:
        return ldap_vars
    else:
        return False
syndbb.app.jinja_env.globals.update(get_ldap_by_username=get_ldap_by_username)


#Get linked accounts by ID
@syndbb.app.template_filter('get_linked_by_id')
@syndbb.cache.memoize(timeout=86400) # get_linked_by_id
def get_linked_by_id(user_id):
    linked_users = []
    user = d2_user.query.filter_by(user_id=user_id).first()
    if user:
        if user.user_auth and user.user_auth != "":
            linked_users = d2_user.query.filter_by(user_auth=user.user_auth).all()
        else:
            linked_users = d2_user.query.filter_by(user_id=user_id).all()
    return linked_users
syndbb.app.jinja_env.globals.update(get_linked_by_id=get_linked_by_id)

#Get username by ID
@syndbb.app.template_filter('get_username_by_id')
@syndbb.cache.memoize(timeout=60) # get_username_by_id
def get_username_by_id(user_id):
    user = d2_user.query.filter_by(user_id=user_id).first()
    if user and user.user_id:
        return user.username
    else:
        return "Guest"
syndbb.app.jinja_env.globals.update(get_username_by_id=get_username_by_id)


#Get username by ID
@syndbb.app.template_filter('get_user_by_id')
def get_user_by_id(user_id):
    user = d2_user.query.filter_by(user_id=user_id).first()
    if user:
        return user
    else:
        return []
syndbb.app.jinja_env.globals.update(get_user_by_id=get_user_by_id)

#Get rank by ID
@syndbb.app.template_filter('get_rank_by_id')
@syndbb.cache.memoize(timeout=60) # get_rank_by_id
def get_rank_by_id(user_id):
    user = d2_user.query.filter_by(user_id=user_id).first()
    if user and user.user_id:
        return user.rank
    else:
        return 0
syndbb.app.jinja_env.globals.update(get_rank_by_id=get_rank_by_id)

#Get title from ID
@syndbb.app.template_filter('get_title_by_id')
@syndbb.cache.memoize(timeout=60) # get_title_by_id
def get_title_by_id(user_id):
    user = d2_user.query.filter_by(user_id=user_id).first()
    if user:
        if user.rank >= 900:
            return "Special Operations"
        elif user.rank >= 500:
            return "Federation Council"
        elif user.rank >= 100:
            return "Peacekeeper"
        elif user.rank >= 50:
            return get_core_config()['site']['donator_group_name']
        elif user.rank >= 20:
            return "Citizen"
        elif user.rank >= 10:
            return "Citizen"
        else:
            return "Tourist"
    else:
        return "Member"
syndbb.app.jinja_env.globals.update(get_title_by_id=get_title_by_id)


#Get title from ID
@syndbb.app.template_filter('get_title_by_rank')
@syndbb.cache.memoize(timeout=60) # get_title_by_rank
def get_title_by_rank(rank):
    if rank:
        if rank >= 900:
            return "Special Operations"
        elif rank >= 500:
            return "Federation Council"
        elif rank >= 100:
            return "Peacekeeper"
        elif rank >= 50:
            return get_core_config()['site']['donator_group_name']
        elif rank >= 20:
            return "Citizen"
        elif rank >= 10:
            return "Citizen"
        else:
            return "Tourist"
    else:
        return "Member"
syndbb.app.jinja_env.globals.update(get_title_by_rank=get_title_by_rank)

#Get banned state
@syndbb.app.template_filter('check_ban_by_id')
@syndbb.cache.memoize(timeout=60) # check_ban_by_id
def check_ban_by_id(id):
    user = d2_user.query.filter_by(user_id=id).first()
    
    if user and user.rank <= 500:
        bans = d2_bans.query.order_by(d2_bans.time.desc()).all()
        for ban in bans:
            if (int(ban.length) is 0) or (int(ban.expires) >= unix_time_current()):
                if ban.banned_id == user.user_id:
                    ips = d2_ip.query.filter_by(user_id=ban.banned_id).all()
                    for ipad in ips:
                        if gdpr_check(syndbb.request.remote_addr) == ipad.ip:
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
syndbb.app.jinja_env.globals.update(check_ban_by_id=check_ban_by_id)


#User group color from user ID
@syndbb.app.template_filter('get_group_style_by_id')
@syndbb.cache.memoize(timeout=300) # get_group_style_by_id
def get_group_style_by_id(user_id):
    user = d2_user.query.filter_by(user_id=user_id).first()
    if user:
        if check_ban_by_id(user.user_id):
            return "banned"
        if user.rank >= 900:
            return "admin"
        elif user.rank >= 500:
            return "operator"
        elif user.rank >= 100:
            return "halfop"
        elif user.rank >= 50:
            return "spec"
        elif user.rank >= 20:
            return "plus"
        elif user.rank >= 10:
            return "citizen"
        else:
            return "tourist"
    else:
        return "tourist"
syndbb.app.jinja_env.globals.update(get_group_style_by_id=get_group_style_by_id)

#User group color from user username
@syndbb.app.template_filter('get_group_style_by_username')
@syndbb.cache.memoize(timeout=300) # get_group_style_by_username
def get_group_style_by_username(username):
    user = d2_user.query.filter_by(username=username).first()
    if user:
        if check_ban_by_id(user.user_id):
            return "banned"
        if user.rank >= 900:
            return "admin"
        elif user.rank >= 500:
            return "operator"
        elif user.rank >= 100:
            return "halfop"
        elif user.rank >= 50:
            return "spec"
        elif user.rank >= 20:
            return "plus"
        elif user.rank >= 10:
            return "citizen"
        else:
            return "tourist"
    else:
        return "tourist"
syndbb.app.jinja_env.globals.update(get_group_style_by_username=get_group_style_by_username)

#User group color
# @syndbb.app.template_filter('get_group_style')
# @syndbb.cache.memoize(timeout=300) # get_group_style
# def get_group_style(group_name, banned=0):
#     if banned:
#         return "color: #FF0000; text-decoration: line-through;"
#     if group_name == "Administrator":
#         return "color: #DB0003; font-weight: bold;"
#     elif group_name == "Operator":
#         return "color: #AC15F2; font-weight: bold;"
#     elif group_name == "Peacekeeper":
#         return "color: #00BC1F; font-weight: bold;"
#     elif group_name == get_core_config()['site']['donator_group_name']:
#         return "color: #B56236; font-weight: bold;"
#     else:
#         return "color: #397FEF; font-weight bold;"
# syndbb.app.jinja_env.globals.update(get_group_style=get_group_style)

## LDAP Functions ##
if syndbb.core_config['ldap']['enabled'] :
    class ldap_user(syndbb.ldap.Entry):
        base_dn = syndbb.core_config['ldap']['base_dn'] 
        entry_rdn = syndbb.core_config['ldap']['entry_rdn']
        object_classes = syndbb.core_config['ldap']['classes']

        display_name = syndbb.ldap.Attribute(syndbb.core_config['ldap']['attribute_displayname'])
        username = syndbb.ldap.Attribute(syndbb.core_config['ldap']['attribute_cn'])
        surname = syndbb.ldap.Attribute(syndbb.core_config['ldap']['attribute_sn'])
        password = syndbb.ldap.Attribute(syndbb.core_config['ldap']['attribute_password'])

    def __repr__(self):
        return '<User %r>' % self.username
else:
    class ldap_user():
        placeholder = True
    def __repr__(self):
        return False

### MySQL Functions ###
class d2_user(syndbb.db.Model):
    user_id = syndbb.db.Column(syndbb.db.Integer, primary_key=True)
    username = syndbb.db.Column(syndbb.db.String(150), unique=True)
    display_name = syndbb.db.Column(syndbb.db.String(300), unique=True)
    token = syndbb.db.Column(syndbb.db.String, unique=False)
    title = syndbb.db.Column(syndbb.db.String, unique=False)
    bio = syndbb.db.Column(syndbb.db.String, unique=False)
    status = syndbb.db.Column(syndbb.db.String, unique=False)
    status_time = syndbb.db.Column(syndbb.db.Integer, unique=False)
    rank = syndbb.db.Column(syndbb.db.Integer, unique=False)
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
    irc_auth = syndbb.db.Column(syndbb.db.String, unique=False)
    upload_auth = syndbb.db.Column(syndbb.db.String, unique=False)
    user_auth = syndbb.db.Column(syndbb.db.String, unique=False)
    upload_url = syndbb.db.Column(syndbb.db.String, unique=False)
    nsfw_toggle = syndbb.db.Column(syndbb.db.Integer, unique=False)
    full_avatar = syndbb.db.Column(syndbb.db.Integer, unique=False)
    tags = syndbb.db.Column(syndbb.db.String, unique=False)


    def __init__(self, username, display_name, token, title, bio, status, status_time, rank, avatar_date, password, post_count, line_count, word_count, profanity_count, karma_positive, karma_negative, points, join_date, last_login, last_activity, irc_auth, upload_auth, user_auth, upload_url, nsfw_toggle, full_avatar, tags):
        self.username = username
        self.display_name = display_name
        self.token = token
        self.title = title
        self.bio = bio
        self.status = status
        self.status_time = status_time
        self.rank = rank
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
        self.irc_auth = irc_auth
        self.upload_auth = upload_auth
        self.user_auth = user_auth
        self.upload_url = upload_url
        self.nsfw_toggle = nsfw_toggle
        self.full_avatar = full_avatar
        self.tags = tags

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
