#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb
from syndbb.models.users import d2_user, d2_session, d2_bans, d2_ip, checkSession
from syndbb.models.d2_hash import d2_hash
from syndbb.models.time import unix_time_current
from syndbb.models.invites import d2_invites

@syndbb.app.route("/login/")
def login():
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(syndbb.session['logged_in']))
        if userid:
            return syndbb.render_template('error_already_logged_in.html', title="Log In")

    dynamic_js_footer = ["js/crypt.js", "js/auth/auth_login.js", "js/bootbox.min.js"]
    return syndbb.render_template('login.html', dynamic_js_footer=dynamic_js_footer, title="Log In")

@syndbb.app.route("/register/")
def register():
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(syndbb.session['logged_in']))
        if userid:
            return syndbb.render_template('error_already_logged_in.html', title="Registration")

    dynamic_js_footer = ["js/crypt.js", "js/auth/auth_regd.js", "js/bootbox.min.js"]
    return syndbb.render_template('register_invite.html', invite="", dynamic_js_footer=dynamic_js_footer, title="Registration")

@syndbb.app.route("/register/<invite>")
def register_invite(invite):
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(syndbb.session['logged_in']))
        if userid:
            return syndbb.render_template('error_already_logged_in.html', title="Registration")

    if invite:
        invites = d2_invites.query.filter_by(code=invite, used_by=0).first()
        if not invites:
            syndbb.flash('The invite code provided is invalid.', 'danger')
        else:
            syndbb.flash('The invite code provided is valid.', 'success')

    dynamic_js_footer = ["js/crypt.js", "js/auth/auth_regd.js", "js/bootbox.min.js"]
    return syndbb.render_template('register.html', invite=invites, dynamic_js_footer=dynamic_js_footer, title="Registration")

@syndbb.app.route("/functions/register/", methods=['GET', 'POST'])
def doregister():
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(syndbb.session['logged_in']))
        if userid:
            return "You are already logged in!"

    username = syndbb.request.form['username']
    password = d2_hash(syndbb.request.form['password'])
    code = syndbb.request.form['code']

    if username and password and code:
        invites = d2_invites.query.filter_by(code=code, used_by=0).first()
        if not invites:
            return 'The invite code provided is invalid.'
        if not syndbb.re.search('^[a-z][a-z0-9-_]{2,32}$', username, syndbb.re.IGNORECASE):
            return "Invalid username (must match IRC standards)."
        user = d2_user.query.filter_by(username=username).first()
        if user:
            return "A user with that username already exists."
        else:
            create_user = d2_user(username, '', '', 0, '', '', '', '', '', 0, password, 0, 0, 0, 0, 0, 0, 0, unix_time_current(), unix_time_current(), unix_time_current(), '', '', '')
            syndbb.db.session.add(create_user)
            syndbb.db.session.flush()
            created_user_id = str(create_user.user_id)
            syndbb.db.session.commit()

            session_id = str(syndbb.uuid.uuid1())
            new_session = d2_session(created_user_id, session_id, unix_time_current())
            syndbb.db.session.add(new_session)
            syndbb.db.session.commit()

            invites.used_by = created_user_id
            syndbb.db.session.commit()

            syndbb.session['logged_in'] = session_id
            return "Registration successful."
    else:
        return "Invalid request."

@syndbb.app.route("/functions/login", methods=['GET', 'POST'])
def dologin():
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(syndbb.session['logged_in']))
        if userid:
            return "You are already logged in!"

    username = syndbb.request.form['username']
    password = d2_hash(syndbb.request.form['password'])

    #syndbb.app.logger.debug("""DEBUG: Username: """ + username+ """\nDEBUG: Hashed Password: """ + password)

    user = d2_user.query.filter_by(username=username).first()
    my_ip = syndbb.request.remote_addr

    if user:
        session_id = str(syndbb.uuid.uuid1())
        if user.password == password:
            new_session = d2_session(user.user_id, session_id, unix_time_current())
            syndbb.db.session.add(new_session)
            syndbb.db.session.commit()
            syndbb.session['logged_in'] = session_id

            user.last_login = unix_time_current()
            syndbb.db.session.commit()

            login_ip = d2_ip(my_ip, user.user_id, unix_time_current(), 2, syndbb.request.path)
            syndbb.db.session.add(login_ip)
            syndbb.db.session.commit()

            return "Login successful."
        else:
            login_ip = d2_ip(my_ip, user.user_id, unix_time_current(), 0, syndbb.request.path)
            syndbb.db.session.add(login_ip)
            syndbb.db.session.commit()
            return "Invalid password."
    else:
        return "Invalid username."

@syndbb.app.route('/functions/logout')
def logout():
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(syndbb.session['logged_in']))
        if userid:
            uniqid = syndbb.request.args.get('uniqid', '')
            if str(uniqid) == str(syndbb.session['logged_in']):
                check_session = d2_session.query.filter_by(sessionid=uniqid).first()
                if check_session:
                    #syndbb.app.logger.debug("DEBUG: Deleting Session: " + check_session.sessionid)
                    syndbb.db.session.delete(check_session)
                    syndbb.db.session.commit()

                    syndbb.session.pop('logged_in', None)
                    syndbb.flash('You have been logged out.', 'warning')
                    return syndbb.redirect(syndbb.url_for('home'))
                else:
                    syndbb.flash('Invalid request.', 'warning')
                    syndbb.session.pop('logged_in', None)
                    return syndbb.redirect(syndbb.url_for('home'))
            else:
                syndbb.flash('Invalid session.', 'warning')
                syndbb.session.pop('logged_in', None)
                return syndbb.redirect(syndbb.url_for('home'))
        else:
            return syndbb.render_template('error_not_logged_in.html', title="Not logged in")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Not logged in")

@syndbb.app.route("/functions/change_password", methods=['GET', 'POST'])
def do_change_password():
    oldpassword = d2_hash(syndbb.request.form['oldpassword'])
    newpassword = d2_hash(syndbb.request.form['newpassword'])
    uniqid = syndbb.request.form['uniqid']

    if oldpassword and newpassword and uniqid:
        userid = checkSession(uniqid)
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            if user.password == oldpassword:
                user.password = newpassword
                syndbb.db.session.commit()
                return "Password change successful."
            else:
                return "Invalid old password."
        else:
            return "Invalid Session"
    else:
        return "Invalid Request"
