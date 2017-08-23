#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb, requests, hashlib
from PIL import Image, ImageOps
from io import BytesIO
from syndbb.models.forums import d2_forums, d2_activity, d2_post_ratings, parse_bbcode
from syndbb.models.users import d2_user, get_avatar, get_group_style_from_id, checkSession
from syndbb.models.time import recent_date, human_date, unix_time_current
from syndbb.models.currency import give_currency, take_currency, give_posts, take_posts

html_escape_table = {
    ">": "&gt;",
    "<": "&lt;",
    }

def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text)

def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

def all_pages():
    links = []
    for rule in syndbb.app.url_map.iter_rules():
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = syndbb.url_for(rule.endpoint, **(rule.defaults or {}))
            links.append(rule.endpoint)
    return links

### Thread/Forum Viewing/Editing ###
@syndbb.app.route("/<category>/")
def view_forum(category):
    forumcheck = d2_forums.query.filter_by(short_name=category).first()
    forumlogo = ""
    dynamic_css_header = []
    if forumcheck:
        dynamic_js_footer = ["js/inline.js", "js/bootbox.min.js"]
        if forumcheck.short_name == "yiff":
            dynamic_css_header.append("css/oify.css")

        logo_file = syndbb.os.getcwd() + "/syndbb/static/images/logos/" + forumcheck.short_name + ".png"
        if syndbb.os.path.isfile(logo_file):
            forumlogo = '<img src="/static/images/logos/' + forumcheck.short_name + '.png" alt="D2K5" class="sitelogo mask">'

        threads = d2_activity.query.filter_by(category=forumcheck.id).order_by(d2_activity.reply_time.desc()).all()

        topbuttons = '<a href="/'+forumcheck.short_name+'/grid" title="Grid View" style="float:right;"><i class="silk-icon icon_application_view_tile" aria-hidden="true"></i></a>'
        if 'logged_in' in syndbb.session:
            userid = checkSession(str(syndbb.session['logged_in']))
            if userid:
                topbuttons += '<a href="/'+forumcheck.short_name+'/new_thread" title="New Thread" style="float:right;"><i class="silk-icon icon_add" aria-hidden="true"></i></a>'

        subheading = []
        subheading.append("")
        thread_list = ""
        for thread in threads:
            if thread.reply_count is 1:
                replystr = "reply"
            else:
                replystr = "replies"
            lastpost = d2_activity.query.filter_by(replyto=thread.id).order_by(d2_activity.time.desc()).first()
            if lastpost:
                latest = lastpost.id
                latestreplier = lastpost
            else:
                latest = thread.id
                latestreplier = thread

            thread_list += '''<tr>
                                    <td class="home-forum home-forum-icon"><img src="/static/images/posticons/icon'''+str(thread.post_icon)+'''.gif" alt=""/></td>
                                    <td class="home-forum">
                                    <span class="small" style="float:right; text-align: right;">
                                        <span class="timedisplay">'''+recent_date(thread.reply_time)+'''</span><br/>
                                        by <a href="/user/'''+latestreplier.user.username+'''" class="profile-inline">'''+latestreplier.user.username+'''</a> <a href="/'''+str(forumcheck.short_name)+'''/'''+str(thread.id)+'''#'''+str(latest)+'''"><img src="/static/images/thread_new.png" style="margin-top: -2px;"/></a>
                                    </span>
                                    <a href="/'''+str(forumcheck.short_name)+'''/'''+str(thread.id)+'''"><b>'''+thread.title+'''</b></a>
                                    <span class="small"><br/>
                                    <a href="/user/'''+thread.user.username+'''" class="profile-inline">'''+thread.user.username+'''</a>, <span class="timedisplay">'''+recent_date(thread.time)+'''</span>
                                    </span>
                                    </td>
                                </tr>'''


        return syndbb.render_template('view_forum.html', forum=forumcheck, thread_list=thread_list, forumlogo=forumlogo, dynamic_js_footer=dynamic_js_footer, dynamic_css_header=dynamic_css_header, title=forumcheck.name, topbuttons=topbuttons, subheading=subheading)
    else:
        return syndbb.render_template('invalid.html', title="No page found")

