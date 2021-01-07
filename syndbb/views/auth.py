#
# Copyright (c) 2017 - 2020 Keira T (https://kei.info.gf). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb, requests, json
from stopforumspam_api import query
from syndbb.models.users import d2_user, d2_bans, d2_ip, check_session_by_id, gdpr_check
from syndbb.models.d2_hash import d2_hash, get_ip_hash
from syndbb.models.time import unix_time_current
from syndbb.models.invites import d2_invites

if syndbb.core_config['ldap']['enabled'] :
    from syndbb.models.d2_hash import ldap_hash
    from syndbb.models.users import ldap_user

@syndbb.app.route("/login/")
def login():
    if 'logged_in' in syndbb.session:
        userid = check_session_by_id(str(syndbb.session['logged_in']))
        if userid:
            return syndbb.render_template('error_already_logged_in.html', title="Log In")

    dynamic_js_footer = ["js/crypt.js", "js/bootbox.min.js"]
    if syndbb.core_config['ldap']['enabled'] :
        dynamic_js_footer.append("js/auth_plain/auth_login.js")
    else:
        dynamic_js_footer.append("js/auth_hash/auth_login.js")
    return syndbb.render_template('login.html', dynamic_js_footer=dynamic_js_footer, title="Log In")

@syndbb.app.route("/register/")
def register():
    if 'logged_in' in syndbb.session:
        userid = check_session_by_id(str(syndbb.session['logged_in']))
        if userid:
            return syndbb.render_template('error_already_logged_in.html', title="Registration")

    dynamic_js_footer = ["js/crypt.js", "js/bootbox.min.js", "js/random_name.js"]
    if syndbb.core_config['ldap']['enabled'] :
        dynamic_js_footer.append("js/auth_plain/auth_regd.js")
    else:
        dynamic_js_footer.append("js/auth_hash/auth_regd.js")
    reg_template = "register_invite.html" if syndbb.core_config['site']['invite_only'] else "register.html"
    if not syndbb.core_config['site']['registration'] :
        reg_template = "register_disabled.html"
    return syndbb.render_template(reg_template, dynamic_js_footer=dynamic_js_footer, invite_code='', title="Registration")
  
#    if 'logged_in' in syndbb.session:
#        userid = check_session_by_id(str(syndbb.session['logged_in']))
#        if userid:
#            return syndbb.render_template('error_already_logged_in.html', title="Registration")
#
#    dynamic_js_footer = ["js/crypt.js", "js/auth_hash/auth_regd.js", "js/bootbox.min.js"]
#    return syndbb.redirect(syndbb.url_for('request_invite'))

#    if invite:
#        invites = d2_invites.query.filter_by(code=invite, used_by=0).first()
#        if not invites:
#            syndbb.flash('The invite code provided is invalid.', 'danger')
#        else:
#            syndbb.flash('The invite code provided is valid.', 'success')



@syndbb.app.route("/register/<invite>")
def register_invite(invite):
    if 'logged_in' in syndbb.session:
        userid = check_session_by_id(str(syndbb.session['logged_in']))
        if userid:
            return syndbb.render_template('error_already_logged_in.html', title="Registration")

    if invite:
        invites = d2_invites.query.filter_by(code=invite, used_by=0).first()
        if not invites:
            syndbb.flash('The invite code provided is invalid.', 'danger')
        else:
            syndbb.flash('The invite code provided is valid.', 'success')

    dynamic_js_footer = ["js/crypt.js", "js/bootbox.min.js", "js/random_name.js"]
    if syndbb.core_config['ldap']['enabled'] :
        dynamic_js_footer.append("js/auth_plain/auth_regd.js")
    else:
        dynamic_js_footer.append("js/auth_hash/auth_regd.js")
    return syndbb.render_template('register.html', invite=invites, dynamic_js_footer=dynamic_js_footer, invite_code=invite, title="Registration")

