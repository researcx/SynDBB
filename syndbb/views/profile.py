#
# Copyright (c) 2017 - 2020 Keira T (https://kei.info.gf). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb, shutil, base64, requests, hashlib, hmac, json
from flask import send_from_directory
from syndbb.models.users import d2_user, ldap_user, d2_ip, check_session_by_id, get_avatar_source_by_id, get_title_by_id, get_flair_by_id
from syndbb.models.channels import d2_channels
from syndbb.models.time import unix_time_current, cdn_path
from syndbb.views.pastebin import html_escape
from werkzeug.utils import secure_filename
from PIL import Image

@syndbb.cache.memoize(timeout=60) # get_user_profile
def get_user_profile(username):
    user = d2_user.query.filter_by(username=username).first()
    return user

def render_tag_list(tags, type):
    if tags:
        tags = tags.split(" ")
        tag_list = ""
        bio_tag_list = ""
        for tag in tags:
            try:
                key, value = tag.split(":")
            except ValueError:
                tag_list += '<span class="tag-type-general"><a href="#/search/?t='+html_escape(tag)+'">'+html_escape(tag.replace("_", " "))+'</a></span>'
            else:
                bio_tag_list += "<dt>" + html_escape(key.replace("_", " ")) + ": </dt><dd><a href=\"#/search/?t="+html_escape(tag)+"\">" + html_escape(value.replace("_", " ")) + "</a></dd>"
        if type == "bio":
            return bio_tag_list
        else:
            return tag_list
    else:
        return False

@syndbb.app.route("/user/<username>")
def profile(username):
    isInline = syndbb.request.args.get('inlinecontent', '')
    user = get_user_profile(username)
    if user:
        username_display = user.display_name + " (" + user.username + ")" if user.display_name else user.username
        subheading = []
        subheading.append("User Profile")
			
        meta_image = get_avatar_source_by_id(user.user_id) if get_avatar_source_by_id(user.user_id) else ""
        meta_description = user.status if user.status else get_title_by_id(user.user_id) + "\n" + user.title
        dynamic_css_header = []
        dynamic_js_footer = ["js/bootbox.min.js", "js/delete.js", "js/profileAvatar.js"]

        if (user.nsfw_toggle) and ('nsfwAllow' not in syndbb.request.cookies):
            dynamic_js_footer.append("js/nsfwprompt.js")
            dynamic_css_header.append("css/nsfw_fill.css")

        tag_list = render_tag_list(user.tags, "profile")
        tag_list_bio = render_tag_list(user.tags, "bio")

        return syndbb.render_template('profile.html', isInline=isInline, dynamic_js_footer=dynamic_js_footer, dynamic_css_header=dynamic_css_header, profile=user, title=username_display, subheading=subheading, tag_list=tag_list, tag_list_bio=tag_list_bio, meta_image=meta_image, meta_description=meta_description)
    else:
        return syndbb.render_template('invalid.html', isInline=isInline, title="Invalid User")

@syndbb.app.route("/account/preferences")
def preferences():
    if 'logged_in' in syndbb.session:
        userid = check_session_by_id(str(syndbb.session['logged_in']))
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            possibleurls = ["local", "i.d2k5.com"]
            uploadurls = []
            for uploadurl in possibleurls:
                if user.upload_url == uploadurl:
                    uploadurls.append([uploadurl, " selected"])
                else:
                    uploadurls.append([uploadurl, " "])
            subheading = []
            subheading.append("<a href='/user/" + user.username + "'>" + user.username + "</a>")
            dynamic_js_footer = ["js/random_name.js"]
            return syndbb.render_template('preferences.html', dynamic_js_footer=dynamic_js_footer, uploadurls=uploadurls, title="Preferences", subheading=subheading)
        else:
            return syndbb.render_template('error_not_logged_in.html', title="Preferences")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Preferences")

@syndbb.app.route("/account/login_history")
def login_history():
    if 'logged_in' in syndbb.session:
        userid = check_session_by_id(str(syndbb.session['logged_in']))
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            logins = d2_ip.query.filter_by(user_id=userid).order_by(d2_ip.time.desc()).all()
            subheading = []
            subheading.append("<a href='/user/" + user.username + "'>" + user.username + "</a>")
            return syndbb.render_template('login_info.html', logins=logins, title="Login History", subheading=subheading)
        else:
            return syndbb.render_template('error_not_logged_in.html', title="Login History")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Login History")


