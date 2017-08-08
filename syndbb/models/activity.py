#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb
from syndbb.models.users import d2_user, d2_bans, is_banned
from syndbb.models.forums import d2_forums, d2_activity
from syndbb.models.time import display_time

#Functions
@syndbb.app.template_filter('get_activity')
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
                                            <td class="event-icon"><i class="fa fa-comments" title="New Post" aria-hidden="true"></i></td>
                                            <td class=""><a href="/user/'''+poster.username+'''" class="profile-inline">'''+poster.username+'''</a> replied to "<a href="/'''+str(forum.short_name)+'''/'''+str(thread.id)+'''#'''+str(post.id)+'''">'''+thread.title+'''</a>" in <a href="/'''+str(forum.short_name)+'''">'''+forum.name+'''</a></td>
                                        </tr>'''

            if item[1] == "thread":
                thread = d2_activity.query.filter(d2_activity.id == item[2]).first()
                poster = d2_user.query.filter_by(user_id=thread.user_id).first()
                forum = d2_forums.query.filter(d2_forums.id == thread.category).first()

                if thread and poster and forum:
                    activity_item += '''<tr>
                                            <td class="event-icon"><i class="fa fa-list-alt" title="New Thread" aria-hidden="true"></i></td>
                                            <td class=""><a href="/user/'''+poster.username+'''"  class="profile-inline">'''+poster.username+'''</a> created "<a href="/'''+str(forum.short_name)+'''/'''+str(thread.id)+'''">'''+thread.title+'''</a>" in <a href="/'''+str(forum.short_name)+'''">'''+forum.name+'''</a></td>
                                        </tr>'''
            count += 1

    return activity_item
syndbb.app.jinja_env.globals.update(get_activity=get_activity)

@syndbb.app.context_processor
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
                        <td class="">'''+ban_time+'''</td>
                        <td class=""><a href="/user/'''+banned.username+'''">'''+banned.username+'''</a></td>
                        <td class="">'''+ban.reason+'''</td>
                        <td class="">'''+banduration+'''</td>
                        <td class=""><a href="/user/'''+banner.username+'''">'''+banner.username+'''</a></td>
                    </tr>'''

    return {'banlist': ban_list}