### Thread/Forum Viewing/Editing ###
@syndbb.app.route("/<category>/grid")
def view_forum_grid(category):
    forumcheck = d2_forums.query.filter_by(short_name=category).first()
    forumlogo = ""
    if forumcheck:
        if forumcheck.short_name == "yiff":
            dynamic_css_header.append("css/oify.css")

        logo_file = syndbb.os.getcwd() + "/syndbb/static/images/logos/" + forumcheck.short_name + ".png"
        if syndbb.os.path.isfile(logo_file):
            forumlogo = '<img src="/static/images/logos/' + forumcheck.short_name + '.png" alt="D2K5" class="sitelogo mask">'

        image_finder = "(?<=\[img\]).*?(?=\[/img\])"
        threads = d2_activity.query.filter_by(category=forumcheck.id).order_by(d2_activity.reply_time.desc()).all()

        topbuttons = '<a href="/'+forumcheck.short_name+'" title="List View" style="float:right;"><i class="silk-icon icon_application_view_list" aria-hidden="true"></i></a>'
        if 'logged_in' in syndbb.session:
            userid = checkSession(str(syndbb.session['logged_in']))
            if userid:
                topbuttons += '<a href="/'+forumcheck.short_name+'/new_thread" title="New Thread" style="float:right;"><i class="silk-icon icon_add" aria-hidden="true"></i></a>'

        subheading = []
        subheading.append("")
        thread_list = ""
        gridview = 1
        for thread in threads:
            if thread.reply_count is 1:
                replystr = "reply"
            else:
                replystr = "replies"
            thread_title = (thread.title[:25] + '...') if len(thread.title) > 25 else thread.title
            lastpost = d2_activity.query.filter_by(replyto=thread.id).order_by(d2_activity.time.desc()).first()
            if lastpost:
                latest = lastpost.id
            else:
                latest = thread.id

            thumbfolder = syndbb.os.getcwd() + "/syndbb/static/data/threadimg/grid/"
            images = syndbb.re.findall(image_finder, thread.content, syndbb.re.IGNORECASE)
            if images:
                firstimg = images[0]
                hashname = hashlib.sha256(firstimg.encode()).hexdigest()
                thumbpath = thumbfolder + hashname + ".png"
                if not syndbb.os.path.isfile(thumbpath):
                    threadimg = requests.get(firstimg)
                    im = Image.open(BytesIO(threadimg.content))
                    im = ImageOps.fit(im, (150, 150),  Image.ANTIALIAS)
                    im.save(thumbpath, "PNG")
                timg = "/static/data/threadimg/grid/" + hashname + ".png"
            else:
                timg = "/static/images/noimage-grid.png"

            thread_list += '''<div class="panel panel-default text-center thread-grid" id="''' + str(thread.id)+ '''" onclick="location.href='/''' + forumcheck.short_name+ '''/''' + str(thread.id)+ '''';" style="cursor: pointer;">
                                  <div class="panel-body">
                                	<div class="threadimg-grid center-block">
                                	  <a href="/''' + forumcheck.short_name+ '''/''' + str(thread.id)+ '''/gallery">
                                		<img src="'''+ timg +'''" title="''' + thread.title + '''" alt="Thread Image" class="activity-threadimg-grid">
                                	  </a>
                                	</div>
                                	<a href="/''' + forumcheck.short_name+ '''/''' + str(thread.id)+ '''" title="''' + thread.title + '''"><b>''' + thread_title + '''</b></a><br>
                                	<a href="/''' + forumcheck.short_name+ '''/''' + str(thread.id)+ '''#'''+str(latest)+'''" class="activity_lastpost"><i>last active ''' + recent_date(thread.reply_time) + '''&nbsp;</i></a>
                                  </div>
                              </div> '''


        return syndbb.render_template('view_forum.html', forum=forumcheck, gridview=gridview, thread_list=thread_list, forumlogo=forumlogo, title=forumcheck.name, topbuttons=topbuttons, subheading=subheading)
    else:
        return syndbb.render_template('invalid.html', title="No page found")