@syndbb.app.route("/account/profiles")
def profiles():
    linked_users = []
    if 'logged_in' in syndbb.session:
        userid = check_session_by_id(str(syndbb.session['logged_in']))
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            if user:
                if user.user_auth and user.user_auth != "":
                    linked_users = d2_user.query.filter_by(user_auth=user.user_auth).all()
            subheading = []
            subheading.append("<a href='/user/" + user.username + "'>" + user.username + "</a>")
            return syndbb.render_template('profiles.html', linked_users=linked_users, title="My Profiles", subheading=subheading)
        else:
            return syndbb.render_template('error_not_logged_in.html', title="My Profiles")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="My Profiles")

@syndbb.app.route("/account/password")
def change_password():
    if 'logged_in' in syndbb.session:
        userid = check_session_by_id(str(syndbb.session['logged_in']))
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            dynamic_js_footer = ["js/crypt.js", "js/bootbox.min.js"]
            if syndbb.core_config['ldap']['enabled'] :
                dynamic_js_footer.append("js/auth_plain/auth_chpw.js")
            else:
                dynamic_js_footer.append("js/auth_hash/auth_chpw.js")
            subheading = []
            subheading.append("<a href='/user/" + user.username + "'>" + user.username + "</a>")
            return syndbb.render_template('change_password.html', dynamic_js_footer=dynamic_js_footer, title="Change Password", subheading=subheading)
        else:
            return syndbb.render_template('error_not_logged_in.html', title="Change Password")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Change Password")

@syndbb.app.route("/functions/save_preferences", methods=['GET', 'POST'])
def save_preferences():
    possibleurls = ["local", "i.d2k5.com", "i.hardcats.net", "i.hard.cat", "i.lulzsec.co.uk", "i.hurr.ca"]

    display_name = syndbb.request.form['display_name']
    status = syndbb.request.form['status']
    irc_auth = 0 #syndbb.request.form['irc_auth']
    upload_auth = syndbb.request.form['upload_auth']
    user_auth = syndbb.request.form['user_auth']
    upload_url = syndbb.request.form['upload_url']
    bio = syndbb.request.form['bio']
    tags = syndbb.request.form['tags']
    uniqid = syndbb.request.form['uniqid']

    nsfw = 1 if 'nsfw_toggle' in syndbb.request.form else 0
    full_avatar = 1 if 'full_avatar' in syndbb.request.form else 0

    if uniqid:
        userid = check_session_by_id(uniqid)
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            user.display_name = display_name
            if syndbb.core_config['ldap']['enabled'] :
                is_ldap_user = ldap_user.query.filter(syndbb.core_config['ldap']['attribute_cn'] + ': '+user.username).first()
                if is_ldap_user:
                    is_ldap_user.display_name = display_name
                    is_ldap_user.save()
            if status != user.status:
                user.status = status
                user.status_time = unix_time_current()
            user.irc_auth = irc_auth
            user.upload_auth = upload_auth
            user.user_auth = user_auth

            user.nsfw_toggle = nsfw
            user.full_avatar = full_avatar
            user.tags = tags
            if upload_url in possibleurls:
                user.upload_url = upload_url
            else:
                user.upload_url = "i.d2k5.com"
            user.bio = bio
            syndbb.db.session.commit()

            syndbb.cache.delete_memoized(syndbb.views.profile.get_user_profile)
            syndbb.cache.delete_memoized(syndbb.models.users.get_linked_by_id)
            syndbb.cache.delete_memoized(syndbb.models.users.get_all_status_updates)
            syndbb.cache.delete_memoized(syndbb.models.users.get_displayed_name_by_id)
            syndbb.cache.delete_memoized(syndbb.models.users.get_displayed_name_by_username)
            syndbb.flash('Preferences updated successfully.', 'success')

            #if irc_auth is not user.irc_auth:
