#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb, shutil, base64, requests, hashlib, hmac, json
from flask import send_from_directory
from syndbb.models.users import d2_user, d2_ip, checkSession
from syndbb.models.time import unix_time_current, cdn_path
from werkzeug.utils import secure_filename
from PIL import Image

@syndbb.cache.memoize(timeout=10)
def get_user_profile(username):
    user = d2_user.query.filter_by(username=username).first()
    return user

@syndbb.app.route("/user/<username>")
def profile(username):
    isInline = syndbb.request.args.get('inlinecontent', '')
    user = get_user_profile(username)
    if user:
        subheading = []
        subheading.append("User Profile")
        dynamic_js_footer = ["js/bootbox.min.js", "js/delete.js", "js/profileAvatar.js"]
        return syndbb.render_template('profile.html', isInline=isInline, dynamic_js_footer=dynamic_js_footer, profile=user, title=user.username, subheading=subheading)
    else:
        return syndbb.render_template('invalid.html', isInline=isInline, title="Invalid User")

@syndbb.app.route("/account/preferences")
def preferences():
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(syndbb.session['logged_in']))
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            possibleurls = ["local", "i.d2k5.com", "i.hardcats.net", "i.lulzsec.co.uk"]
            uploadurls = []
            for uploadurl in possibleurls:
                if user.upload_url == uploadurl:
                    uploadurls.append([uploadurl, " selected"])
                else:
                    uploadurls.append([uploadurl, " "])
            subheading = []
            subheading.append("<a href='/user/" + user.username + "'>" + user.username + "</a>")
            return syndbb.render_template('preferences.html', uploadurls=uploadurls, title="Preferences", subheading=subheading)
        else:
            return syndbb.render_template('error_not_logged_in.html', title="Preferences")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Preferences")

@syndbb.app.route("/account/login_history")
def login_history():
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(syndbb.session['logged_in']))
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

@syndbb.app.route("/account/password")
def change_password():
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(syndbb.session['logged_in']))
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            dynamic_js_footer = ["js/crypt.js", "js/auth/auth_chpw.js", "js/bootbox.min.js"]
            subheading = []
            subheading.append("<a href='/user/" + user.username + "'>" + user.username + "</a>")
            return syndbb.render_template('change_password.html', dynamic_js_footer=dynamic_js_footer, title="Change Password", subheading=subheading)
        else:
            return syndbb.render_template('error_not_logged_in.html', title="Change Password")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Change Password")