@syndbb.app.route("/functions/register/", methods=['GET', 'POST'])
def doregister():
    if 'logged_in' in syndbb.session:
        userid = check_session_by_id(str(syndbb.session['logged_in']))
        if userid:
            return "You are already logged in!"

    username = syndbb.request.form['username']
    password = syndbb.request.form['password']
    tos = syndbb.request.form['tos']

    my_ip = gdpr_check(syndbb.request.remote_addr)
    my_ip_hash = get_ip_hash(syndbb.request.remote_addr)
    
    # tor = requests.get('https://check.torproject.org/exit-addresses', verify=False, timeout=5, stream=True)
    
    # torlines = ""
    
    # for line in tor.iter_lines():
    #     if line: torlines += str(line)
    
    # for ip_tor in torlines:
    #     ip_tor = ip_tor.replace("\n","")
    #     if "ExitAddress" in ip_tor:
    #         ip_tor = ip_tor.split(" ")[1]
    #         if my_ip == ip_tor:
    #             return "You seem to be using Tor or a proxy."
                
    # response = query(ip=my_ip)
    # if response.ip.appears == True:
    #     return "You seem to be using Tor or a proxy, or your IP is blacklisted for spam."
    
    if not tos:
        return "You have not agreed to the rules and terms of service."
    
    # if not token:
    #     return "You must verify yourself."
    
    # if captcha['success'] == False:
    #     return "You must verify yourself."

    if username and password:
        if not syndbb.core_config['site']['registration']:
            return 'Registration is disabled.'
        if syndbb.core_config['site']['invite_only']:
            code = syndbb.request.form['code']
            invites = d2_invites.query.filter_by(code=code, used_by=0).first()
            if not invites:
                return 'The invite code provided is invalid.'
        if not syndbb.re.search('^[a-z][a-z0-9-_]{2,32}$', username, syndbb.re.IGNORECASE):
            return "Invalid username (must match IRC standards)."
        user = d2_user.query.filter_by(username=username).first()
        if user:
            return "A user with that username already exists."
        else:  
            useragent = syndbb.request.headers.get('User-Agent')
            session_hash = d2_hash(syndbb.request.remote_addr + useragent + d2_hash(str(syndbb.uuid.uuid1())))[:20]
            similar_user = d2_hash(syndbb.request.remote_addr + useragent)[:20]

            create_user = d2_user(username=username, display_name='', token='', title='', bio='[i]Welcome to my profile![/i]', status='', status_time=0, rank=1, avatar_date=0, password=d2_hash(syndbb.request.form['password_hash']) if syndbb.core_config['ldap']['enabled']  else d2_hash(password), post_count=0, line_count=0, word_count=0, profanity_count=0, karma_positive=0, karma_negative=0, points=0, join_date=unix_time_current(), last_login=unix_time_current(), last_activity=unix_time_current(), irc_auth='', upload_auth='', user_auth=similar_user, upload_url='local', nsfw_toggle=0, full_avatar=0, tags="Location:This_Website new_user")
            syndbb.db.session.add(create_user)
            syndbb.db.session.flush()
            created_user_id = str(create_user.user_id)
            syndbb.db.session.commit()

            if syndbb.core_config['ldap']['enabled'] :
                ldap_add_user = ldap_user(
                    display_name=username,
                    username=username,
                    surname=username,
                    password=ldap_hash(password)
                )
                ldap_add_user.save()

            login_ip = d2_ip(my_ip, useragent, created_user_id, unix_time_current(), 1, syndbb.request.path, session_hash, my_ip_hash)
            syndbb.db.session.add(login_ip)
            syndbb.db.session.commit()
            if syndbb.core_config['site']['invite_only'] :
                invites.used_by = created_user_id
            syndbb.db.session.commit()

            syndbb.session['logged_in'] = session_hash
            return "Registration successful."
    else:
        return "Invalid request."

