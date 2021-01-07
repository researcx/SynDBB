#
# Copyright (c) 2017 - 2020 Keira T (https://kei.info.gf). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb, requests, hashlib
from syndbb.models.channels import d2_channels, d2_activity, d2_post_ratings, parse_bbcode, get_post_icons, get_channel_data, get_thread_list, get_post_thumbnail, check_channel_auth, get_thread_contents
from syndbb.models.users import d2_user, get_avatar_by_id, get_group_style_by_id, check_session_by_id, get_displayed_name_by_username, get_username_by_id, get_group_style_by_username, get_displayed_name_by_id, get_linked_by_id
from syndbb.models.time import recent_date, human_date, unix_time_current, cdn_path
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

### Thread/Channel Viewing/Editing ###
@syndbb.app.route("/<category>/")
def view_channel(category):
    channelcheck = get_channel_data(category)
    channellogo = ""
    sidebar_extras = ""
    dynamic_js_footer = []
    dynamic_css_header = []
    if channelcheck:
        if not check_channel_auth(channelcheck): return syndbb.render_template('error_insufficient_permissions.html', title="Insufficient permission")
        dynamic_js_footer = ["js/inline.js", "js/bootbox.min.js"]
#        if channelcheck.short_name == "oify":
#            dynamic_css_header.append("css/oify.css")
        if (channelcheck.nsfw) and ('nsfwAllow' not in syndbb.request.cookies):
            dynamic_js_footer.append("js/nsfwprompt.js")
            dynamic_css_header.append("css/nsfw_fill.css")

        logo_file = syndbb.app.static_folder + "/images/logos/" + channelcheck.short_name + ".png"
        if syndbb.os.path.isfile(logo_file):
            channellogo = '<img src="'+cdn_path()+'/images/logos/' + channelcheck.short_name + '.png" alt="D2K5" class="sitelogo mask">'

        threads = get_thread_list(channelcheck.id)

        topbuttons = '<a href="/'+channelcheck.short_name+'/grid" title="Grid View" style="float:right;"><i class="silk-icon icon_application_view_tile" aria-hidden="true"></i></a>'
        if channelcheck.chat_url: topbuttons += '<a href="'+channelcheck.chat_url+'" title="Join Chat" style="float:right;"><i class="silk-icon icon_comments" aria-hidden="true"></i></a>'
        if 'logged_in' in syndbb.session:
            userid = check_session_by_id(str(syndbb.session['logged_in']))
            if userid:
                topbuttons += '<a href="/'+channelcheck.short_name+'/new_thread" title="New Thread" style="float:right;"><i class="silk-icon icon_add" aria-hidden="true"></i></a>'

        subheading = []
        subheading.append("")
        thread_list = ""
        for thread in threads:
            if thread.reply_count == 1:
                replystr = "reply"
            else:
                replystr = "replies"
            if thread.anonymous == 0:
                threadcreator = '<a href="/user/'+get_username_by_id(thread.user_id)+'" class="profile-inline">'+get_displayed_name_by_id(thread.user_id)+'</a>'
                latestreplier = '<a href="/user/'+get_username_by_id(thread.user_id)+'" class="profile-inline">'+get_displayed_name_by_id(thread.user_id)+'</a>'
            else:
                threadcreator = '<a href="#">Anonymous</a>'
                latestreplier = '<a href="#">Anonymous</a>'

            lastpost = d2_activity.query.filter_by(replyto=thread.id).order_by(d2_activity.time.desc()).first()
            if lastpost:
                latest = lastpost.id
                latestreplier = lastpost
                if lastpost.anonymous == 0 and lastpost.user_id:
                    latestreplier = '<a href="/user/'+get_username_by_id(lastpost.user_id)+'" class="profile-inline">'+get_displayed_name_by_id(lastpost.user_id)+'</a>'
                else:
                    latestreplier = '<a href="#">Anonymous</a>'
            else:
                latest = thread.id


            thread_list += '''<tr>
                                    <td class="home-channel home-channel-icon"><img src="'''+cdn_path()+'''/images/posticons/'''+str(thread.post_icon)+'''.png" alt=""/></td>
                                    <td class="home-channel">
                                    <span class="small" style="float:right; text-align: right;">
                                        <span class="timedisplay">'''+recent_date(thread.reply_time)+'''</span><br/>
                                        by '''+latestreplier+'''</a> <a href="/'''+str(channelcheck.short_name)+'''/'''+str(thread.id)+'''#'''+str(latest)+'''"><img src="'''+cdn_path()+'''/icons/thread_new.png" style="margin-top: -2px;"/></a>
                                    </span>
                                    <a href="/'''+str(channelcheck.short_name)+'''/'''+str(thread.id)+'''"><b>'''+thread.title+'''</b></a>
                                    <span class="small"><br/>
                                    '''+threadcreator+''', <span class="timedisplay">'''+recent_date(thread.time)+'''</span>
                                    </span>
                                    </td>
                                </tr>'''

        sidebar_extras = "<center><h4>"+channelcheck.name+"</h4></center>"
        sidebar_extras += '''<dl class="dl-horizontal statistics" style="margin-top: 10px; margin-bottom: 10px;">'''
        if channelcheck.description and channelcheck.description != "":
            sidebar_extras += '''<dt>Description:</dt>
            <dd>'''+ str(channelcheck.description) +'''</dd>'''
        if channelcheck.mod_list and channelcheck.mod_list != "":
            moderator_list_txt = ""
            for mod in channelcheck.mod_list.split(" "):
                if get_displayed_name_by_username(mod):
                    moderator_list_txt += '<a href="/user/'+mod+'" class="username '+get_group_style_by_username(mod)+'">'+get_displayed_name_by_username(mod)+'</a><br/>' 
            sidebar_extras += '''<dt>Moderators:</dt>
            <dd>'''+ moderator_list_txt +'''</dd>'''
        if channelcheck.user_list and channelcheck.user_list != "":
            usr_list_txt = ""
            for usr in channelcheck.user_list.split(" "):
                if get_displayed_name_by_username(usr):
                    usr_list_txt += '<a href="/user/'+usr+'" class="username '+get_group_style_by_username(usr)+'">'+get_displayed_name_by_username(usr)+'</a><br/>' 
            sidebar_extras += '''<dt>Members:</dt>
            <dd>'''+ usr_list_txt +'''</dd>'''
        sidebar_extras += '''</dl>'''
        return syndbb.render_template('view_channel.html', channel=channelcheck, thread_list=thread_list, channellogo=channellogo, dynamic_js_footer=dynamic_js_footer, dynamic_css_header=dynamic_css_header, title=channelcheck.name, topbuttons=topbuttons, subheading=subheading, sidebar_extras=sidebar_extras)
    else:
        return syndbb.render_template('invalid.html', title="No page found")