#                try:
#                    udata = {'username': user.username, 'password': irc_auth}
#                    reqheader = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': syndbb.xmpp_key}
#                    req = requests.get("https://" + syndbb.xmpp_address + ":" + syndbb.xmpp_port + "/plugins/restapi/v1/users", data=json.dumps(udata), headers=reqheader, verify=False, timeout=5)
#                    syndbb.logger.debug(req.request.headers)
#                except requests.exceptions.RequestException:
#                    syndbb.flash('Couldn\'t create an XMPP user.', 'danger')
                
                # try:
                #     requests.get("https://" + syndbb.core_config['znc']['host']  + ":" + syndbb.core_config['znc']['port']  + "/mods/global/httpadmin/adduser?username=" + user.username + "&password=" + irc_auth, auth=(syndbb.core_config['znc']['user'] , syndbb.core_config['znc']['password'] ), verify=False, timeout=5)
                # except requests.exceptions.RequestException:
                #     syndbb.flash('Couldn\'t create an IRC user.', 'danger')

                # try:
                #     requests.get("https://" + syndbb.core_config['znc']['host']  + ":" + syndbb.core_config['znc']['port']  + "/mods/global/httpadmin/userpassword?username=" + user.username + "&password=" + irc_auth, auth=(syndbb.core_config['znc']['user'] , syndbb.core_config['znc']['password'] ), verify=False, timeout=5)
                # except requests.exceptions.RequestException:
                #     syndbb.flash('Couldn\'t change IRC password.', 'danger')

                # try:
                #     requests.get("https://" + syndbb.core_config['znc']['host']  + ":" + syndbb.core_config['znc']['port']  + "/mods/global/httpadmin/addnetwork?username=" + user.username + "&net_name=" + syndbb.core_config['irc']['network']  + "&net_addr=" + syndbb.core_config['irc']['host']  + "&net_port=" + syndbb.core_config['irc']['port'] , auth=(syndbb.core_config['znc']['user'] , syndbb.core_config['znc']['password'] ), verify=False, timeout=5)
                # except requests.exceptions.RequestException:
                #     syndbb.flash('Couldn\'t assign an IRC network.', 'danger')

            return syndbb.redirect(syndbb.url_for('preferences'))
        else:
            return "Invalid Session"
    else:
        return "Invalid Request"

@syndbb.app.route("/functions/update_status", methods=['GET', 'POST'])
def update_status():
    status = syndbb.request.form['status']
    uniqid = syndbb.request.form['uniqid']

    if uniqid:
        userid = check_session_by_id(uniqid)
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            user.status = status
            user.status_time = unix_time_current()
            syndbb.db.session.commit()
            syndbb.cache.delete_memoized(syndbb.views.profile.get_user_profile)
            syndbb.cache.delete_memoized(syndbb.models.users.get_all_status_updates)
            return syndbb.redirect(syndbb.url_for('home'))
        else:
            return "Invalid Session"
    else:
        return "Invalid Request"
    
@syndbb.app.route("/account/viewAvatar/")
def no_avatar():
    davatar = cdn_path() + '/images/default_avatar.png'
    return syndbb.redirect(davatar)

@syndbb.app.route("/account/viewAvatar/<username>")
def view_avatar(username):
    davatar = cdn_path() + '/images/default_avatar.png'
    if username:
        user = d2_user.query.filter_by(username=username).first()
        if user:
            dynamic_js_footer = ["js/jquery.cropit.js", "js/bootbox.min.js", "js/delete.js"]
            avatar_path = syndbb.app.static_folder + "/data/avatars/"+str(user.user_id)+".png"
            uavatar = cdn_path() + "/data/avatars/"+str(user.user_id)+".png?v="+str(user.avatar_date)
            if syndbb.os.path.isfile(avatar_path):
                return syndbb.redirect(uavatar)
            else:
                return syndbb.redirect(davatar)
        else:
            return syndbb.redirect(davatar)
        

@syndbb.app.route("/account/viewAvatar/<username>/source")
def view_avatar_source(username):
    davatar = cdn_path() + '/images/default_avatar.png'
    if username:
        user = d2_user.query.filter_by(username=username).first()
        if user:
            dynamic_js_footer = ["js/jquery.cropit.js", "js/bootbox.min.js", "js/delete.js"]
            avatar_path = syndbb.app.static_folder + "/data/avatars/"+str(user.user_id)+"-src.png"
            uavatar = cdn_path() + "/data/avatars/"+str(user.user_id)+"-src.png?v="+str(user.avatar_date)
            if syndbb.os.path.isfile(avatar_path):
                return syndbb.redirect(uavatar)
            else:
                return syndbb.redirect(davatar)
        else:
            return syndbb.redirect(davatar)


