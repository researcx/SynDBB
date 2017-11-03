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

html_escape_table = {
        "'":'&#39;',
        '"':'&quot;',
        '>':'&gt;',
        '<':'&lt;',
        '&':'&amp;'
    }

def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text)

def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


### Non-Forum Specific ###

# Post Feed
# /feed/posts/xml
@syndbb.app.route("/feed/posts/xml")
@syndbb.cache.memoize(timeout=60)
def feed_posts_xml_all():
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
                forum = d2_forums.query.filter(d2_forums.id == thread.category).first()

                if post and thread and forum:
                    if post.anonymous == 0:
                        latestreplier = post.user.username
                    else:
                        latestreplier = 'Anonymous'

                    activity_item += '''<item>
                                    		<guid>'''+str(post.id)+'''</guid>
                                    		<title>'''+latestreplier+''' replied to "'''+html_escape(thread.title)+'''" in '''+html_escape(forum.name)+'''</title>
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
def feed_threads_xml_all():
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
                forum = d2_forums.query.filter(d2_forums.id == thread.category).first()

                if thread and forum:
                    if thread.anonymous == 0:
                        threadcreator = thread.user.username
                    else:
                        threadcreator = 'Anonymous'

                    activity_item += '''<item>
                                    		<guid>'''+str(thread.id)+'''</guid>
                                    		<title>'''+threadcreator+''' created "'''+html_escape(thread.title)+'''" in '''+html_escape(forum.name)+'''</title>
                                    		<link>https://d2k5.com/'''+str(forum.short_name)+'''/'''+str(thread.id)+'''</link>
                                    		<pubDate>'''+human_date(thread.time)+'''</pubDate>
                                    	</item>'''
            count += 1

    template = syndbb.render_template('thread_feed.xml', threads=activity_item)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'
    return response

### Forum Specific

# Forum List
# /feed/channels
@syndbb.app.route("/feed/channels")
@syndbb.cache.memoize(timeout=60)
def feed_channels_xml():
    activity = []
    activity_item = ""
    count = 0
    limit = 512

    forums = d2_forums.query.filter(d2_forums.approved == 1).all()
    for forum in forums:
        if count < limit:
            activity_item += '''<item>
                                    <id>'''+str(forum.id)+'''</id>
                                    <channel>'''+forum.short_name+'''</channel>
                                    <name>'''+forum.name+'''</name>
                                    <description>'''+forum.description+'''</description>
                                </item>'''
            count += 1

    template = syndbb.render_template('post_feed.xml', posts=activity_item)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'
    return response

# Post Feed
# /feed/posts/xml
@syndbb.app.route("/feed/posts/xml/<sforum>")
@syndbb.cache.memoize(timeout=2)
def feed_posts_xml(sforum):
    activity = []
    activity_item = ""
    count = 0
    limit = 40

    sforum = d2_forums.query.filter(d2_forums.short_name == sforum).first()
    posts = d2_activity.query.filter(d2_activity.replyto != 0).order_by(d2_activity.time.desc()).limit(limit).all()

    for post in posts:
        activity.append([post.time, "post", post.id])

    activity.sort(reverse=True)

    for item in activity:
        if count < limit:
            if item[1] == "post":
                post = d2_activity.query.filter(d2_activity.id == item[2]).first()
                thread = d2_activity.query.filter(d2_activity.id == post.replyto).first()
                forum = d2_forums.query.filter(d2_forums.id == thread.category).first()
                
                if thread.category == sforum.id:
                    if post and thread and forum:
                        if post.anonymous == 0:
                            latestreplier = post.user.username
                        else:
                            latestreplier = 'Anonymous'

                        activity_item += '''<item>
                                                <guid>'''+str(post.id)+'''</guid>
                                                <title>'''+latestreplier+''' replied to "'''+html_escape(thread.title)+'''" in '''+html_escape(forum.name)+'''</title>
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
@syndbb.app.route("/feed/threads/xml/<sforum>")
@syndbb.cache.memoize(timeout=60)
def feed_threads_xml(sforum):
    activity = []
    activity_item = ""
    count = 0
    limit = 40
    
    sforum = d2_forums.query.filter(d2_forums.short_name == sforum).first()
    threads = d2_activity.query.filter(d2_activity.category != 0).filter(d2_activity.category == sforum.id).order_by(d2_activity.reply_time.desc()).limit(limit).all()

    for thread in threads:
        activity.append([thread.time, "thread", thread.id])

    activity.sort(reverse=True)

    for item in activity:
        if count < limit:
            if item[1] == "thread":
                thread = d2_activity.query.filter(d2_activity.id == item[2]).first()
                forum = d2_forums.query.filter(d2_forums.id == thread.category).first()

                if thread and forum:
                    if thread.anonymous == 0:
                        threadcreator = thread.user.username
                    else:
                        threadcreator = 'Anonymous'

                    activity_item += '''<item>
                                    		<guid>'''+str(thread.id)+'''</guid>
                                    		<title>'''+threadcreator+''' created "'''+html_escape(thread.title)+'''" in '''+html_escape(forum.name)+'''</title>
                                    		<link>https://d2k5.com/'''+str(forum.short_name)+'''/'''+str(thread.id)+'''</link>
                                    		<pubDate>'''+human_date(thread.time)+'''</pubDate>
                                    	</item>'''
            count += 1

    template = syndbb.render_template('thread_feed.xml', threads=activity_item)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'
    return response