### Thread/Forum Viewing/Editing ###
@syndbb.app.route("/<category>/new_thread")
def view_forum_create(category):
    forumcheck = d2_forums.query.filter_by(short_name=category).first()
    forumlogo = ""
    if forumcheck:
        dynamic_css_header = ["css/bbcode_editor.css", "css/dropdown.css"]
        dynamic_js_footer = ["js/jquery.dd.min.js", "js/jquery.rangyinputs.js", "js/bbcode_editor_forums.js", "js/threads.js", "js/inline.js", "js/bootbox.min.js"]
        if forumcheck.short_name == "yiff":
            dynamic_css_header.append("css/oify.css")

        subheading = []
        subheading.append('<a href="/'+forumcheck.short_name+'">'+forumcheck.name+'</a>')

        logo_file = syndbb.os.getcwd() + "/syndbb/static/images/logos/" + forumcheck.short_name + ".png"
        if syndbb.os.path.isfile(logo_file):
            forumlogo = '<img src="/static/images/logos/' + forumcheck.short_name + '.png" alt="D2K5" class="sitelogo mask">'

        return syndbb.render_template('new_thread.html', forum=forumcheck, forumlogo=forumlogo, dynamic_css_header=dynamic_css_header, dynamic_js_footer=dynamic_js_footer, title="New Thread", subheading=subheading)
    else:
        return syndbb.render_template('invalid.html', title="No page found")

@syndbb.app.route("/<category>/<thread>")
def view_thread(category, thread):
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(syndbb.session['logged_in']))
        if userid:
            forumcheck = d2_forums.query.filter_by(short_name=category).first()
            forumlogo = ""
            if forumcheck:
                topbuttons = '<a href="/'+forumcheck.short_name+'/'+thread+'/gallery" title="Gallery View" style="float:right;"><i class="silk-icon icon_application_view_tile" aria-hidden="true"></i></a>'
                dynamic_css_header = ["css/bbcode_editor.css"]
                dynamic_js_footer = ["js/bootstrap-filestyle.min.js", "js/jquery.rangyinputs.js", "js/bbcode_editor_forums.js", "js/posts.js", "js/post_ratings.js", "js/bootbox.min.js", "js/delete.js", "js/inline.js"]
                if forumcheck.short_name == "yiff":
                    dynamic_css_header.append("css/oify.css")
                logo_file = syndbb.os.getcwd() + "/syndbb/static/images/logos/" + forumcheck.short_name + ".png"
                if syndbb.os.path.isfile(logo_file):
                    forumlogo = '<img src="/static/images/logos/' + forumcheck.short_name + '.png" alt="D2K5" class="sitelogo mask">'
                threadcheck = d2_activity.query.filter_by(id=thread).first()
                if threadcheck:
                    subheading = []
                    subheading.append('<a href="/'+forumcheck.short_name+'">'+forumcheck.name+'</a>')
                    thread_title = (threadcheck.title[:75] + '...') if len(threadcheck.title) > 75 else threadcheck.title
                    replycheck = d2_activity.query.filter_by(replyto=thread).all()
                    return syndbb.render_template('view_thread.html', forum=forumcheck, replies=replycheck, thread=threadcheck, forumlogo=forumlogo, dynamic_css_header=dynamic_css_header, dynamic_js_footer=dynamic_js_footer, title="#"+forumcheck.short_name + " &bull; " + thread_title + " &bull; " + forumcheck.name, forumtitle=thread_title, topbuttons=topbuttons, subheading=subheading)
                else:
                    return syndbb.render_template('invalid.html', title="No thread found")
            else:
                return syndbb.render_template('invalid.html', title="No page found")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Not logged in")