### Thread/Channel Viewing/Editing ###
@syndbb.app.route("/<category>/grid")
def view_channel_grid(category):
    channelcheck = get_channel_data(category)
    channellogo = ""
    sidebar_extras = ""
    dynamic_js_footer = []
    dynamic_css_header = []
    if channelcheck:
        if not check_channel_auth(channelcheck): return syndbb.render_template('error_insufficient_permissions.html', title="Insufficient permission")
#        if channelcheck.short_name == "oify":
#            dynamic_css_header.append("css/oify.css")
        if (channelcheck.nsfw) and ('nsfwAllow' not in syndbb.request.cookies):
            dynamic_js_footer.append("js/nsfwprompt.js")
            dynamic_css_header.append("css/nsfw_fill.css")

        logo_file = syndbb.app.static_folder + "/images/logos/" + channelcheck.short_name + ".png"
        if syndbb.os.path.isfile(logo_file):
            channellogo = '<img src="'+cdn_path()+'/images/logos/' + channelcheck.short_name + '.png" alt="D2K5" class="sitelogo mask">'

        threads = get_thread_list(channelcheck.id)

        topbuttons = '<a href="/'+channelcheck.short_name+'" title="List View" style="float:right;"><i class="silk-icon icon_application_view_list" aria-hidden="true"></i></a>'
        if channelcheck.chat_url: topbuttons += '<a href="'+channelcheck.chat_url+'" title="Join Chat" style="float:right;"><i class="silk-icon icon_comments" aria-hidden="true"></i></a>'
        if 'logged_in' in syndbb.session:
            userid = check_session_by_id(str(syndbb.session['logged_in']))
            if userid:
                topbuttons += '<a href="/'+channelcheck.short_name+'/new_thread" title="New Thread" style="float:right;"><i class="silk-icon icon_add" aria-hidden="true"></i></a>'

        subheading = []
        subheading.append("")
        thread_list = ""
        gridview = 1
        for thread in threads:
            if thread.reply_count == 1:
                replystr = "reply"
            else:
                replystr = "replies"
            thread_title = (thread.title[:25] + '...') if len(thread.title) > 25 else thread.title
            lastpost = d2_activity.query.filter_by(replyto=thread.id).order_by(d2_activity.time.desc()).first()
            if lastpost:
                latest = lastpost.id
            else:
                latest = thread.id

            timg = get_post_thumbnail(thread.id, method="crop", recheck=False)['src']

            thread_list += '''<div class="panel panel-default text-center thread-grid" id="''' + str(thread.id)+ '''" onclick="location.href='/''' + channelcheck.short_name+ '''/''' + str(thread.id)+ '''';" style="cursor: pointer;">
                                  <div class="panel-body">
                                	<div class="threadimg-grid center-block">
                                	  <a href="/''' + channelcheck.short_name+ '''/''' + str(thread.id)+ '''/gallery">
                                		<img src="'''+ timg +'''" title="''' + thread.title + '''" alt="Thread Image" class="activity-threadimg-grid">
                                	  </a>
                                	</div>
                                	<a href="/''' + channelcheck.short_name+ '''/''' + str(thread.id)+ '''" title="''' + thread.title + '''"><b>''' + thread_title + '''</b></a><br/>
                                	<a href="/''' + channelcheck.short_name+ '''/''' + str(thread.id)+ '''#'''+str(latest)+'''" class="activity_lastpost"><i>last active ''' + recent_date(thread.reply_time) + '''&nbsp;</i></a>
                                  </div>
                              </div> '''
        sidebar_extras = "<center><h4>"+channelcheck.name+"</h4></center>"
        sidebar_extras += '''<dl class="dl-horizontal statistics" style="margin-top: 10px; margin-bottom: 10px;">'''
        if channelcheck.description and channelcheck.description != "":
            sidebar_extras += '''<dt>Description:</dt>
            <dd>'''+ channelcheck.description +'''</dd>'''
        if channelcheck.mod_list and channelcheck.mod_list != "":
            moderator_list = []
            moderator_list_txt = ""
            for mod in channelcheck.mod_list.split(" "):
                if get_displayed_name_by_username(mod):
                    moderator_list_txt += '<a href="/user/'+mod+'" class="username '+get_group_style_by_username(mod)+'">'+get_displayed_name_by_username(mod)+'</a><br/>' 
            sidebar_extras += '''<dt>Moderators:</dt>
            <dd>'''+ moderator_list_txt +'''</dd>'''
        sidebar_extras += '''</dl>'''
        return syndbb.render_template('view_channel.html', channel=channelcheck, gridview=gridview, thread_list=thread_list, channellogo=channellogo, title=channelcheck.name, topbuttons=topbuttons, subheading=subheading, sidebar_extras=sidebar_extras)
    else:
        return syndbb.render_template('invalid.html', title="No page found")

