#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb
from syndbb.models.users import d2_user, d2_bans, is_banned, get_group_style_from_id
from syndbb.models.forums import d2_forums, d2_activity, get_forum_icon
from syndbb.models.time import display_time, recent_date, human_date

#Functions
def unique_items(L):
    found = set()
    for item in L:
        if item[3] not in found:
            yield item
            found.add(item[3])

@syndbb.app.template_filter('get_recent_posts')
@syndbb.cache.memoize(timeout=60)
def get_recent_posts(limit=10):
    activity = []
    activity_sorted = []
    activity_item = ""
    count = 0

    posts = d2_activity.query.filter(d2_activity.replyto != 0).order_by(d2_activity.time.desc()).limit(limit).all()
    threads = d2_activity.query.filter(d2_activity.category != 0).order_by(d2_activity.reply_time.desc()).limit(limit).all()

    for post in posts:
        activity.append([post.time, "post", post.id, post.replyto])

    for thread in threads:
        activity.append([thread.time, "thread", thread.id, thread.id])

    activity.sort(reverse=True)
    activity = unique_items(activity)

    for item in activity:
        if count < limit:
            if item[1] == "post":
                post = d2_activity.query.filter(d2_activity.id == item[2]).first()
                thread = d2_activity.query.filter(d2_activity.id == post.replyto).first()
                creator = d2_user.query.filter_by(user_id=thread.user_id).first()
                poster = d2_user.query.filter_by(user_id=post.user_id).first()
                forum = d2_forums.query.filter(d2_forums.id == thread.category).first()

                if post and thread and poster and forum:
                    activity_item += '''<tr>
                                            <td class="home-forum home-forum-icon"><a href="/'''+str(forum.short_name)+'''/'''+str(thread.id)+'''#'''+str(post.id)+'''"><img src="/static/images/posticons/icon'''+str(thread.post_icon)+'''.gif" alt=""/></a></td>
                                            <td class="home-forum">
                                            <span class="small" style="float:right; text-align: right;">
                                                <span class="timedisplay">'''+recent_date(post.time)+'''</span><br/>
                                                by <a href="/user/'''+poster.username+'''" class="profile-inline">'''+poster.username+'''</a> <a href="/'''+str(forum.short_name)+'''/'''+str(thread.id)+'''#'''+str(post.id)+'''"><img src="/static/images/thread_new.png" style="margin-top: -2px;"/></a>
                                            </span>
                                            <a href="/'''+str(forum.short_name)+'''/'''+str(thread.id)+'''#'''+str(post.id)+'''"><b>'''+thread.title+'''</b></a>
                                            <span class="small"><br/>
                                            <a href="/user/'''+creator.username+'''" class="profile-inline">'''+creator.username+'''</a>, <span class="timedisplay">'''+recent_date(thread.time)+'''</span>, <a href="/'''+str(forum.short_name)+'''">'''+forum.name+'''</a>
                                            </span>

                                            </td>
                                        </tr>'''

            if item[1] == "thread":
                thread = d2_activity.query.filter(d2_activity.id == item[2]).first()
                poster = d2_user.query.filter_by(user_id=thread.user_id).first()
                forum = d2_forums.query.filter(d2_forums.id == thread.category).first()

                if thread and poster and forum:
                    activity_item += '''<tr>
                                            <td class="home-forum home-forum-icon"><a href="/'''+str(forum.short_name)+'''/'''+str(thread.id)+'''"><img src="/static/images/posticons/icon'''+str(thread.post_icon)+'''.gif" alt=""/></a></td>
                                            <td class="home-forum">
                                            <span class="small" style="float:right; text-align: right;">
                                                <span class="timedisplay">'''+recent_date(thread.reply_time)+'''</span><br/>
                                                by <a href="/user/'''+poster.username+'''" class="profile-inline">'''+poster.username+'''</a> <a href="/'''+str(forum.short_name)+'''/'''+str(thread.id)+'''"><img src="/static/images/thread_new.png" style="margin-top: -2px;"/></a>
                                            </span>
                                            <a href="/'''+str(forum.short_name)+'''/'''+str(thread.id)+'''"><b>'''+thread.title+'''</b></a>
                                            <span class="small"><br/>
                                            <a href="/user/'''+poster.username+'''" class="profile-inline">'''+poster.username+'''</a>, <span class="timedisplay">'''+recent_date(thread.time)+'''</span>, <a href="/'''+str(forum.short_name)+'''">'''+forum.name+'''</a>
                                            </span></td>
                                        </tr>'''
            count += 1

    return activity_item