@syndbb.app.route("/<category>/<thread>/gallery")
def view_thread_gallery(category, thread):
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(syndbb.session['logged_in']))
        if userid:
            forumcheck = d2_forums.query.filter_by(short_name=category).first()
            forumlogo = ""
            if forumcheck:
                topbuttons = '<a href="/'+forumcheck.short_name+'/'+thread+'" title="List View" style="float:right;"><i class="silk-icon icon_application_view_list" aria-hidden="true"></i></a>'
                dynamic_css_header = ["css/bbcode_editor.css"]
                dynamic_js_footer = ["js/jquery.rangyinputs.js", "js/bbcode_editor_forums.js", "js/posts.js", "js/bootbox.min.js", "js/delete.js", "js/inline.js"]
                if forumcheck.short_name == "yiff":
                    dynamic_css_header.append("css/oify.css")
                logo_file = syndbb.os.getcwd() + "/syndbb/static/images/logos/" + forumcheck.short_name + ".png"
                if syndbb.os.path.isfile(logo_file):
                    forumlogo = '<img src="/static/images/logos/' + forumcheck.short_name + '.png" alt="D2K5" class="sitelogo mask">'
                threadcheck = d2_activity.query.filter_by(id=thread).first()
                image_list = []
                if threadcheck:
                    thread_title = (threadcheck.title[:75] + '...') if len(threadcheck.title) > 75 else threadcheck.title

                    image_finder = "(?<=\[img\]).*?(?=\[/img\])"
                    images = syndbb.re.findall(image_finder, threadcheck.content, syndbb.re.IGNORECASE)
                    for image in images:
                        image_list.append(image)

                    replycheck = d2_activity.query.filter_by(replyto=thread).all()
                    for reply in replycheck:
                        images = syndbb.re.findall(image_finder, reply.content, syndbb.re.IGNORECASE)
                        for image in images:
                            image_list.append(image)

                    imagecount = str(len(image_list)) + " images"
                    if len(image_list) == 1:
                        imagecount = imagecount.rstrip('s')

                    subheading = []
                    subheading.append('<a href="/'+forumcheck.short_name+'">'+forumcheck.name+'</a>')

                    return syndbb.render_template('view_thread_gallery.html', forum=forumcheck, thread=threadcheck, forumlogo=forumlogo, images=image_list, imagecount=imagecount, title="#"+forumcheck.short_name + " &bull; " + thread_title + " &bull; " + forumcheck.name, forumtitle=thread_title, topbuttons=topbuttons, subheading=subheading)
                else:
                    return syndbb.render_template('invalid.html', title="No thread found")
            else:
                return syndbb.render_template('invalid.html', title="No page found")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Not logged in")

@syndbb.app.route("/post/<post>")
def view_post(post):
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(syndbb.session['logged_in']))
        if userid:
            isInline = syndbb.request.args.get('inlinecontent', '')
            postcheck = d2_activity.query.filter_by(id=post).first()
            if postcheck:
                if postcheck.title:
                    thread_title = (postcheck.title[:75] + '...') if len(postcheck.title) > 75 else postcheck.title
                    postvars = postcheck
                else:
                    threadcheck = d2_activity.query.filter_by(id=postcheck.replyto).first()
                    thread_title = (threadcheck.title[:75] + '...') if len(threadcheck.title) > 75 else threadcheck.title
                    postvars = threadcheck
                forumcheck = d2_forums.query.filter_by(id=postvars.category).first()


                return syndbb.render_template('view_post.html', isInline=isInline, post=postcheck, title="#"+forumcheck.short_name + " &bull; " + thread_title + " &bull; " + forumcheck.name, forumtitle="<a href='/" + forumcheck.short_name + "/"+str(postvars.id)+"'>" + thread_title + "</a>")
            else:
                return syndbb.render_template('invalid.html', title=" &bull; No post found")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Not logged in")

@syndbb.app.route("/posts/<user>")
def view_user_posts(user):
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(syndbb.session['logged_in']))
        if userid:
            dynamic_css_header = ["css/bbcode_editor.css"]
            isInline = syndbb.request.args.get('inlinecontent', '')
            postcheck = d2_activity.query.filter_by(user_id=user).filter(d2_activity.replyto != 0).order_by(d2_activity.time.desc()).all()
            usercheck = d2_user.query.filter_by(user_id=user).first()
            if usercheck:
                if postcheck:
                    subheading = []
                    subheading.append('<a href="/user/'+usercheck.username+'">'+usercheck.username+'</a>')
                    return syndbb.render_template('view_user_posts.html', isInline=isInline, posts=postcheck, title="All posts by " + usercheck.username, subheading=subheading)
                else:
                    return syndbb.render_template('invalid.html', title=" &bull; No posts found")
            else:
                return syndbb.render_template('invalid.html', title=" &bull; No user found")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Not logged in")

