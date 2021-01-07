#
# Copyright (c) 2017 - 2020 Keira T (https://kei.info.gf). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb, shutil, base64, requests, json, random
from syndbb.models.users import d2_user
from syndbb.models.d2_hash import d2_hash
from syndbb.models.channels import d2_channels, get_post_icons, get_post_thumbnail
from syndbb.views.channels import html_escape
from syndbb.models.activity import d2_activity
from syndbb.models.time import unix_time_current
from flask import make_response

@syndbb.app.route("/api/site/", methods=['GET', 'POST'])
def site_api():
    apikey = syndbb.request.form['api']
    if apikey == syndbb.core_config['site']['api']:
        # 127.0.0.1:5000/api/site/?api=INVALID_API&create_thread=true&username=admin&category=general&content=hello&title=test&icon=shitpost&anon=0
        if 'create_thread' in syndbb.request.form:
            username = syndbb.request.form['username']
            category = syndbb.request.form['category']
            content = syndbb.request.form['content']
            title = syndbb.request.form['title']
            icon = syndbb.request.form['icon']
            anon = syndbb.request.form['anon']

            if not username: return "username not set"
            if not category: return "category not set"
            if not content: return "content not set"
            if not title: return "title not set"
            if not icon: return "icon not set"
            if not anon: return "anon not set"
            
            message = """Posting as: &username="""+username+"""<br/>
                Category: &category="""+category+"""<br/>
                Content: &content="""+content+"""<br/>
                Title: &title="""+title+"""<br/>
                Icon: &icon="""+icon+"""<br/>
                Anon: &anon="""+anon+"""<br/>
                <br/>"""

            user = d2_user.query.filter_by(username=username).first()
            if not user: return "user not found"
            category = d2_channels.query.filter_by(short_name=category).first()
            if not category: return "category not found"
            thread = d2_activity.query.filter_by(title=html_escape(title)).first()
            if thread: return str(thread.id)
            tcontent = d2_activity.query.filter_by(content=content).first()
            if tcontent: return str(tcontent.id)

            allowed_icons = [] # allow all icons in the posticons folder
            for ticon in get_post_icons(whitelist=False): 
                allowed_icons.append(ticon[1])
            # allowed_icons = ['art', 'attention', 'banme', 'computers', 'en', 'event', 'fap', 'funny', 'gaming', 'gross', 'help', 'hot', 'letsplay', 'link', 'music', 'newbie', 'news', 'photos', 'politics', 'poll', 'postyour', 'question', 'rant', 'release', 'repeat', 'request', 'school', 'serious', 'shitpost', 'stupid', 'tv', 'unfunny', 'weird', 'whine']
            if icon not in allowed_icons: return "thread icon does not exist (allowed: "+ str(allowed_icons)+")"

            create_thread = d2_activity(user.user_id, unix_time_current(), content, 0, 0, html_escape(title), category.id, unix_time_current(), 0, 0, icon, int(anon))
            syndbb.db.session.add(create_thread)
            syndbb.db.session.flush()
            thread_id = str(create_thread.id)
            syndbb.db.session.commit()

            get_post_thumbnail(thread_id, 'resize', False)

            syndbb.cache.delete_memoized(syndbb.models.channels.get_thread_contents)
            syndbb.cache.delete_memoized(syndbb.models.channels.get_thread_list)
            syndbb.cache.delete_memoized(syndbb.models.activity.get_activity)
            syndbb.cache.delete_memoized(syndbb.views.xml_feed.feed_threads_xml)
            syndbb.cache.delete_memoized(syndbb.models.channels.replies_to_post)
            return str(thread_id)
        # 127.0.0.1:5000/api/site/?api=INVALID_API&create_post=true&username=admin&reply_to_thread=23&reply_to_post=23&content=hello&anon=0
        if 'create_post' in syndbb.request.form:
            username = syndbb.request.form['username']
            content = syndbb.request.form['content']
            reply_to_thread = syndbb.request.form['reply_to_thread']
            reply_to_post = syndbb.request.form['reply_to_post'] #leave as 0 for no reply to any post
            anon = syndbb.request.form['anon']

            if not username: return "username not set"
            if not content: return "content not set"
            if not reply_to_thread: return "reply_to_thread not set"
            if not reply_to_post: reply_to_post = 0
            if not anon: return "anon not set"
            
            # message = """Replying as: &username="""+username+"""<br/>
            #     To thread: &reply_to_thread="""+reply_to_thread+"""<br/>
            #     To post: &reply_to_post="""+reply_to_post+"""<br/>
            #     Content: &content="""+content+"""<br/>
            #     Anon: &anon="""+anon+"""<br/>
            #     <br/>"""

            user = d2_user.query.filter_by(username=username).first()
            if not user: return "user not found"
            thread = d2_activity.query.filter_by(id=reply_to_thread).first()
            if not thread: return "thread not found"
            if int(reply_to_post) != 0:
                post = d2_activity.query.filter_by(id=reply_to_post).first()
                if not post: return "post not found"


            cthread = d2_activity.query.filter_by(replyto=0).filter_by(content=content).first()
            if cthread: return "reply exists"
            tfcontent = d2_activity.query.filter_by(replyto=thread.id).filter_by(content=content).first()
            if tfcontent: return "reply exists"

            create_reply = d2_activity(user.user_id, unix_time_current(), content, int(reply_to_thread), int(reply_to_post), '', 0, 0, 0, 0, 1, int(anon))
            syndbb.db.session.add(create_reply)
            syndbb.db.session.flush()
            reply_id = str(create_reply.id)
            syndbb.db.session.commit()

            get_post_thumbnail(reply_id, 'resize', False)

            syndbb.cache.delete_memoized(syndbb.models.channels.get_thread_contents)
            syndbb.cache.delete_memoized(syndbb.models.channels.get_thread_list)
            syndbb.cache.delete_memoized(syndbb.models.activity.get_activity)
            syndbb.cache.delete_memoized(syndbb.views.xml_feed.feed_posts_xml)
            syndbb.cache.delete_memoized(syndbb.models.channels.replies_to_post)

            return str(reply_id)
        if 'create_user' in syndbb.request.form:
            username = syndbb.request.form['username']
            password = syndbb.request.form['password']
            rank = syndbb.request.form['rank']


            if not username: return "username not set"
            if not password: return "password not set"
            if not rank: return "rank not set"
            
            user = d2_user.query.filter_by(username=username).first()
            if user:
                return "A user with that username already exists."
            else:  
                create_user = d2_user(username=username, display_name='', token='', title='', bio='', status='', status_time=0, rank=rank, avatar_date=0, password=d2_hash(password), post_count=0, line_count=0, word_count=0, profanity_count=0, karma_positive=0, karma_negative=0, points=0, join_date=unix_time_current(), last_login=unix_time_current(), last_activity=unix_time_current(), irc_auth='', upload_auth='', user_auth='', upload_url='local', nsfw_toggle=0, full_avatar=0, tags='')
                syndbb.db.session.add(create_user)
                syndbb.db.session.flush()
                created_user_id = str(create_user.user_id)
                syndbb.db.session.commit()
            
            return str(created_user_id)
    else:
        return 0