@syndbb.app.route("/functions/save_preferences", methods=['GET', 'POST'])
def save_preferences():
    possibleurls = ["local", "i.d2k5.com", "i.hardcats.net", "i.lulzsec.co.uk"]

    status = syndbb.request.form['status']
    location = syndbb.request.form['location']
    gender = syndbb.request.form['gender']
    occupation = syndbb.request.form['occupation']
    url = syndbb.request.form['url']
    ircauth = syndbb.request.form['ircauth']
    uploadauth = syndbb.request.form['uploadauth']
    upload_url = syndbb.request.form['upload_url']
    bio = syndbb.request.form['bio']
    uniqid = syndbb.request.form['uniqid']

    if uniqid:
        userid = checkSession(uniqid)
        if userid:

            user = d2_user.query.filter_by(user_id=userid).first()
            user.status = status
            user.status_time = unix_time_current()
            user.location = location
            user.gender = gender
            user.occupation = occupation
            user.site = url
            user.uploadauth = uploadauth
            if upload_url in possibleurls:
                user.upload_url = upload_url
            else:
                user.upload_url = "i.d2k5.com"
            user.bio = bio

            #Do the Matrix API stuff
            matrixuser = user.username
            matrixpass = ircauth
            authstring = matrixuser+"\x00"+matrixpass+"\x00notadmin"
            matrix_hmac = hmac.new(syndbb.matrix_api_reg_key.encode(), authstring.encode(), hashlib.sha1).hexdigest()

            #Matrix User Registration
            try:
                udata = {'user': matrixuser, 'password': matrixpass, 'type': 'org.matrix.login.shared_secret', 'mac': matrix_hmac}
                reg = requests.post(syndbb.matrix_api + "client/api/v1/register", data=json.dumps(udata), verify=False)
                matrix_response = json.loads(reg.text)

                #Remember access token and set display name
                if 'access_token' in matrix_response:
                    access_token = matrix_response['access_token']
                    user.token = access_token
                    udata = {'displayname': matrixuser}
                    reg = requests.put(syndbb.matrix_api + "client/r0/profile/%40"+matrixuser+"%3Aim.d2k5.com/displayname?access_token="+user.token, data=json.dumps(udata), verify=False)
                    syndbb.flash("Chat user created.", "success")
            except requests.exceptions.RequestException:
                syndbb.flash('Couldn\'t create a chat user.', 'danger')

            if user.token:
                udata = {'new_password': matrixpass, 'type': 'm.login.password', 'user': "%40"+matrixuser+"%3Aim.d2k5.com", 'password': user.ircauth}
                reg = requests.post(syndbb.matrix_api + "client/r0/account/password?access_token="+user.token, data=json.dumps(udata), verify=False)
                matrix_response = json.loads(reg.text)
                syndbb.flash(matrix_response)

            user.ircauth = ircauth
            syndbb.cache.delete_memoized(syndbb.models.users.get_all_status_updates)
            syndbb.flash('Preferences updated successfully.', 'success')
            syndbb.db.session.commit()

            # try:
            #     requests.get("https://" + syndbb.znc_address + ":" + syndbb.znc_port + "/mods/global/httpadmin/adduser?username=" + user.username + "&password=" + ircauth, auth=(syndbb.znc_user, syndbb.znc_password), verify=False)
            # except requests.exceptions.RequestException:
            #     syndbb.flash('Couldn\'t create an IRC user.', 'danger')
            #
            # try:
            #     requests.get("https://" + syndbb.znc_address + ":" + syndbb.znc_port + "/mods/global/httpadmin/userpassword?username=" + user.username + "&password=" + ircauth, auth=(syndbb.znc_user, syndbb.znc_password), verify=False)
            # except requests.exceptions.RequestException:
            #     syndbb.flash('Couldn\'t change IRC password.', 'danger')
            #
            # try:
            #     requests.get("https://" + syndbb.znc_address + ":" + syndbb.znc_port + "/mods/global/httpadmin/addnetwork?username=" + user.username + "&net_name=" + syndbb.irc_network_name + "&net_addr=" + syndbb.irc_network_address + "&net_port=" + syndbb.irc_network_port, auth=(syndbb.znc_user, syndbb.znc_password), verify=False)
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
        userid = checkSession(uniqid)
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            user.status = status
            user.status_time = unix_time_current()
            syndbb.db.session.commit()
            syndbb.cache.delete_memoized(syndbb.models.users.get_all_status_updates)
            return syndbb.redirect(syndbb.url_for('home'))
        else:
            return "Invalid Session"
    else:
        return "Invalid Request"

@syndbb.app.route("/account/viewAvatar/<userid>")
def view_avatar(userid):
    if userid:
        user = d2_user.query.filter_by(user_id=userid).first()
        if user:
            dynamic_js_footer = ["js/jquery.cropit.js", "js/bootbox.min.js", "js/delete.js"]
            avatar = cdn_path() + "/data/avatars/"+str(user.user_id)+".png?v="+str(user.avatar_date)
            return syndbb.redirect(avatar)