@syndbb.app.route("/threads/<user>")
def view_user_threads(user):
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(syndbb.session['logged_in']))
        if userid:
            dynamic_css_header = ["css/bbcode_editor.css"]
            isInline = syndbb.request.args.get('inlinecontent', '')
            threadcheck = d2_activity.query.filter_by(user_id=user).filter(d2_activity.replyto == 0).order_by(d2_activity.time.desc()).all()
            usercheck = d2_user.query.filter_by(user_id=user).first()
            if usercheck:
                if threadcheck:
                    thread_list = ""
                    for thread in threadcheck:
                        forumcheck = d2_forums.query.filter_by(id=thread.category).first()
                        if thread.reply_count is 1:
                            replystr = "reply"
                        else:
                            replystr = "replies"
                        lastpost = d2_activity.query.filter_by(replyto=thread.id).order_by(d2_activity.time.desc()).first()
                        if lastpost:
                            latest = lastpost.id
                            latestreplier = lastpost
                        else:
                            latest = thread.id
                            latestreplier = thread
                        thread_list += '''<tr>
                                                <td class="home-forum home-forum-icon"><img src="/static/images/posticons/icon'''+str(thread.post_icon)+'''.gif" alt=""/></td>
                                                <td class="home-forum">
                                                <span class="small" style="float:right; text-align: right;">
                                                    <span class="timedisplay">'''+recent_date(thread.reply_time)+'''</span><br/>
                                                    by <a href="/user/'''+latestreplier.user.username+'''" class="profile-inline">'''+latestreplier.user.username+'''</a> <a href="/'''+str(forumcheck.short_name)+'''/'''+str(thread.id)+'''#'''+str(latest)+'''"><img src="/static/images/thread_new.png" style="margin-top: -2px;"/></a>
                                                </span>
                                                <a href="/'''+str(forumcheck.short_name)+'''/'''+str(thread.id)+'''"><b>'''+thread.title+'''</b></a>
                                                <span class="small"><br/>
                                                <a href="/user/'''+thread.user.username+'''" class="profile-inline">'''+thread.user.username+'''</a>, <span class="timedisplay">'''+recent_date(thread.time)+'''</span>
                                                </span>
                                                </td>
                                            </tr>'''
                    subheading = []
                    subheading.append('<a href="/user/'+usercheck.username+'">'+usercheck.username+'</a>')
                    return syndbb.render_template('view_user_threads.html', dynamic_css_header=dynamic_css_header, isInline=isInline, thread_list=thread_list, title="All threads by " + usercheck.username, subheading=subheading)
                else:
                    return syndbb.render_template('invalid.html', title=" &bull; No threads found")
            else:
                return syndbb.render_template('invalid.html', title=" &bull; No threads found")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Not logged in")

@syndbb.app.route("/post/<post>/edit")
def edit_post(post):
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(syndbb.session['logged_in']))
        if userid:
            isInline = syndbb.request.args.get('inlinecontent', '')
            postcheck = d2_activity.query.filter_by(id=post).first()
            if postcheck:
                if postcheck.title:
                    thread_title = (postcheck.title[:75] + '...') if len(postcheck.title) > 75 else postcheck.title
                    postvars = postcheck
                else:
                    threadcheck = d2_activity.query.filter_by(id=postcheck.replyto).first()
                    thread_title = (threadcheck.title[:75] + '...') if len(threadcheck.title) > 75 else threadcheck.title
                    postvars = threadcheck
                forumcheck = d2_forums.query.filter_by(id=postvars.category).first()

                dynamic_css_header = ["css/bbcode_editor.css"]
                dynamic_js_footer = ["js/jquery.rangyinputs.js", "js/bbcode_editor_forums.js", "js/editing.js", "js/bootbox.min.js"]
                subheading = []
                subheading.append("<a href='/" + forumcheck.short_name + "/'>" + forumcheck.name + "</a>")
                subheading.append("<a href='/" + forumcheck.short_name + "/"+str(postvars.id)+"'>" + thread_title + "</a>")
                return syndbb.render_template('edit_post.html', isInline=isInline, post=postcheck, dynamic_css_header=dynamic_css_header, dynamic_js_footer=dynamic_js_footer, title="#"+forumcheck.short_name + " &bull; " + thread_title + " &bull; " + forumcheck.name, forumtitle="Editing Post", subheading=subheading)
            else:
                return syndbb.render_template('invalid.html', title=" &bull; No post found")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Not logged in")

