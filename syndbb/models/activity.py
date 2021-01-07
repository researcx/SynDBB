#
# Copyright (c) 2017 - 2020 Keira T (https://kei.info.gf). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb
from syndbb.models.users import d2_user, d2_bans, check_ban_by_id, get_group_style_by_id, get_displayed_name_by_username, get_displayed_name_by_id, get_username_by_id
from syndbb.models.channels import d2_channels, d2_activity
from syndbb.models.time import display_time, recent_date, human_date, get_ban_expiry, cdn_path

#Functions
def unique_items(L):
    found = set()
    for item in L:
        if item[3] not in found:
            yield item
            found.add(item[3])

@syndbb.app.template_filter('get_recent_posts')
@syndbb.cache.memoize(timeout=300) #get_recent_posts
def get_recent_posts(limit=20, include=[]): ## TODO: add exclusions
    activity = []
    activity_sorted = []
    posts = []
    threads = []
    activity_item = ""
    count = 0

    for included_channel in include:
        channel = d2_channels.query.filter(d2_channels.short_name == included_channel).first()
        if channel:
            post_finder = d2_activity.query.filter(d2_activity.replyto != 0).order_by(d2_activity.time.desc()).limit(limit).all()
            for post in post_finder:
                thread_check = d2_activity.query.filter(d2_activity.id == post.replyto).first()
                if thread_check:
                    category_check = d2_channels.query.filter(d2_channels.id == thread_check.category).first()
                    if included_channel == category_check.short_name:
                        posts.append(post)
            thread_finder = d2_activity.query.filter(d2_activity.category == channel.id).order_by(d2_activity.time.desc()).limit(limit).all()
            for thread in thread_finder:
                threads.append(thread)

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
                channel = d2_channels.query.filter(d2_channels.id == thread.category).first()

                if (post and thread and channel):
                    if thread.anonymous == 0 and thread.user_id:
                        threadcreator = '<a href="/user/'+get_username_by_id(thread.user_id)+'" class="profile-inline">'+get_displayed_name_by_id(thread.user_id)+'</a>'
                    else:
                        threadcreator = '<a href="#">Anonymous</a>'

                    if post.anonymous == 0 and post.user_id:
                        latestreplier = '<a href="/user/'+get_username_by_id(post.user_id)+'" class="profile-inline">'+get_displayed_name_by_id(post.user_id)+'</a>'
                    else:
                        latestreplier = '<a href="#">Anonymous</a>'

                    activity_item += '''<tr>
                                            <td class="home-channel home-channel-icon"><a href="/'''+str(channel.short_name)+'''/'''+str(thread.id)+'''#'''+str(post.id)+'''"><img src="'''+cdn_path()+'''/images/posticons/'''+str(thread.post_icon)+'''.png" alt=""/></a></td>
                                            <td class="home-channel">
                                            <span class="small align-right home-channel-latest">
                                                <span class="timedisplay">'''+recent_date(post.time)+'''</span><br/>
                                                by '''+latestreplier+''' <a href="/'''+str(channel.short_name)+'''/'''+str(thread.id)+'''#'''+str(post.id)+'''"><img src="'''+cdn_path()+'''/icons/thread_new.png" style="margin-top: -2px;"/></a>
                                            </span>
                                            <a href="/'''+str(channel.short_name)+'''/'''+str(thread.id)+'''#'''+str(post.id)+'''"><b>'''+thread.title+'''</b></a>
                                            <span class="small"><br/>
                                            '''+threadcreator+''', <span class="timedisplay">'''+recent_date(thread.time)+'''</span>, <a href="/'''+str(channel.short_name)+'''">'''+channel.name+'''</a>
                                            </span>
                                        </tr>'''
                    count += 1

            if item[1] == "thread":
                thread = d2_activity.query.filter(d2_activity.id == item[2]).first()
                channel = d2_channels.query.filter(d2_channels.id == thread.category).first()
                if (thread and channel):
                    if thread.anonymous == 0:
                        threadcreator = '<a href="/user/'+get_username_by_id(thread.user_id)+'" class="profile-inline">'+get_displayed_name_by_id(thread.user_id)+'</a>'
                    else:
                        threadcreator = '<a href="#">Anonymous</a>'
                    activity_item += '''<tr>
                                            <td class="home-channel home-channel-icon"><a href="/'''+str(channel.short_name)+'''/'''+str(thread.id)+'''"><img src="'''+cdn_path()+'''/images/posticons/'''+str(thread.post_icon)+'''.png" alt=""/></a></td>
                                            <td class="home-channel">
                                            <span class="small align-right home-channel-latest">
                                                <span class="timedisplay">'''+recent_date(thread.reply_time)+'''</span><br/>
                                                by '''+threadcreator+''' <a href="/'''+str(channel.short_name)+'''/'''+str(thread.id)+'''"><img src="'''+cdn_path()+'''/icons/thread_new.png" style="margin-top: -2px;"/></a>
                                            </span>
                                            <a href="/'''+str(channel.short_name)+'''/'''+str(thread.id)+'''"><b>'''+thread.title+'''</b></a>
                                            <span class="small"><br/>
                                            '''+threadcreator+''', <span class="timedisplay">'''+recent_date(thread.time)+'''</span>, <a href="/'''+str(channel.short_name)+'''">'''+channel.name+'''</a>
                                            </span></td>
                                        </tr>'''
                    count += 1

    return activity_item
