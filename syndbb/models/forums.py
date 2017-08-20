#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb
from syndbb.models.get_emote import get_emote
from syndbb.models.users import d2_user, get_group_style_from_id
import syndbb.models.bbcode

### General Functions ###
#Forum list
@syndbb.app.context_processor
def inject_forums():
    forums = d2_forums.query.filter_by(approved='1', owned_by='0').all()
    return {'forums': forums}

#Custom Forum List
@syndbb.app.context_processor
def inject_custom_forums():
    forums = d2_forums.query.filter(d2_forums.owned_by != '0').filter(d2_forums.approved == '1').all()
    return {'custom_forums': forums}

#Forum icons
@syndbb.app.template_filter('get_forum_icon')
def get_forum_icon(short_name):
    forum_icon = '/static/data/logos/{}.png'.format(short_name)
    forum_icon_default = '/static/data/logos/blank.png'
    root_path = syndbb.app.root_path

    if syndbb.os.path.isfile(root_path+forum_icon):
        return forum_icon
    else:
        return forum_icon_default
syndbb.app.jinja_env.globals.update(get_forum_icon=get_forum_icon)

#Reply IDs for a post
@syndbb.app.template_filter('replies_to_post')
def replies_to_post(post_id):
    replies = d2_activity.query.filter_by(replyToPost=post_id).all()

    if replies:
        return replies
    else:
        return False
syndbb.app.jinja_env.globals.update(replies_to_post=replies_to_post)

#Get post rating
@syndbb.app.template_filter('get_post_rating')
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
    postname = syndbb.re.findall('@(\w+)', text, syndbb.re.IGNORECASE)
    for user in postname:
        d2user = d2_user.query.filter_by(username=user).first()
        if d2user:
            user_link = '<a href="/user/'+d2user.username+'" style="'+get_group_style_from_id(d2user.user_id)+'">'+d2user.username+'</a>'
            text = syndbb.re.sub(user, user_link, text)
    # Add in emotes
    for k, v in get_emote():
        text = text.replace(v, '<img src="/static/images/emots/'+k+'" alt="'+k+'" title="'+v+'" class="emoticon" />')
    return text
syndbb.app.jinja_env.globals.update(parse_bbcode=parse_bbcode)

### MySQL Functions ###
class d2_forums(syndbb.db.Model):
    id = syndbb.db.Column(syndbb.db.Integer, primary_key=True)
    name = syndbb.db.Column(syndbb.db.String(50), unique=True)
    short_name = syndbb.db.Column(syndbb.db.String(4), unique=True)
    description = syndbb.db.Column(syndbb.db.String, unique=False)
    nsfw = syndbb.db.Column(syndbb.db.Integer, unique=False)
    owned_by = syndbb.db.Column(syndbb.db.Integer, unique=False)
    approved = syndbb.db.Column(syndbb.db.Integer, unique=False)

    def __init__(self, name, short_name, description, owned_by, nsfw, approved):
        self.name = name
        self.short_name = short_name
        self.description = description
        self.owned_by = owned_by
        self.nsfw = nsfw
        self.approved = approved

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

    def __init__(self, user_id, time, content, replyto, replyToPost, title, category, reply_time, reply_count, rating):
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
