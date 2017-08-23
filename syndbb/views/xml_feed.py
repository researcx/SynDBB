#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb
from syndbb.models.users import d2_user, d2_bans, is_banned
from syndbb.models.forums import d2_forums, d2_activity
from syndbb.models.time import display_time, human_date
from flask import make_response

# Post Feed
# /feed/posts/xml
@syndbb.app.route("/feed/posts/xml")
@syndbb.cache.memoize(timeout=60)
def feed_posts_xml():
    activity = []
    activity_item = ""
    count = 0
    limit = 10

    posts = d2_activity.query.filter(d2_activity.replyto != 0).order_by(d2_activity.time.desc()).limit(limit).all()

    for post in posts:
        activity.append([post.time, "post", post.id])

    activity.sort(reverse=True)

    for item in activity:
        if count < limit:
            if item[1] == "post":
                post = d2_activity.query.filter(d2_activity.id == item[2]).first()
                thread = d2_activity.query.filter(d2_activity.id == post.replyto).first()
                poster = d2_user.query.filter_by(user_id=post.user_id).first()
                forum = d2_forums.query.filter(d2_forums.id == thread.category).first()

                if post and thread and poster and forum:
                    activity_item += '''<item>
                                    		<guid>'''+str(post.id)+'''</guid>
                                    		<title>'''+poster.username+''' replied to "'''+thread.title+'''" in '''+forum.name+'''</title>
                                    		<link>https://d2k5.com/'''+str(forum.short_name)+'''/'''+str(thread.id)+'''#'''+str(post.id)+'''</link>
                                    		<pubDate>'''+human_date(post.time)+'''</pubDate>
                                    	</item>'''
            count += 1

    template = syndbb.render_template('post_feed.xml', posts=activity_item)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'
    return response

# Thread Feed
# /feed/threads/xml
@syndbb.app.route("/feed/threads/xml")
@syndbb.cache.memoize(timeout=60)
def feed_threads_xml():
    activity = []
    activity_item = ""
    count = 0
    limit = 10

    threads = d2_activity.query.filter(d2_activity.category != 0).order_by(d2_activity.reply_time.desc()).limit(limit).all()

    for thread in threads:
        activity.append([thread.time, "thread", thread.id])

    activity.sort(reverse=True)

    for item in activity:
        if count < limit:
            if item[1] == "thread":
                thread = d2_activity.query.filter(d2_activity.id == item[2]).first()
                poster = d2_user.query.filter_by(user_id=thread.user_id).first()
                forum = d2_forums.query.filter(d2_forums.id == thread.category).first()

                if thread and poster and forum:
                    activity_item += '''<item>
                                    		<guid>'''+str(thread.id)+'''</guid>
                                    		<title>'''+poster.username+''' created "'''+thread.title+'''" in '''+forum.name+'''</title>
                                    		<link>https://d2k5.com/'''+str(forum.short_name)+'''/'''+str(thread.id)+'''</link>
                                    		<pubDate>'''+human_date(thread.time)+'''</pubDate>
                                    	</item>'''
            count += 1

    template = syndbb.render_template('thread_feed.xml', threads=activity_item)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'
    return response