@syndbb.app.route("/account/avatar")
def configure_avatar():
    if 'logged_in' in syndbb.session:
        userid = check_session_by_id(str(syndbb.session['logged_in']))
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            dynamic_js_footer = ["js/jquery.cropit.js", "js/bootbox.min.js", "js/delete.js"]
            avatar_list = []
            avatar_sources = []
            avatarfolder = syndbb.app.static_folder + "/data/avatars/"+str(userid)+"/"

            if not syndbb.os.path.exists(avatarfolder):
                syndbb.logger.info("path does not exist, creating")
                syndbb.os.makedirs(avatarfolder)
            else:
                syndbb.logger.info(avatarfolder + " exists")

            for avatar in syndbb.os.listdir(avatarfolder):
                filepath = avatarfolder + "/" + avatar
                if syndbb.os.path.isfile(filepath):
                    addtime = int(syndbb.os.stat(filepath).st_mtime)
                    if "src" not in avatar:
                        avatar_list.append([avatar.split(".")[0], addtime])
                    else:
                        avatar_sources.append([avatar.split(".")[0], addtime])
            avatar_list.sort(reverse=True)
            avatar_sources.sort(reverse=True)


            subheading = []
            subheading.append("<a href='/user/" + user.username + "'>" + user.username + "</a>")

            return syndbb.render_template('configure_avatar.html', avatar_list=avatar_list, avatar_sources=avatar_sources, dynamic_js_footer=dynamic_js_footer, title="Change Avatar", subheading=subheading)
        else:
            return syndbb.render_template('error_not_logged_in.html', title="Change Avatar")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Change Avatar")

@syndbb.app.route("/account/flair")
def configure_flair():
    if 'logged_in' in syndbb.session:
        userid = check_session_by_id(str(syndbb.session['logged_in']))
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            dynamic_js_footer = ["js/jquery.cropit.js", "js/bootbox.min.js", "js/delete.js"]

            flair_list = get_flair_by_id(user.user_id)

            subheading = []
            subheading.append("<a href='/user/" + user.username + "'>" + user.username + "</a>")

            return syndbb.render_template('configure_flair.html', flair_list=flair_list, dynamic_js_footer=dynamic_js_footer, title="Change Flair", subheading=subheading)
        else:
            return syndbb.render_template('error_not_logged_in.html', title="Change Flair")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Change Flair")

@syndbb.app.route('/functions/upload_avatar', methods=['GET', 'POST'])
def upload_avatar():
    if syndbb.request.method == 'POST':
        uploaded_avatar = syndbb.request.form['avatar']
        uploaded_avatar = uploaded_avatar[uploaded_avatar.find(",")+1:]
        userid = check_session_by_id(str(syndbb.session['logged_in']))
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            avatar_original_folder = syndbb.app.static_folder + "/data/avatars/"+str(userid)+"-src.png"
            avatar_original_history = syndbb.app.static_folder + "/data/avatars/"+str(userid)+"/"+str(unix_time_current())+"-src.png"

            avatar_folder = syndbb.app.static_folder + "/data/avatars/"+str(userid)+".png"
            avatar_history = syndbb.app.static_folder + "/data/avatars/"+str(userid)+"/"+str(unix_time_current())+".png"

            if 'avatar_source' not in syndbb.request.files:
                return "No avatar selected."
            avatar_source = syndbb.request.files['avatar_source']
            if avatar_source.filename == '':
                return "No avatar selected."
            if avatar_source:
                filename = secure_filename(avatar_source.filename)
                avatar_source.save(avatar_original_folder)

                try:
                    im = Image.open(avatar_original_folder)
                    im.thumbnail((1024,1024))
                    im.save(avatar_original_folder, "PNG")

                    shutil.copy2(avatar_original_folder, avatar_original_history)
                except IOError:
                    syndbb.flash('Problem setting avatar.', 'danger')
                    return syndbb.redirect(syndbb.url_for('configure_avatar'))

            if 'avatar' not in syndbb.request.form:
                syndbb.flash('No avatar selected.', 'danger')
                return syndbb.redirect(syndbb.url_for('configure_avatar'))
            else:
                try:
                    with open(avatar_folder, "wb") as fh:
                        fh.write(base64.b64decode(uploaded_avatar))

                    im = Image.open(avatar_folder)
                    im.thumbnail((256,256))
                    im.save(avatar_folder, "PNG")

                    shutil.copy2(avatar_folder, avatar_history)

                    user.avatar_date = unix_time_current()
                    syndbb.db.session.commit()
                    syndbb.flash('Avatar uploaded successfully.', 'success')
                except IOError:
                    syndbb.flash('Problem setting flair.', 'danger')
                    return syndbb.redirect(syndbb.url_for('configure_flair'))
                
                syndbb.cache.delete_memoized(syndbb.models.users.get_avatar_by_id)
                syndbb.cache.delete_memoized(syndbb.models.users.get_avatar_source_by_id)

                return syndbb.redirect(syndbb.url_for('configure_avatar'))


