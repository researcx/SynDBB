#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb, json, requests, urllib.parse
from operator import itemgetter
from syndbb.models.get_emote import get_emote
from syndbb.models.users import d2_user, get_group_style_from_id
from syndbb.models.time import cdn_path
import syndbb.models.bbcode

### General Functions ###
#Forum list
@syndbb.app.context_processor
@syndbb.cache.memoize(timeout=60)
def inject_forums():
    forums = d2_forums.query.filter_by(approved='1', owned_by='0').all()
    return {'forums': forums}

#Custom Forum List
@syndbb.app.context_processor
@syndbb.cache.memoize(timeout=60)
def inject_custom_forums():
    forums = d2_forums.query.filter(d2_forums.owned_by != '0').filter(d2_forums.approved == '1').all()
    return {'custom_forums': forums}

#Get post icons
@syndbb.cache.memoize(timeout=60)
def get_post_icons():
    iconfolder = syndbb.app.static_folder + "/images/posticons/"
    picon_list = []
    for picon in syndbb.os.listdir(iconfolder):
        filepath = iconfolder + "/" + picon
        if syndbb.os.path.isfile(filepath):
            addtime = int(syndbb.os.stat(filepath).st_mtime)
            code = syndbb.os.path.splitext(picon)[0]
            picon_list.append([picon, code])
    picon_list.sort(reverse=False)
    return picon_list
syndbb.app.jinja_env.globals.update(get_post_icons=get_post_icons)

# #Forum icons
# @syndbb.app.template_filter('get_forum_logo')
# @syndbb.cache.memoize(timeout=60)
# def get_forum_logo(short_name):
#     forum_icon = '/images/logos/{}.png'.format(short_name)
#     forum_icon_default = '/images/logos/blank.png'
#     root_path = syndbb.app.static_folder
#
#     if syndbb.os.path.isfile(root_path+forum_icon):
#         return cdn_path() + forum_icon
#     else:
#         return cdn_path() + forum_icon_default
# syndbb.app.jinja_env.globals.update(get_forum_logo=get_forum_logo)
#
# #Forum icons 2
# @syndbb.app.template_filter('get_forum_icon')
# @syndbb.cache.memoize(timeout=60)
# def get_forum_icon(short_name):
#     forum_icon = '/images/forumicons/{}.png'.format(short_name)
#     forum_icon_default = '/images/forumicons/blank.png'
#     root_path = syndbb.app.static_folder
#
#     if syndbb.os.path.isfile(root_path+forum_icon):
#         return cdn_path() + forum_icon
#     else:
#         return cdn_path() + forum_icon_default
# syndbb.app.jinja_env.globals.update(get_forum_icon=get_forum_icon)

#Reply IDs for a post
@syndbb.app.template_filter('replies_to_post')
@syndbb.cache.memoize(timeout=30)
def replies_to_post(post_id):
    replies = d2_activity.query.filter_by(replyToPost=post_id).all()
    if replies:
        return replies
    else:
        return False
syndbb.app.jinja_env.globals.update(replies_to_post=replies_to_post)

#Get post rating
@syndbb.app.template_filter('get_post_rating')
@syndbb.cache.memoize(timeout=30)
def get_post_rating(post_id):
    ratings = d2_post_ratings.query.filter_by(post_id=post_id).all()

    final_count = 0
    for rating in ratings:
        final_count = final_count + rating.type
    return final_count
syndbb.app.jinja_env.globals.update(get_post_rating=get_post_rating)

#Parse forum BBCode
@syndbb.app.template_filter('parse_bbcode')
def parse_bbcode(text):
    # Do the bbcode parsing
    text = syndbb.models.bbcode.parser.format(text)
    # Get @usernames and turn them into links
    postname = syndbb.re.findall('(@\w+)', text, syndbb.re.IGNORECASE)
    for user in postname:
        highlighted_user = user[1:]
        d2user = d2_user.query.filter_by(username=highlighted_user).first()
        if d2user:
            user_link = '<a href="/user/'+d2user.username+'" class="username '+get_group_style_from_id(d2user.user_id)+' link-postname profile-inline">'+d2user.username+'</a>'
            text = syndbb.re.sub(user, user_link, text)
    # Add in emotes
    for k, v in get_emote():
        text = text.replace(v, '<img src="'+cdn_path()+'/images/emots/'+k+'" alt="'+k+'" title="'+v+'" class="emoticon" />')
    return text
syndbb.app.jinja_env.globals.update(parse_bbcode=parse_bbcode)