syndbb.app.jinja_env.globals.update(get_recent_posts=get_recent_posts)

@syndbb.app.template_filter('get_activity')
@syndbb.cache.memoize(timeout=86400) # get_activity
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
                channel = d2_channels.query.filter(d2_channels.id == thread.category).first()

                if post and thread and channel and user:
                    if post.anonymous == 0:
                        latestreplier = '<a href="/user/'+get_username_by_id(post.user_id)+'" class="profile-inline">'+get_displayed_name_by_id(post.user_id)+'</a>'
                    else:
                        latestreplier = '<a href="#">Anonymous</a>'

                    activity_item += '''<tr>
                                            <td class="event-icon"><i class="silk-icon icon_comment_add" aria-hidden="true"></i></td>
                                            <td>'''+latestreplier+''' replied to "<a href="/'''+str(channel.short_name)+'''/'''+str(thread.id)+'''#'''+str(post.id)+'''">'''+thread.title+'''</a>" in <a href="/'''+str(channel.short_name)+'''">'''+channel.name+'''</a></td>
                                        </tr>'''

            if item[1] == "thread":
                thread = d2_activity.query.filter(d2_activity.id == item[2]).first()
                channel = d2_channels.query.filter(d2_channels.id == thread.category).first()

                if thread and channel:

                    if thread.anonymous == 0:
                        threadcreator = '<a href="/user/'+get_username_by_id(thread.user_id)+'" class="profile-inline">'+get_displayed_name_by_id(thread.user_id)+'</a>'
                    else:
                        threadcreator = '<a href="#">Anonymous</a>'

                    activity_item += '''<tr>
                                            <td class="event-icon"><i class="silk-icon icon_application_view_list" aria-hidden="true"></i></td>
                                            <td>'''+threadcreator+''' created "<a href="/'''+str(channel.short_name)+'''/'''+str(thread.id)+'''">'''+thread.title+'''</a>" in <a href="/'''+str(channel.short_name)+'''">'''+channel.name+'''</a></td>
                                        </tr>'''
            count += 1

    return activity_item
syndbb.app.jinja_env.globals.update(get_activity=get_activity)

@syndbb.app.context_processor
@syndbb.cache.memoize(timeout=86400) # ban_list
def ban_list():
    bans = d2_bans.query.filter(d2_bans.banned_id != 0).filter(d2_bans.display != 0).all()
    ban_list = ""

    for ban in bans:
        banned = d2_user.query.filter_by(user_id=ban.banned_id).first()
        banner = d2_user.query.filter_by(user_id=ban.banner).first()

        if ban.length is not 0:
            banduration = display_time(ban.length)
            timeleft = get_ban_expiry(ban.expires)
        else:
            banduration = "FOREVER"
            timeleft = "NEVER"
        if ban.length is -1:
            banduration = "UNBANNED"
            timeleft = "EXPIRED"



        ban_list += '''<tr>
                        <td>'''+recent_date(ban.time)+'''</td>
                        <td><a href="/user/'''+banned.username+'''" class="username '''+get_group_style_by_id(banned.user_id)+'''">'''+banned.username+'''</a></td>
                        <td>'''+ban.reason+'''</td>
                        <td>'''+banduration+'''</td>
                        <td>'''+timeleft+'''</td>
                        <td><a href="/user/'''+banner.username+'''" class="username '''+get_group_style_by_id(banner.user_id)+'''">'''+banner.username+'''</a></td>
                    </tr>'''

    return {'ban_list': ban_list}