@syndbb.app.route("/api/irc/", methods=['GET', 'POST'])
def irc_api():
    apikey = syndbb.request.args.get('api', '')

    nick = syndbb.request.args.get('nick', '')
    if nick:
        if not syndbb.re.search('^[a-z][a-z0-9-_]{2,32}$', nick, syndbb.re.IGNORECASE):
            return "Invalid nick (must match IRC standards)."
        user = d2_user.query.filter_by(username=nick).first()

        # Get user profile in XML
        # /api/irc/?nick=<nick>&get_profile=1
        get_profile = syndbb.request.args.get('get_profile', '')
        if get_profile:
            template = syndbb.render_template('userinfo.xml', user=user)
            response = make_response(template)
            response.headers['Content-Type'] = 'application/xml'
            return response

        # Count lines spoken
        # /api/irc/?api=<api>&nick=<nick>&count_lines=<amount>
        count_lines = syndbb.request.form['count_lines']
        if count_lines:
            if apikey != syndbb.core_config['site']['api']: return "invalid API"
            if int(count_lines) >= 5:
                user.points = user.points + (int(count_lines) / 2)
            user.line_count = user.line_count + int(count_lines)
            syndbb.db.session.commit()
            return str(user.line_count)

        # Count words used
        # /api/irc/?api=<api>&nick=<nick>&count_words=<amount>
        count_words = syndbb.request.form['count_words']
        if count_words:
            if apikey != syndbb.core_config['site']['api']: return "invalid API"
            if int(count_words) >= 50:
                user.points = user.points + (int(count_words) / 2)
            user.word_count = user.word_count + int(count_words)
            syndbb.db.session.commit()
            return str(user.word_count)

        # Count profanity used
        # /api/irc/?api=<api>&nick=<nick>&count_profanity=<amount>
        count_profanity = syndbb.request.form['count_profanity']
        if apikey != syndbb.core_config['site']['api']: return "invalid API"
        if count_profanity:
            user.profanity_count = user.profanity_count + int(count_profanity)
            syndbb.db.session.commit()
            return str(user.profanity_count)

        # Add positive karma
        # /api/irc/?api=<api>&nick=<nick>&karma_positive=<amount>
        karma_positive = syndbb.request.form['karma_positive']
        if apikey != syndbb.core_config['site']['api']: return "invalid API"
        if karma_positive:
            user.karma_positive = user.karma_positive + int(karma_positive)
            syndbb.db.session.commit()
            return str(user.karma_positive)

        # Add negative karma
        # /api/irc/?api=<api>&nick=<nick>&karma_negative=<amount>
        karma_negative = syndbb.request.form['karma_negative']
        if apikey != syndbb.core_config['site']['api']: return "invalid API"
        if karma_negative:
            user.karma_negative = user.karma_negative + int(karma_negative)
            syndbb.db.session.commit()
            return str(user.karma_negative)

        # Give currency
        # /api/irc/?api=<api>&nick=<nick>&give_currency=<amount>
        give_currency = syndbb.request.form['give_currency']
        if give_currency:
            if apikey != syndbb.core_config['site']['api']: return "invalid API"
            user.points = user.points + int(give_currency)
            syndbb.db.session.commit()
            return str(user.points)

        # Take currency
        # /api/irc/?api=<api>&nick=<nick>&take_currency=<amount>
        take_currency = syndbb.request.form['take_currency']
        if take_currency:
            if apikey != syndbb.core_config['site']['api']: return "invalid API"
            user.points = user.points + int(take_currency)
            syndbb.db.session.commit()
            return str(user.points)

        return "Nothing to do."
    else:
        # Do the IRC user count thing
        # /api/irc/?api=<api>&do_usercount
        do_usercount = syndbb.request.form['do_usercount']
        if do_usercount:
            if apikey != syndbb.core_config['site']['api']: return "invalid API"
            try:
                zncrequest = requests.get("https://" + syndbb.core_config['znc']['host']  + ":" + syndbb.core_config['znc']['port']  + "/mods/global/httpadmin/listusers", auth=(syndbb.core_config['znc']['user'] , syndbb.core_config['znc']['password'] ), verify=False, timeout=5)
                count_data = json.loads(zncrequest.text)
                count = str(count_data["count"])

                with open("logs/irc_users.log", "w") as text_file:
                    text_file.write(count)

                return count
            except requests.exceptions.RequestException:
                return "0"

        return "No nickname defined."
    return "Invalid request"