syndbb.app.jinja_env.globals.update(get_recent_posts=get_recent_posts)

@syndbb.app.template_filter('get_activity')
@syndbb.cache.memoize(timeout=60)
def get_activity(limit=10):
    activity = []
    activity_item = ""
    count = 0

    posts = d2_activity.query.filter(d2_activity.replyto != 0).order_by(d2_activity.time.desc()).limit(limit).all()
    threads = d2_activity.query.filter(d2_activity.category != 0).order_by(d2_activity.reply_time.desc()).limit(limit).all()

    for post in posts:
        activity.append([post.time, "post", post.id])

    for thread in threads:
        activity.append([thread.time, "thread", thread.id])

    activity.sort(reverse=True)

    for item in activity:
        if count < limit:
            if item[1] == "post":
                post = d2_activity.query.filter(d2_activity.id == item[2]).first()
                thread = d2_activity.query.filter(d2_activity.id == post.replyto).first()
                poster = d2_user.query.filter_by(user_id=post.user_id).first()
                forum = d2_forums.query.filter(d2_forums.id == thread.category).first()

                if post and thread and poster and forum:
                    activity_item += '''<tr>
                                            <td class="event-icon"><i class="silk-icon icon_comment_add" aria-hidden="true"></i></td>
                                            <td><a href="/user/'''+poster.username+'''" class="profile-inline">'''+poster.username+'''</a> replied to "<a href="/'''+str(forum.short_name)+'''/'''+str(thread.id)+'''#'''+str(post.id)+'''">'''+thread.title+'''</a>" in <a href="/'''+str(forum.short_name)+'''">'''+forum.name+'''</a></td>
                                        </tr>'''

            if item[1] == "thread":
                thread = d2_activity.query.filter(d2_activity.id == item[2]).first()
                poster = d2_user.query.filter_by(user_id=thread.user_id).first()
                forum = d2_forums.query.filter(d2_forums.id == thread.category).first()

                if thread and poster and forum:
                    activity_item += '''<tr>
                                            <td class="event-icon"><i class="silk-icon icon_application_view_list" aria-hidden="true"></i></td>
                                            <td><a href="/user/'''+poster.username+'''"  class="profile-inline">'''+poster.username+'''</a> created "<a href="/'''+str(forum.short_name)+'''/'''+str(thread.id)+'''">'''+thread.title+'''</a>" in <a href="/'''+str(forum.short_name)+'''">'''+forum.name+'''</a></td>
                                        </tr>'''
            count += 1

    return activity_item
syndbb.app.jinja_env.globals.update(get_activity=get_activity)

@syndbb.app.context_processor
@syndbb.cache.memoize(timeout=180)
def ban_list():
    bans = d2_bans.query.filter(d2_bans.banned_id != 0).all()
    ban_list = ""

    for ban in bans:
        banned = d2_user.query.filter_by(user_id=ban.banned_id).first()
        banner = d2_user.query.filter_by(user_id=ban.banner).first()

        if ban.length is not 0:
            banduration = display_time(ban.length)
        else:
            banduration = "FOREVER"
        if ban.length is -1:
            banduration = "UNBANNED"

        ban_time = syndbb.datetime.fromtimestamp(int(ban.time)).strftime('%Y-%m-%d %H:%M:%S')

        ban_list += '''<tr>
                        <td>'''+ban_time+'''</td>
                        <td><a href="/user/'''+banned.username+'''" style="'''+get_group_style_from_id(banned.user_id)+'''">'''+banned.username+'''</a></td>
                        <td>'''+ban.reason+'''</td>
                        <td>'''+banduration+'''</td>
                        <td><a href="/user/'''+banner.username+'''" style="'''+get_group_style_from_id(banner.user_id)+'''">'''+banner.username+'''</a></td>
                    </tr>'''

    return {'ban_list': ban_list}