### Thread/Channel Viewing/Editing ###
@syndbb.app.route("/<category>/new_thread")
def view_channel_create(category):
    sidebar_extras = ""
    channelcheck = get_channel_data(category)
    channellogo = ""
    if 'logged_in' in syndbb.session:
        userid = check_session_by_id(str(syndbb.session['logged_in']))
        if userid:
            if channelcheck:
                if not check_channel_auth(channelcheck): return syndbb.render_template('error_insufficient_permissions.html', title="Insufficient permission")
                dynamic_css_header = ["css/bbcode_editor.css", "css/dropdown.css"]
                dynamic_js_footer = ["js/jquery.dd.min.js", "js/jquery.rangyinputs.js", "js/bbcode_editor_channels.js", "js/threads.js", "js/inline.js", "js/bootbox.min.js"]
#                if channelcheck.short_name == "oify":
#                    dynamic_css_header.append("css/oify.css")

                subheading = []
                subheading.append('<a href="/'+channelcheck.short_name+'">'+channelcheck.name+'</a>')

                logo_file = syndbb.app.static_folder + "/images/logos/" + channelcheck.short_name + ".png"
                if syndbb.os.path.isfile(logo_file):
                    channellogo = '<img src="'+cdn_path()+'/images/logos/' + channelcheck.short_name + '.png" alt="D2K5" class="sitelogo mask">'

                sidebar_extras = "<center><h4>"+channelcheck.name+"</h4></center>"
                sidebar_extras += '''<dl class="dl-horizontal statistics" style="margin-top: 10px; margin-bottom: 10px;">'''
                if channelcheck.description and channelcheck.description != "":
                    sidebar_extras += '''<dt>Description:</dt>
                    <dd>'''+ channelcheck.description +'''</dd>'''
                if channelcheck.mod_list and channelcheck.mod_list != "":
                    moderator_list = []
                    moderator_list_txt = ""
                    for mod in channelcheck.mod_list.split(" "):
                        if get_displayed_name_by_username(mod):
                            moderator_list_txt += '<a href="/user/'+mod+'" class="username '+get_group_style_by_username(mod)+'">'+get_displayed_name_by_username(mod)+'</a><br/>' 
                    sidebar_extras += '''<dt>Moderators:</dt>
                    <dd>'''+ moderator_list_txt +'''</dd>'''
                sidebar_extras += '''</dl>'''

                return syndbb.render_template('new_thread.html', channel=channelcheck, channellogo=channellogo, dynamic_css_header=dynamic_css_header, dynamic_js_footer=dynamic_js_footer, title="New Thread", subheading=subheading, sidebar_extras=sidebar_extras)
            else:
                return syndbb.render_template('invalid.html', title="No page found")
        else:
            return syndbb.render_template('error_not_logged_in.html', title="Not logged in")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Not logged in")

@syndbb.app.route("/<category>/<thread>")
def view_thread(category, thread):
    channelcheck = get_channel_data(category)
    sidebar_extras = ""
    channellogo = ""
    if channelcheck:
        if not check_channel_auth(channelcheck): return syndbb.render_template('error_insufficient_permissions.html', title="Insufficient permission")
        topbuttons = '<a href="/'+channelcheck.short_name+'/'+thread+'/gallery" title="Gallery View" style="float:right;"><i class="silk-icon icon_application_view_tile" aria-hidden="true"></i></a>'
        dynamic_css_header = ["css/bbcode_editor.css"]
        dynamic_js_footer = ["js/bootstrap-filestyle.min.js", "js/jquery.rangyinputs.js", "js/bbcode_editor_channels.js", "js/posts.js", "js/post_ratings.js", "js/bootbox.min.js", "js/delete.js", "js/inline.js"]