### Rate Posts ###
@syndbb.app.route('/functions/rate_post/')
def do_rate_post():
    post_id = syndbb.request.args.get('post_id', '')
    ratingtype = syndbb.request.args.get('type', '')
    uniqid = syndbb.request.args.get('uniqid', '')
    if post_id and ratingtype and uniqid:
        if 'logged_in' in syndbb.session:
            userid = checkSession(str(uniqid))
            if userid:
                postcheck = d2_activity.query.filter_by(id=post_id).first()
                if postcheck:
                    ratingcheck = d2_post_ratings.query.filter_by(post_id=post_id).filter_by(user_id=userid).first()
                    if ratingcheck:
                       return "You've already rated this post."
                    post_creator = d2_user.query.filter_by(user_id=postcheck.user_id).first()

                    if ratingtype == "down":
                        post_creator.karma_negative = post_creator.karma_negative + 1
                        syndbb.db.session.commit()
                        ratingtype = -1
                    elif ratingtype == "up":
                        post_creator.karma_positive = post_creator.karma_positive + 1
                        syndbb.db.session.commit()
                        ratingtype = 1

                    postcheck.rating = int(postcheck.rating) + ratingtype
                    syndbb.db.session.commit()

                    submit_rating = d2_post_ratings(post_id, userid, ratingtype)
                    syndbb.db.session.add(submit_rating)
                    syndbb.db.session.commit()

                    return str(postcheck.id)
                else:
                    return "Trying to rate a post which doesnt exist."
        else:
            return "You are not logged in!"
    else:
        return "Invalid Request"

### Create/Preview Threads/Posts ###
@syndbb.app.route("/functions/create_thread/", methods=['GET', 'POST'])
def create_thread():
    uniqid = syndbb.request.form['uniqid']
    tname = syndbb.request.form['thread_title']
    tpost = syndbb.request.form['post_content']
    ticon = syndbb.request.form['post_icon']
    tcat = syndbb.request.form['category']
    if tname and tpost and tcat and ticon and uniqid:
        userid = checkSession(uniqid)
        if userid:
            if len(tname) < 2:
                return 'Thread title is too short (less than 2 characters).'
            elif len(tname) > 100:
                return 'Thread title is too long (over 100 characters).'
            ticon = ticon.strip("icon")
            if int(ticon) not in range(1, 35):
                return 'Thread icon doesn\'t exist.'


            forumcheck = d2_forums.query.filter_by(id=tcat).first()
            if forumcheck:
                    lastpost = d2_activity.query.filter_by(user_id=userid).order_by(d2_activity.time.desc()).first()
                    if lastpost and (unix_time_current() - lastpost.time) <= 15:
                        return "Trying to create threads too quickly, wait a while before trying again."
                    else:
                        # syndbb.flash('Your thread has been created.', 'success')
                        create_thread = d2_activity(userid, unix_time_current(), tpost, 0, 0, html_escape(tname), tcat, unix_time_current(), 0, 0, ticon)
                        syndbb.db.session.add(create_thread)
                        syndbb.db.session.flush()
                        thread_id = str(create_thread.id)
                        syndbb.db.session.commit()
                        give_currency(userid, 5)
                        give_posts(userid, 1)
                        return  "/" + forumcheck.short_name + "/" + thread_id
            else:
                return 'Trying to post in a forum which doesn\'t exist.'
        else:
            return "Invalid Session"
    else:
        return "Invalid Request"