@syndbb.app.route('/functions/upload_flair', methods=['GET', 'POST'])
def upload_flair():
    if syndbb.request.method == 'POST':
        uploaded_flair = syndbb.request.form['flair']
        uploaded_flair = uploaded_flair[uploaded_flair.find(",")+1:]
        userid = check_session_by_id(str(syndbb.session['logged_in']))
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            if 'flair' not in syndbb.request.form:
                syndbb.flash('No flair selected.', 'danger')
                return syndbb.redirect(syndbb.url_for('configure_flair'))
            else:
                try:
                    if 'flair_source' not in syndbb.request.files:
                        return "No flair selected."
                    flair_source = syndbb.request.files['flair_source']
                    if not flair_source or flair_source.filename == '':
                        return "No flair selected."

                    flair_folder = syndbb.app.static_folder + "/data/flair/"+str(userid)+".png"
                    flair_history = syndbb.app.static_folder + "/data/flair/"+str(userid)+"/"+syndbb.os.path.splitext(secure_filename(flair_source.filename))[0]+".png"

                    with open(flair_folder, "wb") as fh:
                        fh.write(base64.b64decode(uploaded_flair))

                    im = Image.open(flair_folder)
                    im.thumbnail((16,16))
                    im.save(flair_folder, "PNG")

                    shutil.copy2(flair_folder, flair_history)
                except IOError:
                    syndbb.flash('Problem setting flair.', 'danger')
                    return syndbb.redirect(syndbb.url_for('configure_flair'))

            syndbb.flash('Flair uploaded successfully.', 'success')

            syndbb.cache.delete_memoized(syndbb.models.users.get_flair_by_id)

            return syndbb.redirect(syndbb.url_for('configure_flair'))

@syndbb.app.route("/functions/change_user/")
def change_user():
    switch_to = syndbb.request.args.get('userid', '')
    uniqid = syndbb.request.args.get('uniqid', '')

    if uniqid:
        userid = check_session_by_id(uniqid)
        if userid:
            session = d2_ip.query.filter_by(sessionid=uniqid).first()
            session.user_id = switch_to
            syndbb.db.session.commit()
            return syndbb.redirect(syndbb.url_for('home'))
        else:
            return "Invalid Session"
    else:
        return "Invalid Request"

@syndbb.app.route("/functions/remove_flair/")
def remove_flair():
    flair = syndbb.request.args.get('file', '')
    uniqid = syndbb.request.args.get('uniqid', '')

    if uniqid:
        userid = check_session_by_id(uniqid)
        if userid:
            if flair:
                flair_source = syndbb.app.static_folder + "/data/flair/"+str(userid)+"/"+flair+".png"
                if syndbb.os.path.isfile(flair_source):
                    syndbb.os.remove(flair_source)
                    syndbb.flash('Flair removed.', 'success')
                    syndbb.cache.delete_memoized(syndbb.models.users.get_flair_by_id)
                    return syndbb.redirect(syndbb.url_for('configure_flair'))
                else:
                    syndbb.flash('No such flair exists.', 'danger')
                    return syndbb.redirect(syndbb.url_for('configure_flair'))
            else:
                flair_source = syndbb.app.static_folder + "/data/flair/"+str(userid)+".png"
                syndbb.os.remove(flair_source)
                syndbb.flash('Flair removed.', 'success')
                syndbb.cache.delete_memoized(syndbb.models.users.get_flair_by_id)
                return syndbb.redirect(syndbb.url_for('configure_flair'))
        else:
            return "Invalid Session"
    else:
        return "Invalid Request"