#            if channelcheck.short_name == "oify":
#                dynamic_css_header.append("css/oify.css")
        if (channelcheck.nsfw) and ('nsfwAllow' not in syndbb.request.cookies):
            dynamic_js_footer.append("js/nsfwprompt.js")
            dynamic_css_header.append("css/nsfw_fill.css")
        logo_file = syndbb.app.static_folder + "/images/logos/" + channelcheck.short_name + ".png"
        if syndbb.os.path.isfile(logo_file):
            channellogo = '<img src="'+cdn_path()+'/images/logos/' + channelcheck.short_name + '.png" alt="D2K5" class="sitelogo mask">'
        threadcheck = get_thread_contents(thread)
        if threadcheck:
            subheading = []
            subheading.append('<a href="/'+channelcheck.short_name+'">'+channelcheck.name+'</a>')
            thread_title = (threadcheck.title[:75] + '...') if len(threadcheck.title) > 75 else threadcheck.title
            replycheck = d2_activity.query.filter_by(replyto=thread).all()

            participants_txt = ""
            participant_list = []
            if not threadcheck.anonymous:
                participant_list.append(get_username_by_id(threadcheck.user_id))
            for reply in replycheck:
                if not reply.anonymous:
                    participant_list.append(get_username_by_id(reply.user_id))
            for participant in list(dict.fromkeys(participant_list)):
                if get_displayed_name_by_username(participant):
                    participants_txt += '<a href="/user/'+participant+'" class="username '+get_group_style_by_username(participant)+'">'+get_displayed_name_by_username(participant)+'</a><br/>' 

            sidebar_extras = "<center><h4 style='padding-left: 8px; padding-right: 8px;'>"+thread_title+"</h4></center>"
            sidebar_extras += '''<dl class="dl-horizontal statistics" style="margin-top: 10px; margin-bottom: 10px;">'''
            if participants_txt:
                sidebar_extras += '''<dt>Participants:</dt>
                <dd>'''+ participants_txt +'''</dd>'''
            sidebar_extras += '''</dl>'''
            sidebar_extras += '''<dl class="dl-horizontal statistics" style="margin-top: 10px; margin-bottom: 10px;">'''
            sidebar_extras += '''<dt>Channel:</dt>
            <dd>'''+ channelcheck.name +'''</dd>'''
            if channelcheck.mod_list != "":
                moderator_list = []
                moderator_list_txt = ""
                for mod in channelcheck.mod_list.split(" "):
                    if get_displayed_name_by_username(mod):
                        moderator_list_txt += '<a href="/user/'+mod+'" class="username '+get_group_style_by_username(mod)+'">'+get_displayed_name_by_username(mod)+'</a><br/>' 
                sidebar_extras += '''<dt>Moderators:</dt>
                <dd>'''+ moderator_list_txt +'''</dd>'''
            sidebar_extras += '''</dl>'''
            if channelcheck.type == 0:
                template = "view_thread.html"
            if channelcheck.type == 1:
                template = "view_thread_imageboard.html"
            return syndbb.render_template(template, channel=channelcheck, replies=replycheck, thread=threadcheck, channellogo=channellogo, dynamic_css_header=dynamic_css_header, dynamic_js_footer=dynamic_js_footer, title="#"+channelcheck.short_name + " &bull; " + thread_title + " &bull; " + channelcheck.name, channeltitle=thread_title, topbuttons=topbuttons, subheading=subheading, sidebar_extras=sidebar_extras)
        else:
            return syndbb.render_template('invalid.html', title="No thread found")
    else:
        return syndbb.render_template('invalid.html', title="No page found")


@syndbb.app.route("/<category>/<thread>/gallery")
def view_thread_gallery(category, thread):
    channelcheck = get_channel_data(category)
    channellogo = ""
    if channelcheck:
        if not check_channel_auth(channelcheck): return syndbb.render_template('error_insufficient_permissions.html', title="Insufficient permission")
        topbuttons = '<a href="/'+channelcheck.short_name+'/'+thread+'" title="List View" style="float:right;"><i class="silk-icon icon_application_view_list" aria-hidden="true"></i></a>'
        dynamic_css_header = ["css/bbcode_editor.css"]
        dynamic_js_footer = ["js/jquery.rangyinputs.js", "js/bbcode_editor_channels.js", "js/posts.js", "js/bootbox.min.js", "js/delete.js", "js/inline.js"]