@syndbb.app.route("/functions/create_reply/", methods=['GET', 'POST'])
def create_reply():
    uniqid = syndbb.request.form['uniqid']
    tpost = syndbb.request.form['post_content']
    reply_to = syndbb.request.form['reply_to']
    if 'reply_post' in syndbb.request.form:
        reply_post = syndbb.request.form['reply_post']
    else:
        reply_post = "0"
    if tpost and reply_to and uniqid:
        userid = checkSession(uniqid)
        if userid:
            threadcheck = d2_activity.query.filter_by(id=reply_to).first()
            if threadcheck:
                    if reply_post is not "0":
                        postcheck = d2_activity.query.filter_by(id=reply_post).first()
                        if not postcheck:
                            return 'Trying to reply to a post which doesn\'t exist.'
                    lastpost = d2_activity.query.filter_by(user_id=userid).order_by(d2_activity.time.desc()).first()
                    if lastpost and (unix_time_current() - lastpost.time) <= 15:
                        return "Trying to create posts too quickly, wait a while before trying again."
                    else:
                        # syndbb.flash('Your thread has been created.', 'success')
                        threadcheck.reply_time = unix_time_current()
                        threadcheck.reply_count += 1
                        syndbb.db.session.commit()

                        create_reply = d2_activity(userid, unix_time_current(), tpost, reply_to, reply_post, '', 0, 0, 0, 0, 1)
                        syndbb.db.session.add(create_reply)
                        syndbb.db.session.flush()
                        thread_id = str(create_reply.id)
                        syndbb.db.session.commit()
                        give_currency(userid, 2)
                        give_posts(userid, 1)
                        return  "/"
            else:
                return 'Trying to post in a thread which doesn\'t exist.'
        else:
            return "Invalid Session"
    else:
        return "Invalid Request"

@syndbb.app.route("/functions/preview_bbcode/", methods=['GET', 'POST'])
def preview_bbcode():
    tpost = syndbb.request.form['post_content']
    if tpost:
        return parse_bbcode(tpost)
    else:
        return "Invalid Request"

### Edit/Delete Posts ###
@syndbb.app.route("/functions/edit_post/", methods=['GET', 'POST'])
def do_edit():
    uniqid = syndbb.request.form['uniqid']
    editing = syndbb.request.form['editing']
    tpost = syndbb.request.form['post_content']
    if tpost and editing and uniqid:
        userid = checkSession(uniqid)
        if userid:
            editcheck = d2_activity.query.filter_by(id=editing).first()
            if editcheck.title:
                postvars = editcheck
            else:
                postvars = d2_activity.query.filter_by(id=editcheck.replyto).first()
            forumcheck = d2_forums.query.filter_by(id=postvars.category).first()
            editor = d2_user.query.filter_by(user_id=userid).first()
            if (editor.rank >= 500) or (int(editcheck.user_id) == int(userid)):
                if editcheck:
                    editcheck.content = tpost
                    syndbb.db.session.commit()

                    return "/"+forumcheck.short_name+"/"+str(postvars.id)+"#"+editing
                else:
                    return 'Trying to edit a post which doesn\'t exist.'
            else:
                return "Trying to edit a post which isn't yours."
        else:
            return "Invalid Session"
    else:
        return "Invalid Request"

@syndbb.app.route('/functions/delete_post/')
def delete_post():
    post_id = syndbb.request.args.get('post_id', '')
    uniqid = syndbb.request.args.get('uniqid', '')
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(uniqid))
        if userid:
            postcheck = d2_activity.query.filter_by(id=post_id).first()
            if postcheck:
                if postcheck.title:
                    postvars = postcheck
                else:
                    postvars = d2_activity.query.filter_by(id=postcheck.replyto).first()
                forumcheck = d2_forums.query.filter_by(id=postvars.category).first()
                user = d2_user.query.filter_by(user_id=userid).first()
                if (user.rank >= 500) or (int(postcheck.user_id) == int(userid)):
                    if postcheck.title:
                        replies = d2_activity.query.filter_by(replyto=postcheck.id).all()
                        for reply in replies:
                            syndbb.db.session.delete(reply)
                            syndbb.db.session.commit()

                        syndbb.db.session.delete(postcheck)
                        syndbb.db.session.commit()
                        take_currency(postcheck.user_id, 5)
                        take_posts(userid, 1)
                        syndbb.flash('Thread has been deleted.', 'danger')
                        return syndbb.redirect("/"+forumcheck.short_name)
                    else:
                        postvars.reply_count -= 1
                        syndbb.db.session.commit()

                        syndbb.db.session.delete(postcheck)
                        syndbb.db.session.commit()
                        take_currency(postcheck.user_id, 2)
                        take_posts(userid, 1)
                        syndbb.flash('Post has been deleted.', 'danger')
                        return syndbb.redirect("/"+forumcheck.short_name+"/"+str(postvars.id))
                else:
                    return "Trying to delete a post which isn't yours."

            else:
                return "Trying to delete a post which doesnt exist."