@syndbb.app.route("/account/avatar")
def change_avatar():
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(syndbb.session['logged_in']))
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            dynamic_js_footer = ["js/jquery.cropit.js", "js/bootbox.min.js", "js/delete.js"]
            avatar_list = []
            avatar_sources = []
            avatarfolder = syndbb.app.static_folder + "/data/avatars/"+str(userid)+"/"

            if not syndbb.os.path.exists(avatarfolder):
                print("path does not exist, creating")
                syndbb.os.makedirs(avatarfolder)
            else:
                print(avatarfolder + " exists")

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

            return syndbb.render_template('change_avatar.html', avatar_list=avatar_list, avatar_sources=avatar_sources, dynamic_js_footer=dynamic_js_footer, title="Change Avatar", subheading=subheading)
        else:
            return syndbb.render_template('error_not_logged_in.html', title="Change Avatar")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Change Avatar")


@syndbb.app.route('/functions/upload_avatar', methods=['GET', 'POST'])
def upload_avatar():
    if syndbb.request.method == 'POST':
        uploaded_avatar = syndbb.request.form['avatar']
        uploaded_avatar = uploaded_avatar[uploaded_avatar.find(",")+1:]
        userid = checkSession(str(syndbb.session['logged_in']))
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

                im = Image.open(avatar_original_folder)
                im.thumbnail((1024,1024))
                im.save(avatar_original_folder, "PNG")

                shutil.copy2(avatar_original_folder, avatar_original_history)

            if 'avatar' not in syndbb.request.form:
                syndbb.flash('No avatar selected.', 'danger')
                return syndbb.redirect(syndbb.url_for('change_avatar'))
            else:
                with open(avatar_folder, "wb") as fh:
                    fh.write(base64.b64decode(uploaded_avatar))
                with open(avatar_history, "wb") as fh:
                    fh.write(base64.b64decode(uploaded_avatar))
                user.avatar_date = unix_time_current()
                syndbb.db.session.commit()
                syndbb.flash('Avatar uploaded successfully.', 'success')
                return syndbb.redirect(syndbb.url_for('change_avatar'))


@syndbb.app.route("/functions/set_avatar/")
def set_avatar():
    avatar = syndbb.request.args.get('file', '')
    uniqid = syndbb.request.args.get('uniqid', '')

    if uniqid:
        userid = checkSession(uniqid)
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
                return syndbb.redirect(syndbb.url_for('change_avatar'))
            else:
                syndbb.flash('No such avatar exists.', 'danger')
                return syndbb.redirect(syndbb.url_for('change_avatar'))
        else:
            return "Invalid Session"
    else:
        return "Invalid Request"

@syndbb.app.route("/functions/remove_avatar/")
def remove_avatar():
    avatar = syndbb.request.args.get('file', '')
    uniqid = syndbb.request.args.get('uniqid', '')

    if uniqid:
        userid = checkSession(uniqid)
        if userid:
            if avatar:
                avatar_original_source = syndbb.app.static_folder + "/data/avatars/"+str(userid)+"/"+avatar+"-src.png"
                avatar_source = syndbb.app.static_folder + "/data/avatars/"+str(userid)+"/"+avatar+".png"
                if syndbb.os.path.isfile(avatar_source):
                    syndbb.os.remove(avatar_source)
                    if syndbb.os.path.isfile(avatar_original_source):
                        syndbb.os.remove(avatar_original_source)
                    syndbb.flash('Avatar removed.', 'success')
                    return syndbb.redirect(syndbb.url_for('change_avatar'))
                else:
                    syndbb.flash('No such avatar exists.', 'danger')
                    return syndbb.redirect(syndbb.url_for('change_avatar'))
            else:
                avatar_original_source = syndbb.app.static_folder + "/data/avatars/"+str(userid)+"-src.png"
                avatar_source = syndbb.app.static_folder + "/data/avatars/"+str(userid)+".png"
                syndbb.os.remove(avatar_source)
                if syndbb.os.path.isfile(avatar_original_source):
                    syndbb.os.remove(avatar_original_source)
                user = d2_user.query.filter_by(user_id=userid).first()
                user.avatar_date = 0
                syndbb.db.session.commit()
                syndbb.flash('Avatar removed.', 'success')
                return syndbb.redirect(syndbb.url_for('change_avatar'))
        else:
            return "Invalid Session"
    else:
        return "Invalid Request"