#            if channelcheck.short_name == "oify":
#                dynamic_css_header.append("css/oify.css")
        if (channelcheck.nsfw) and ('nsfwAllow' not in syndbb.request.cookies):
            dynamic_js_footer.append("js/nsfwprompt.js")
            dynamic_css_header.append("css/nsfw_fill.css")
        logo_file = syndbb.app.static_folder + "/images/logos/" + channelcheck.short_name + ".png"
        if syndbb.os.path.isfile(logo_file):
            channellogo = '<img src="'+cdn_path()+'/images/logos/' + channelcheck.short_name + '.png" alt="D2K5" class="sitelogo mask">'
        threadcheck = get_thread_contents(thread)
        image_list = []
        if threadcheck:
            lists = ["(?<=\[img\]).*?(?=\[/img\])", "(?<=\[t\]).*?(?=\[/t\])", "(?<=\[ct\]).*?(?=\[/ct\])"]            
            for type in lists:
                images = syndbb.re.findall(type, threadcheck.content, syndbb.re.IGNORECASE)
                thread_title = (threadcheck.title[:75] + '...') if len(threadcheck.title) > 75 else threadcheck.title
                for image in images:
                    image_list.append(image)
                replycheck = d2_activity.query.filter_by(replyto=thread).all()
                for reply in replycheck:
                    images = syndbb.re.findall(type, reply.content, syndbb.re.IGNORECASE)
                    for image in images:
                        image_list.append(image)

                imagecount = str(len(image_list)) + " images"
                if len(image_list) == 1:
                    imagecount = imagecount.rstrip('s')

            subheading = []
            subheading.append('<a href="/'+channelcheck.short_name+'">'+channelcheck.name+'</a>')

            return syndbb.render_template('view_thread_gallery.html', channel=channelcheck, thread=threadcheck, channellogo=channellogo, images=image_list, imagecount=imagecount, title="#"+channelcheck.short_name + " &bull; " + thread_title + " &bull; " + channelcheck.name, channeltitle=thread_title, topbuttons=topbuttons, subheading=subheading)
        else:
            return syndbb.render_template('invalid.html', title="No thread found")
    else:
        return syndbb.render_template('invalid.html', title="No page found")

@syndbb.app.route("/post/<post>")
def view_post(post):
    isInline = syndbb.request.args.get('inlinecontent', '')
    postcheck = d2_activity.query.filter_by(id=post).first()
    if postcheck:
        if postcheck.title:
            thread_title = (postcheck.title[:75] + '...') if len(postcheck.title) > 75 else postcheck.title
            postvars = postcheck
        else:
            threadcheck = get_thread_contents(postcheck.replyto)
            thread_title = (threadcheck.title[:75] + '...') if len(threadcheck.title) > 75 else threadcheck.title
            postvars = threadcheck
        channelcheck = d2_channels.query.filter_by(id=postvars.category).first()
        if not check_channel_auth(channelcheck): return syndbb.render_template('error_insufficient_permissions.html', title="Insufficient permission")
        return syndbb.render_template('view_post.html', isInline=isInline, post=postcheck, title="#"+channelcheck.short_name + " &bull; " + thread_title + " &bull; " + channelcheck.name, channeltitle="<a href='/" + channelcheck.short_name + "/"+str(postvars.id)+"'>" + thread_title + "</a>")
    else:
        return syndbb.render_template('invalid.html', title=" &bull; No post found")

@syndbb.app.route("/posts/<user>")
def view_user_posts(user):
    if 'logged_in' in syndbb.session:
        userid = check_session_by_id(str(syndbb.session['logged_in']))
        if userid:
            dynamic_css_header = ["css/bbcode_editor.css"]
            isInline = syndbb.request.args.get('inlinecontent', '')
            posts = []
            postcheck = d2_activity.query.filter_by(user_id=user).filter(d2_activity.replyto != 0).filter(d2_activity.anonymous != 1).order_by(d2_activity.time.desc()).all()
            usercheck = d2_user.query.filter_by(user_id=user).first()

            if usercheck:
                if postcheck:
                    for post in postcheck:
                        replycheck = d2_activity.query.filter_by(id=post.replyto).first()
                        channelcheck = d2_channels.query.filter_by(id=replycheck.category).first()
                        if channelcheck and check_channel_auth(channelcheck): posts.append(post)
                    syndbb.logger.debug(posts)
                    subheading = []
                    subheading.append('<a href="/user/'+usercheck.username+'">'+usercheck.username+'</a>')
                    return syndbb.render_template('view_user_posts.html', isInline=isInline, posts=posts, title="All posts by " + usercheck.username, subheading=subheading)
                else:
                    return syndbb.render_template('invalid.html', title=" &bull; No posts found")
            else:
                return syndbb.render_template('invalid.html', title=" &bull; No user found")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Not logged in")