@syndbb.app.route("/functions/set_avatar/")
def set_avatar():
    avatar = syndbb.request.args.get('file', '')
    uniqid = syndbb.request.args.get('uniqid', '')

    if uniqid:
        userid = check_session_by_id(uniqid)
        if userid:

            avatar_original_source = syndbb.app.static_folder + "/data/avatars/"+str(userid)+"/"+avatar+"-src.png"
            avatar_original_destination = syndbb.app.static_folder + "/data/avatars/"+str(userid)+"-src.png"

            avatar_source = syndbb.app.static_folder + "/data/avatars/"+str(userid)+"/"+avatar+".png"
            avatar_destination = syndbb.app.static_folder + "/data/avatars/"+str(userid)+".png"
            if syndbb.os.path.isfile(avatar_source):
                shutil.copy2(avatar_source, avatar_destination)
                if syndbb.os.path.isfile(avatar_original_source):
                    shutil.copy2(avatar_original_source, avatar_original_destination)
                else:
                    if syndbb.os.path.isfile(avatar_original_destination):
                        syndbb.os.remove(avatar_original_destination)

                user = d2_user.query.filter_by(user_id=userid).first()
                user.avatar_date = unix_time_current()
                syndbb.db.session.commit()

                syndbb.flash('Avatar updated successfully.', 'success')
                syndbb.cache.delete_memoized(syndbb.models.users.get_avatar_by_id)
                syndbb.cache.delete_memoized(syndbb.models.users.get_avatar_source_by_id)
                return syndbb.redirect(syndbb.url_for('configure_avatar'))
            else:
                syndbb.flash('No such avatar exists.', 'danger')
                return syndbb.redirect(syndbb.url_for('configure_avatar'))
        else:
            return "Invalid Session"
    else:
        return "Invalid Request"

@syndbb.app.route("/functions/remove_avatar/")
def remove_avatar():
    avatar = syndbb.request.args.get('file', '')
    uniqid = syndbb.request.args.get('uniqid', '')

    if uniqid:
        userid = check_session_by_id(uniqid)
        if userid:
            if avatar:
                avatar_original_source = syndbb.app.static_folder + "/data/avatars/"+str(userid)+"/"+avatar+"-src.png"
                avatar_source = syndbb.app.static_folder + "/data/avatars/"+str(userid)+"/"+avatar+".png"
                if syndbb.os.path.isfile(avatar_source):
                    syndbb.os.remove(avatar_source)
                    if syndbb.os.path.isfile(avatar_original_source):
                        syndbb.os.remove(avatar_original_source)
                    syndbb.cache.delete_memoized(syndbb.models.users.get_avatar_by_id)
                    syndbb.cache.delete_memoized(syndbb.models.users.get_avatar_source_by_id)
                    syndbb.flash('Avatar removed.', 'success')
                    return syndbb.redirect(syndbb.url_for('configure_avatar'))
                else:
                    syndbb.flash('No such avatar exists.', 'danger')
                    return syndbb.redirect(syndbb.url_for('configure_avatar'))
            else:
                avatar_original_source = syndbb.app.static_folder + "/data/avatars/"+str(userid)+"-src.png"
                avatar_source = syndbb.app.static_folder + "/data/avatars/"+str(userid)+".png"
                syndbb.os.remove(avatar_source)
                if syndbb.os.path.isfile(avatar_original_source):
                    syndbb.os.remove(avatar_original_source)
                user = d2_user.query.filter_by(user_id=userid).first()
                user.avatar_date = 0
                syndbb.db.session.commit()
                syndbb.cache.delete_memoized(syndbb.models.users.get_avatar_by_id)
                syndbb.cache.delete_memoized(syndbb.models.users.get_avatar_source_by_id)
                syndbb.flash('Avatar removed.', 'success')
                return syndbb.redirect(syndbb.url_for('configure_avatar'))
        else:
            return "Invalid Session"
    else:
        return "Invalid Request"