@syndbb.app.route("/functions/login", methods=['GET', 'POST'])
def dologin():
    if 'logged_in' in syndbb.session:
        userid = check_session_by_id(str(syndbb.session['logged_in']))
        if userid:
            return "You are already logged in!"

    username = syndbb.request.form['username']
    password = syndbb.request.form['password']

    user = d2_user.query.filter_by(username=username).first()
    my_ip = gdpr_check(syndbb.request.remote_addr)
    my_ip_hash = get_ip_hash(syndbb.request.remote_addr)
    useragent = syndbb.request.headers.get('User-Agent')
    session_hash = d2_hash(syndbb.request.remote_addr + useragent + d2_hash(str(syndbb.uuid.uuid1())))[:20]

    if user:
        if syndbb.core_config['ldap']['enabled'] :
            password_hash = syndbb.request.form['password_hash']
            is_ldap_user = ldap_user.query.filter(syndbb.core_config['ldap']['attribute_cn'] + ': '+username).first()
            if user.password == d2_hash(password_hash):
                if not is_ldap_user:
                    login_ip = d2_ip(my_ip, useragent, user.user_id, unix_time_current(), 1, syndbb.request.path, session_hash, my_ip_hash)
                    syndbb.db.session.add(login_ip)
                    syndbb.db.session.commit()
                    
                    syndbb.session['logged_in'] = session_hash
                    syndbb.session.permanent = True
                    
                    user.last_login = unix_time_current()

                    ldap_add_user = ldap_user(
                        display_name=username,
                        username=username,
                        surname=username,
                        password=ldap_hash(password)
                    )
                    ldap_add_user.save()
                    return "Login successful."

            valid = syndbb.ldap.authenticate(username, password, syndbb.core_config['ldap']['attribute_cn'], syndbb.core_config['ldap']['base_dn'] )
            if not valid:
                login_ip = d2_ip(my_ip, useragent, user.user_id, unix_time_current(), 0, syndbb.request.path, "N/A", my_ip_hash)
                syndbb.db.session.add(login_ip)
                syndbb.db.session.commit()
                return 'Invalid credentials.'
                
            login_ip = d2_ip(my_ip, useragent, user.user_id, unix_time_current(), 1, syndbb.request.path, session_hash, my_ip_hash)
            syndbb.db.session.add(login_ip)
            syndbb.db.session.commit()

            syndbb.session['logged_in'] = session_hash
            syndbb.session.permanent = True
            return 'Login successful.'
        else:
            if user.password == d2_hash(password):
                login_ip = d2_ip(my_ip, useragent, user.user_id, unix_time_current(), 1, syndbb.request.path, session_hash, my_ip_hash)
                syndbb.db.session.add(login_ip)
                syndbb.db.session.commit()
                
                syndbb.session['logged_in'] = session_hash
                syndbb.session.permanent = True
                
                user.last_login = unix_time_current()
                
                return "Login successful."
            else:
                login_ip = d2_ip(my_ip, useragent, user.user_id, unix_time_current(), 0, syndbb.request.path, "N/A", my_ip_hash)
                syndbb.db.session.add(login_ip)
                syndbb.db.session.commit()
                return "Invalid credentials."
    else:
        return "Invalid credentials."

@syndbb.app.route('/functions/logout')
def logout():
    if 'logged_in' in syndbb.session:
        userid = check_session_by_id(str(syndbb.session['logged_in']))
        if userid:
            uniqid = syndbb.request.args.get('uniqid', '')
            if str(uniqid) == str(syndbb.session['logged_in']):
                check_session = d2_ip.query.filter_by(sessionid=uniqid).filter_by(ip=gdpr_check(syndbb.request.remote_addr)).first()
                if check_session:
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
    old_password = syndbb.request.form['oldpassword']
    new_password = syndbb.request.form['newpassword']
    uniqid = syndbb.request.form['uniqid']

    if old_password and new_password and uniqid:
        userid = check_session_by_id(uniqid)
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            if syndbb.core_config['ldap']['enabled'] :
                new_password_hash = syndbb.request.form['newpassword_hash']
                is_ldap_user = ldap_user.query.filter(syndbb.core_config['ldap']['attribute_cn'] + ': '+user.username).first()
                if is_ldap_user:
                    valid = syndbb.ldap.authenticate(user.username, old_password, syndbb.core_config['ldap']['attribute_cn'], syndbb.core_config['ldap']['base_dn'] )
                    if valid:
                        ldapuser = ldap_user.query.filter(syndbb.core_config['ldap']['attribute_cn'] + ': '+user.username).first()
                        ldapuser.password = ldap_hash(new_password)
                        ldapuser.save()
        
                        user.password = d2_hash(new_password_hash)
                        syndbb.db.session.commit()
                    else:
                        return "Invalid old password."
            else:
                if user.password == d2_hash(old_password):
                    user.password = d2_hash(new_password)
                    syndbb.db.session.commit()
                else:
                     return "Invalid old password."
            check_session = d2_ip.query.filter_by(user_id=user.user_id).filter_by(login=1).all()
            for usession in check_session:
                syndbb.db.session.delete(usession)
                syndbb.db.session.commit()
            syndbb.session.pop('logged_in', None)
            syndbb.flash('You have been logged out due to a password change.', 'danger')
            return "Password change successful."
        else:
            return "Invalid Session"
    else:
        return "Invalid Request"