### Custom Forums ###
@syndbb.app.route("/request-channel/")
def request_forum():
    if 'logged_in' in syndbb.session:
        return syndbb.render_template('request_forum.html', title="New Channel", subheading=[""])
    else:
        return syndbb.render_template('error_not_logged_in.html', title="New Channel", subheading=[""])

@syndbb.app.route("/functions/custom_forum/", methods=['GET', 'POST'])
def request_custom_forum():
    uniqid = syndbb.request.form['uniqid']
    fname = syndbb.request.form['forum-name']
    fdesc = syndbb.request.form['forum-description']
    facrn = syndbb.request.form['forum-acronym']
    if 'forum-nsfw' in syndbb.request.form:
        fnsfw = 1
    else:
        fnsfw = 0
    if uniqid and fname and fdesc:
        userid = checkSession(uniqid)
        if userid:
            if not syndbb.re.match('^[\w-]+$', facrn):
                syndbb.flash('Short name contains non-alphanumeric characters.', 'danger')
                return syndbb.redirect(syndbb.url_for('request_forum'))
            if len(fname) < 5:
                syndbb.flash('Channel name is under 5 characters.', 'danger')
                return syndbb.redirect(syndbb.url_for('request_forum'))
            elif len(fname) > 25:
                syndbb.flash('Channel name is over 25 characters.', 'danger')
                return syndbb.redirect(syndbb.url_for('request_forum'))

            if len(facrn) < 1:
                syndbb.flash('Short name is under 1 character.', 'danger')
                return syndbb.redirect(syndbb.url_for('request_forum'))
            elif len(facrn) > 5:
                syndbb.flash('Short name is over 5 characters.', 'danger')
                return syndbb.redirect(syndbb.url_for('request_forum'))

            invalid_shortcodes = all_pages()
            if facrn in invalid_shortcodes:
                syndbb.flash('Attempting to use a restricted short name.', 'danger')
                return syndbb.redirect(syndbb.url_for('request_forum'))
            forumcheck = d2_forums.query.filter_by(name=fname).first()
            if forumcheck:
                syndbb.flash('A forum with that name already exists.', 'danger')
                return syndbb.redirect(syndbb.url_for('request_forum'))
            else:
                acronymcheck = d2_forums.query.filter_by(short_name=facrn).first()
                if acronymcheck:
                    syndbb.flash('A forum with this short name already exists.', 'danger')
                    return syndbb.redirect(syndbb.url_for('request_forum'))
                else:
                    requestcheck = d2_forums.query.filter_by(approved='0', owned_by=userid).first()
                    if requestcheck:
                        syndbb.flash('You\'ve already requested a forum, wait for it to be approved.', 'danger')
                        return syndbb.redirect(syndbb.url_for('request_forum'))
                    else:
                        new_forum = d2_forums(fname, facrn, fdesc, userid, fnsfw, 0)
                        syndbb.db.session.add(new_forum)
                        syndbb.db.session.commit()
                        syndbb.flash('Your request has been submitted.', 'success')
                        return syndbb.redirect(syndbb.url_for('request_forum'))
        else:
            syndbb.flash('Invalid session.', 'danger')
            return syndbb.redirect(syndbb.url_for('request_forum'))
    else:
        syndbb.flash('Invalid request.', 'danger')
        return syndbb.redirect(syndbb.url_for('request_forum'))
