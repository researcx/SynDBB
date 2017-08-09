#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb, shutil, base64, requests
from syndbb.models.users import d2_user, d2_ip, checkSession
from syndbb.models.time import unix_time_current

@syndbb.app.route("/user/<username>")
def profile(username):
    isInline = syndbb.request.args.get('inlinecontent', '')
    user = d2_user.query.filter_by(username=username).first()
    if user:
        dynamic_js_footer = ["js/bootbox.min.js", "js/delete.js", "js/profileAvatar.js"]
        return syndbb.render_template('profile.html', isInline=isInline, dynamic_js_footer=dynamic_js_footer, profile=user, title="User Profile: "+user.username)
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
            return syndbb.render_template('preferences.html', uploadurls=uploadurls, title="Preferences")
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
            return syndbb.render_template('login_info.html', logins=logins, title="Login History")
        else:
            return syndbb.render_template('error_not_logged_in.html', title="Login History")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Login History")

@syndbb.app.route("/account/password")
def change_password():
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(syndbb.session['logged_in']))
        if userid:
            dynamic_js_footer = ["js/crypt.js", "js/auth/auth_chpw.js", "js/bootbox.min.js"]
            return syndbb.render_template('change_password.html', dynamic_js_footer=dynamic_js_footer, title="Change Password")
        else:
            return syndbb.render_template('error_not_logged_in.html', title="Change Password")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Change Password")

@syndbb.app.route("/functions/save_preferences", methods=['GET', 'POST'])
def save_preferences():
    possibleurls = ["local", "i.d2k5.com", "i.hardcats.net", "i.lulzsec.co.uk"]

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
            user.location = location
            user.gender = gender
            user.occupation = occupation
            user.site = url
            user.ircauth = ircauth
            user.uploadauth = uploadauth
            if upload_url in possibleurls:
                user.upload_url = upload_url
            else:
                user.upload_url = "i.d2k5.com"
            user.bio = bio
            syndbb.db.session.commit()

            syndbb.flash('Preferences updated successfully.', 'success')

            try:
                requests.get("https://" + syndbb.znc_address + ":" + syndbb.znc_port + "/mods/global/httpadmin/adduser?username=" + user.username + "&password=" + ircauth, auth=(syndbb.znc_user, syndbb.znc_password), verify=False)
            except requests.exceptions.RequestException:
                syndbb.flash('Couldn\'t create an IRC user.', 'danger')

            try:
                requests.get("https://" + syndbb.znc_address + ":" + syndbb.znc_port + "/mods/global/httpadmin/userpassword?username=" + user.username + "&password=" + ircauth, auth=(syndbb.znc_user, syndbb.znc_password), verify=False)
            except requests.exceptions.RequestException:
                syndbb.flash('Couldn\'t change IRC password.', 'danger')

            try:
                requests.get("https://" + syndbb.znc_address + ":" + syndbb.znc_port + "/mods/global/httpadmin/addnetwork?username=" + user.username + "&net_name=" + syndbb.irc_network_name + "&net_addr=" + syndbb.irc_network_address + "&net_port=" + syndbb.irc_network_port, auth=(syndbb.znc_user, syndbb.znc_password), verify=False)
            except requests.exceptions.RequestException:
                syndbb.flash('Couldn\'t assign an IRC network.', 'danger')

            return syndbb.redirect(syndbb.url_for('preferences'))
        else:
            return "Invalid Session"
    else:
        return "Invalid Request"


@syndbb.app.route("/account/avatar")
def change_avatar():
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(syndbb.session['logged_in']))
        if userid:
            dynamic_js_footer = ["js/jquery.cropit.js", "js/avatar.js", "js/bootbox.min.js", "js/delete.js"]
            avatar_list = []
            avatarfolder = syndbb.os.getcwd() + "/syndbb/static/data/avatars/"+str(userid)+"/"

            if not syndbb.os.path.exists(avatarfolder):
                print("path does not exist, creating")
                syndbb.os.makedirs(avatarfolder)
            else:
                print(avatarfolder + " exists")

            for avatar in syndbb.os.listdir(avatarfolder):
                filepath = avatarfolder + "/" + avatar
                if syndbb.os.path.isfile(filepath):
                    addtime = int(syndbb.os.stat(filepath).st_mtime)
                    avatar_list.append([avatar, addtime])
            avatar_list.sort(reverse=True)

            return syndbb.render_template('change_avatar.html', avatar_list=avatar_list, dynamic_js_footer=dynamic_js_footer, title="Change Avatar")
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
            avatar_folder = syndbb.os.getcwd() + "/syndbb/static/data/avatars/"+str(userid)+".png"
            avatar_history = syndbb.os.getcwd() + "/syndbb/static/data/avatars/"+str(userid)+"/"+str(unix_time_current())+".png"

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

            avatar_source = syndbb.os.getcwd() + "/syndbb/static/data/avatars/"+str(userid)+"/"+avatar
            avatar_destination = syndbb.os.getcwd() + "/syndbb/static/data/avatars/"+str(userid)+".png"
            if syndbb.os.path.isfile(avatar_source):
                shutil.copy2(avatar_source, avatar_destination)

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
                avatar_source = syndbb.os.getcwd() + "/syndbb/static/data/avatars/"+str(userid)+"/"+avatar
                if syndbb.os.path.isfile(avatar_source):
                    syndbb.os.remove(avatar_source)
                    syndbb.flash('Avatar removed.', 'success')
                    return syndbb.redirect(syndbb.url_for('change_avatar'))
                else:
                    syndbb.flash('No such avatar exists.', 'danger')
                    return syndbb.redirect(syndbb.url_for('change_avatar'))
            else:
                avatar_source = syndbb.os.getcwd() + "/syndbb/static/data/avatars/"+str(userid)+".png"
                syndbb.os.remove(avatar_source)
                user = d2_user.query.filter_by(user_id=userid).first()
                user.avatar_date = 0
                syndbb.db.session.commit()
                syndbb.flash('Avatar removed.', 'success')
                return syndbb.redirect(syndbb.url_for('change_avatar'))
        else:
            return "Invalid Session"
    else:
        return "Invalid Request"