#Get channel info
@syndbb.app.template_filter('get_channel_list')
#@syndbb.cache.memoize(timeout=360)
def get_channel_list():
    channels = []
    chlist = ""
    forum_list = d2_forums.query.filter_by(owned_by=0).all()
    for forum in forum_list:
        threadcount = 0
        messagecount = 0
        forum_icon = '/images/forumicons/{}.png'.format(forum.short_name)
        forum_icon_default = '/images/forumicons/blank.png'
        root_path = syndbb.app.static_folder
        if syndbb.os.path.isfile(root_path+forum_icon):
            forum_icon = cdn_path() + forum_icon
        else:
            forum_icon = cdn_path() + forum_icon_default
        threadcount = d2_activity.query.filter(d2_activity.category == forum.id).count()
        threadlist = d2_activity.query.filter(d2_activity.category == forum.id).all()
        
        for thread in threadlist:
            messagecount += d2_activity.query.filter(d2_activity.replyto == thread.id).count()
            
        messagecount = threadcount + messagecount
            
        channels.append({"id": forum.id, "name": forum.name, "description": forum.description, "alias": forum.short_name, "anon": forum.anon, "auth": forum.auth, "owned_by": forum.owned_by, "nsfw": forum.nsfw, "alias": forum.short_name, "icon": forum_icon, "messages": messagecount})
    channels.sort(key=itemgetter('id'))

    for forum in channels:
        modes = ""
        
        if forum['auth'] == 1:
            modes += '<i title="Authorization required." class="fa fa-lock" aria-hidden="true"></i> '
        if forum['anon'] == 1:
            modes += ' <i title="Anonymous posting allowed." class="fa fa-eye-slash" aria-hidden="true"></i> '
        if forum['nsfw'] == 1:
            modes += '<i title="Not safe for work. [18+]" class="fa fa-ban" aria-hidden="true"></i>'
        
        chlist += '''<tr>
            <td class="home-forum home-forum-icon"><a href="/''' + str(forum['alias']) + '''"><img src="'''+ str(forum['icon']) + '''" alt=""/></a></td>
            <td class="home-forum"><a href="/''' + str(forum['alias']) + '''"><b>''' + str(forum['name']) + '''</b></a>
            <br/><span class="small">''' + str(forum['description']) + '''</span>
            </td>
            <td class="home-forum home-forum-modes" style="padding-right: 9px !important;">
                <span style="float: right;">
                   <span class="text-muted">''' + modes + '''</span>
                </span>
            </td>
            
            <td class="home-forum home-forum-threads" title="Messages">
                <span style="float: right;">
                   ''' + str(forum['messages']) + '''
                </span>
            </td>

            <td class="home-forum small home-forum-options" style="padding-right: 9px !important;">
                <a href="/''' + str(forum['alias']) + '''/grid" title="Grid/Catalog View">
                    <i class="silk-icon icon_application_view_tile" aria-hidden="true"></i>
                </a>
                <a href="/''' + str(forum['alias']) + '''/new_thread" title="Create A New Thread">
                    <i class="silk-icon icon_add" aria-hidden="true"></i>
                </a>
            </td>
          </tr>'''
    return chlist
syndbb.app.jinja_env.globals.update(get_channel_list=get_channel_list)

### MySQL Functions ###
class d2_forums(syndbb.db.Model):
    id = syndbb.db.Column(syndbb.db.Integer, primary_key=True)
    name = syndbb.db.Column(syndbb.db.String(50), unique=True)
    short_name = syndbb.db.Column(syndbb.db.String(4), unique=True)
    description = syndbb.db.Column(syndbb.db.String, unique=False)
    nsfw = syndbb.db.Column(syndbb.db.Integer, unique=False)
    owned_by = syndbb.db.Column(syndbb.db.Integer, unique=False)
    approved = syndbb.db.Column(syndbb.db.Integer, unique=False)
    auth = syndbb.db.Column(syndbb.db.Integer, unique=False)
    anon = syndbb.db.Column(syndbb.db.Integer, unique=False)

    def __init__(self, name, short_name, description, owned_by, nsfw, approved, auth, anon):
        self.name = name
        self.short_name = short_name
        self.description = description
        self.owned_by = owned_by
        self.nsfw = nsfw
        self.approved = approved
        self.auth = auth
        self.anon = anon

    def __repr__(self):
        return '<Forum %r>' % self.name

class d2_activity(syndbb.db.Model):
    id = syndbb.db.Column(syndbb.db.Integer, primary_key=True)
    user_id = syndbb.db.Column(syndbb.db.Integer, syndbb.db.ForeignKey('d2_user.user_id'))
    user = syndbb.db.relationship('d2_user', backref=syndbb.db.backref('d2_activity', lazy='dynamic'))
    time = syndbb.db.Column(syndbb.db.Integer, unique=False)
    content = syndbb.db.Column(syndbb.db.String, unique=False)
    replyto = syndbb.db.Column(syndbb.db.Integer, unique=False)
    replyToPost = syndbb.db.Column(syndbb.db.Integer, unique=False)
    title = syndbb.db.Column(syndbb.db.String, unique=False)
    category = syndbb.db.Column(syndbb.db.Integer, unique=False)
    reply_time = syndbb.db.Column(syndbb.db.Integer, unique=False)
    reply_count = syndbb.db.Column(syndbb.db.Integer, unique=False)
    rating = syndbb.db.Column(syndbb.db.Integer, unique=False)
    post_icon = syndbb.db.Column(syndbb.db.Integer, unique=False)
    anonymous = syndbb.db.Column(syndbb.db.Integer, unique=False)

    def __init__(self, user_id, time, content, replyto, replyToPost, title, category, reply_time, reply_count, rating, post_icon, anonymous):
        self.user_id = user_id
        self.time = time
        self.content = content
        self.replyto = replyto
        self.replyToPost = replyToPost
        self.title = title
        self.category = category
        self.reply_time = reply_time
        self.reply_count = reply_count
        self.rating = rating
        self.post_icon = post_icon
        self.anonymous = anonymous

    def __repr__(self):
        return '<Post %r>' % self.id

class d2_post_ratings(syndbb.db.Model):
    id = syndbb.db.Column(syndbb.db.Integer, primary_key=True)
    post_id = syndbb.db.Column(syndbb.db.String(50), unique=False)
    user_id = syndbb.db.Column(syndbb.db.String(4), unique=False)
    type = syndbb.db.Column(syndbb.db.String, unique=False)

    def __init__(self, post_id, user_id, type):
        self.post_id = post_id
        self.user_id = user_id
        self.type = type

    def __repr__(self):
        return '<Rating %r>' % self.type