@syndbb.app.route("/threads/<user>")
def view_user_threads(user):
    if 'logged_in' in syndbb.session:
        userid = check_session_by_id(str(syndbb.session['logged_in']))
        if userid:
            dynamic_css_header = ["css/bbcode_editor.css"]
            isInline = syndbb.request.args.get('inlinecontent', '')
            threadcheck = d2_activity.query.filter_by(user_id=user).filter(d2_activity.replyto == 0).filter(d2_activity.anonymous != 1).order_by(d2_activity.time.desc()).all()
            usercheck = d2_user.query.filter_by(user_id=user).first()
            if usercheck:
                if threadcheck:
                    thread_list = ""
                    for thread in threadcheck:
                        channelcheck = d2_channels.query.filter_by(id=thread.category).first()
                        if channelcheck and check_channel_auth(channelcheck):
                            if thread.reply_count == 1:
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
                                                    <td class="home-channel home-channel-icon"><img src="'''+cdn_path()+'''/images/posticons/'''+str(thread.post_icon)+'''.png" alt=""/></td>
                                                    <td class="home-channel">
                                                    <span class="small" style="float:right; text-align: right;">
                                                        <span class="timedisplay">'''+recent_date(thread.reply_time)+'''</span><br/>
                                                        by <a href="/user/'''+get_username_by_id(latestreplier.user_id)+'''" class="profile-inline">'''+get_username_by_id(latestreplier.user_id)+'''</a> <a href="/'''+str(channelcheck.short_name)+'''/'''+str(thread.id)+'''#'''+str(latest)+'''"><img src="'''+cdn_path()+'''/icons/thread_new.png" style="margin-top: -2px;"/></a>
                                                    </span>
                                                    <a href="/'''+str(channelcheck.short_name)+'''/'''+str(thread.id)+'''"><b>'''+thread.title+'''</b></a>
                                                    <span class="small"><br/>
                                                    <a href="/user/'''+get_username_by_id(thread.user_id)+'''" class="profile-inline">'''+get_username_by_id(thread.user_id)+'''</a>, <span class="timedisplay">'''+recent_date(thread.time)+'''</span>
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
        userid = check_session_by_id(str(syndbb.session['logged_in']))
        if userid:
            isInline = syndbb.request.args.get('inlinecontent', '')
            postcheck = d2_activity.query.filter_by(id=post).first()
            if postcheck:
                if postcheck.title:
                    thread_title = (postcheck.title[:75] + '...') if len(postcheck.title) > 75 else postcheck.title
                    postvars = postcheck
                else:
                    threadcheck = get_thread_contents(postcheck.replyto)
                    thread_title = (threadcheck.title[:75] + '...') if len(threadcheck.title) > 75 else threadcheck.title
                    postvars = threadcheck
                channelcheck = d2_channels.query.filter_by(id=postvars.category).first()
                if not check_channel_auth(channelcheck): return syndbb.render_template('error_insufficient_permissions.html', title="Insufficient permission")

                dynamic_css_header = ["css/bbcode_editor.css"]
                dynamic_js_footer = ["js/jquery.rangyinputs.js", "js/bbcode_editor_channels.js", "js/editing.js", "js/bootbox.min.js"]
                subheading = []
                subheading.append("<a href='/" + channelcheck.short_name + "/'>" + channelcheck.name + "</a>")
                subheading.append("<a href='/" + channelcheck.short_name + "/"+str(postvars.id)+"'>" + thread_title + "</a>")
                return syndbb.render_template('edit_post.html', isInline=isInline, post=postcheck, dynamic_css_header=dynamic_css_header, dynamic_js_footer=dynamic_js_footer, title="#"+channelcheck.short_name + " &bull; " + thread_title + " &bull; " + channelcheck.name, channeltitle="Editing Post", subheading=subheading)
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
            userid = check_session_by_id(str(uniqid))
            if userid:
                postcheck = d2_activity.query.filter_by(id=post_id).first()
                if postcheck:
                    if postcheck.replyto != 0:
                        replycheck = d2_activity.query.filter_by(id=postcheck.replyto).first()
                        channelcheck = d2_channels.query.filter_by(id=replycheck.category).first()
                    if postcheck.category != 0:
                        channelcheck = d2_channels.query.filter_by(id=postcheck.category).first()
                    if channelcheck and not check_channel_auth(channelcheck): return "Insufficient permission!"

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

                    syndbb.cache.delete_memoized(syndbb.models.channels.get_post_rating)

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
    post_as = int(syndbb.request.form['post_as']) if 'post_as' in syndbb.request.form else check_session_by_id(uniqid)
    anonymous = 0
    allowed_icons = []
    for tficon in get_post_icons(whitelist=True): 
        allowed_icons.append(tficon[1])
    if not tname:
        return "Thread title not specified."
    if not tpost:
        return "No thread content."
    if not tcat:
        return "No category specified."
    if not ticon:
        return "No thread icon specified."
    if tname and tpost and tcat and ticon and uniqid:
        userid = check_session_by_id(uniqid)
        if userid:
            if len(tname) < 2:
                return 'Thread title is too short (less than 2 characters).'
            elif len(tname) > 100:
                return 'Thread title is too long (over 100 characters).'
            if ticon not in allowed_icons:
                return 'Invalid thread icon.'

            channelcheck = d2_channels.query.filter_by(id=tcat).first()
            if channelcheck:
                    if not check_channel_auth(channelcheck): return "Insufficient permission"
                    allowed_ids = []
                    for profile in get_linked_by_id(userid):
                        allowed_ids.append(profile.user_id)
                    if post_as in allowed_ids:
                        userid = post_as
                    if post_as == 0:
                        anonymous = 1
                    if channelcheck.anon == 0:
                        anonymous = 0
                    lastpost = d2_activity.query.filter_by(user_id=userid).order_by(d2_activity.time.desc()).first()
                    if lastpost and (unix_time_current() - lastpost.time) <= syndbb.core_config['site']['post_timeout']:
                        return "Trying to create threads too quickly, wait a while before trying again."
                    else:
                        # syndbb.flash('Your thread has been created.', 'success')
                        create_thread = d2_activity(userid, unix_time_current(), tpost, 0, 0, html_escape(tname), tcat, unix_time_current(), 0, 0, ticon, anonymous)
                        syndbb.db.session.add(create_thread)
                        syndbb.db.session.flush()
                        thread_id = str(create_thread.id)
                        syndbb.db.session.commit()
                        give_currency(userid, 5)
                        give_posts(userid, 1)
    
                        syndbb.cache.delete_memoized(syndbb.models.channels.get_thread_contents)
                        syndbb.cache.delete_memoized(syndbb.models.channels.get_thread_list)
                        syndbb.cache.delete_memoized(syndbb.models.activity.get_recent_posts)
                        syndbb.cache.delete_memoized(syndbb.models.activity.get_activity)
                        syndbb.cache.delete_memoized(syndbb.views.xml_feed.feed_threads_xml)
                        syndbb.cache.delete_memoized(syndbb.models.channels.replies_to_post)
                        syndbb.cache.delete_memoized(syndbb.models.channels.get_channel_list)

                        return  "/" + channelcheck.short_name + "/" + thread_id
            else:
                return 'Trying to post in a channel which doesn\'t exist.'
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
    post_as = int(syndbb.request.form['post_as']) if 'post_as' in syndbb.request.form else check_session_by_id(uniqid)
    anonymous = 0
    if tpost and reply_to and uniqid:
        userid = check_session_by_id(uniqid)
        if userid:
            threadcheck = get_thread_contents(reply_to)
            if threadcheck:
                channelcheck = d2_channels.query.filter_by(id=threadcheck.category).first()
                if channelcheck:
                    if not check_channel_auth(channelcheck): return "Insufficient permission"
                    allowed_ids = []
                    for profile in get_linked_by_id(userid):
                        allowed_ids.append(profile.user_id)
                    if post_as in allowed_ids:
                        userid = post_as
                    if post_as == 0:
                        anonymous = 1
                    if channelcheck.anon == 0:
                        anonymous = 0
                    if reply_post != "0":
                        postcheck = d2_activity.query.filter_by(id=reply_post).first()
                        if not postcheck:
                            return 'Trying to reply to a post which doesn\'t exist.'
                    lastpost = d2_activity.query.filter_by(user_id=userid).order_by(d2_activity.time.desc()).first()
                    if lastpost and (unix_time_current() - lastpost.time) <= int(syndbb.core_config['site']['post_timeout'] ):
                        return "Trying to post too quickly, wait a while before trying again."
                    else:
                        # syndbb.flash('Your thread has been created.', 'success')
                        threadcheck.reply_time = unix_time_current()
                        threadcheck.reply_count += 1
                        syndbb.db.session.commit()

                        create_reply = d2_activity(userid, unix_time_current(), tpost, reply_to, reply_post, '', 0, 0, 0, 0, 1, anonymous)
                        syndbb.db.session.add(create_reply)
                        syndbb.db.session.flush()
                        thread_id = str(create_reply.id)
                        syndbb.db.session.commit()
                        give_currency(userid, 2)
                        give_posts(userid, 1)

                        syndbb.cache.delete_memoized(syndbb.models.channels.get_thread_contents)
                        syndbb.cache.delete_memoized(syndbb.models.channels.get_thread_list)
                        syndbb.cache.delete_memoized(syndbb.models.activity.get_recent_posts)
                        syndbb.cache.delete_memoized(syndbb.models.activity.get_activity)
                        syndbb.cache.delete_memoized(syndbb.views.xml_feed.feed_posts_xml)
                        syndbb.cache.delete_memoized(syndbb.models.channels.replies_to_post)
                        syndbb.cache.delete_memoized(syndbb.models.channels.get_channel_list)

                        return  "/"
                else:
                    return "Channel not found!"
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
        userid = check_session_by_id(uniqid)
        if userid:
            editcheck = d2_activity.query.filter_by(id=editing).first()
            if editcheck.title:
                postvars = editcheck
            else:
                postvars = d2_activity.query.filter_by(id=editcheck.replyto).first()
            channelcheck = d2_channels.query.filter_by(id=postvars.category).first()
            if not check_channel_auth(channelcheck): return "Insufficient permission"
            editor = d2_user.query.filter_by(user_id=userid).first()
            if (editor.rank >= 100) or (int(editcheck.user_id) == int(userid)):
                if editcheck:
                    editcheck.content = tpost
                    syndbb.db.session.commit()

                    syndbb.cache.delete_memoized(syndbb.models.channels.get_thread_contents)

                    return "/"+channelcheck.short_name+"/"+str(postvars.id)+"#"+editing
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
        userid = check_session_by_id(str(uniqid))
        if userid:
            postcheck = d2_activity.query.filter_by(id=post_id).first()
            if postcheck:
                if postcheck.title:
                    postvars = postcheck
                else:
                    postvars = d2_activity.query.filter_by(id=postcheck.replyto).first()
                channelcheck = d2_channels.query.filter_by(id=postvars.category).first()
                if not check_channel_auth(channelcheck): return "Insufficient permission"
                user = d2_user.query.filter_by(user_id=userid).first()
                if (user.rank >= 100) or (int(postcheck.user_id) == int(userid)):
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

                        syndbb.cache.delete_memoized(syndbb.models.channels.get_thread_contents)
                        syndbb.cache.delete_memoized(syndbb.models.channels.get_thread_list)
                        syndbb.cache.delete_memoized(syndbb.models.activity.get_recent_posts)
                        syndbb.cache.delete_memoized(syndbb.models.activity.get_activity)
                        syndbb.cache.delete_memoized(syndbb.views.xml_feed.feed_threads_xml)
                        syndbb.cache.delete_memoized(syndbb.models.channels.replies_to_post)
                        syndbb.cache.delete_memoized(syndbb.models.channels.get_channel_list)

                        return syndbb.redirect("/"+channelcheck.short_name)
                    else:
                        postvars.reply_count -= 1
                        syndbb.db.session.commit()

                        syndbb.db.session.delete(postcheck)
                        syndbb.db.session.commit()
                        take_currency(postcheck.user_id, 2)
                        take_posts(userid, 1)
                        syndbb.flash('Post has been deleted.', 'danger')

                        syndbb.cache.delete_memoized(syndbb.models.channels.get_thread_contents)
                        syndbb.cache.delete_memoized(syndbb.models.activity.get_recent_posts)
                        syndbb.cache.delete_memoized(syndbb.models.activity.get_activity)
                        syndbb.cache.delete_memoized(syndbb.views.xml_feed.feed_posts_xml)
                        syndbb.cache.delete_memoized(syndbb.models.channels.replies_to_post)
                        syndbb.cache.delete_memoized(syndbb.models.channels.get_channel_list)

                        return syndbb.redirect("/"+channelcheck.short_name+"/"+str(postvars.id))
                else:
                    return "Trying to delete a post which isn't yours."

            else:
                return "Trying to delete a post which doesnt exist."

### Community Channels ###
@syndbb.app.route("/request-channel/")
def request_channel():
    if 'logged_in' in syndbb.session:
        return syndbb.render_template('request_channel.html', title="New Channel", subheading=[""])
    else:
        return syndbb.render_template('error_not_logged_in.html', title="New Channel", subheading=[""])

@syndbb.app.route("/functions/custom_channel/", methods=['GET', 'POST'])
def request_custom_channel():
    uniqid = syndbb.request.form['uniqid']
    fname = syndbb.request.form['channel-name']
    fdesc = syndbb.request.form['channel-description']
    furl = syndbb.request.form['channel-chat-url']
    facrn = syndbb.request.form['channel-acronym']
    fauth = syndbb.request.form['channel-access-rank']
    fusers = syndbb.request.form['channel-access-user']
    fmods = syndbb.request.form['channel-access-moderator']
    #ftype = syndbb.request.form['channel-type']
    ftype = 0
    if 'nsfw_toggle' in syndbb.request.form:
        fnsfw = 1
    else:
        fnsfw = 0
    if 'anon_toggle' in syndbb.request.form:
        fanon = 1
    else:
        fanon = 0
    if uniqid and fname:
        userid = check_session_by_id(uniqid)
        if userid:
            if not syndbb.re.match('^[\w-]+$', facrn):
                syndbb.flash('Short name contains non-alphanumeric characters.', 'danger')
                return syndbb.redirect(syndbb.url_for('request_channel'))
            if len(fname) < 4:
                syndbb.flash('Channel name is under 3 characters.', 'danger')
                return syndbb.redirect(syndbb.url_for('request_channel'))
            elif len(fname) > 25:
                syndbb.flash('Channel name is over 25 characters.', 'danger')
                return syndbb.redirect(syndbb.url_for('request_channel'))

            if len(facrn) < 1:
                syndbb.flash('Short name is under 1 character.', 'danger')
                return syndbb.redirect(syndbb.url_for('request_channel'))
            elif len(facrn) > 10:
                syndbb.flash('Short name is over 10 characters.', 'danger')
                return syndbb.redirect(syndbb.url_for('request_channel'))

            invalid_shortcodes = all_pages()
            if facrn in invalid_shortcodes:
                syndbb.flash('Attempting to use a restricted short name.', 'danger')
                return syndbb.redirect(syndbb.url_for('request_channel'))
            channelcheck = d2_channels.query.filter_by(name=fname).first()
            if channelcheck:
                syndbb.flash('A channel with that name already exists.', 'danger')
                return syndbb.redirect(syndbb.url_for('request_channel'))
            else:
                acronymcheck = d2_channels.query.filter_by(short_name=facrn).first()
                if acronymcheck:
                    syndbb.flash('A channel with this short name already exists.', 'danger')
                    return syndbb.redirect(syndbb.url_for('request_channel'))
                else:
                    requestcheck = d2_channels.query.filter_by(approved='0', owned_by=userid).first()
                    if requestcheck:
                        syndbb.flash('You\'ve already requested a channel, wait for it to be approved.', 'danger')
                        return syndbb.redirect(syndbb.url_for('request_channel'))
                    else:
                        new_channel = d2_channels(fname, facrn, fdesc, furl, fnsfw, userid, 0, fauth, fanon, fusers, fmods, ftype)
                        syndbb.db.session.add(new_channel)
                        syndbb.db.session.commit()
                        syndbb.flash('Your request has been submitted.', 'success')
                        return syndbb.redirect(syndbb.url_for('request_channel'))
        else:
            syndbb.flash('Invalid session.', 'danger')
            return syndbb.redirect(syndbb.url_for('request_channel'))
    else:
        syndbb.flash('Invalid request.', 'danger')
        return syndbb.redirect(syndbb.url_for('request_channel'))
