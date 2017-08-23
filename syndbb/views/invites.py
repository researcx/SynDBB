#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb
from syndbb.models.users import d2_user, checkSession
from syndbb.models.invites import d2_invites, d2_requests

@syndbb.app.route("/account/invite")
def my_invites():
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(syndbb.session['logged_in']))
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            invites = d2_invites.query.filter_by(user_id=userid).all()
            subheading = []
            subheading.append("<a href='/user/" + user.username + "/'>" + user.username + "</a>")
            return syndbb.render_template('invites.html', invite_list=invites, title="Invites", subheading=subheading)
        else:
            return syndbb.render_template('error_not_logged_in.html', title="Invites")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Invites")

@syndbb.app.route('/functions/generate_invite/')
def generate_invite():
    uniqid = syndbb.request.args.get('uniqid', '')
    userid = checkSession(str(uniqid))
    code = str(syndbb.uuid.uuid4().hex)
    if userid:
        create_invite = d2_invites(code, userid, 0)
        syndbb.db.session.add(create_invite)
        syndbb.db.session.commit()

        syndbb.flash('An invite has been generated.', 'success')
        return syndbb.redirect(syndbb.url_for('my_invites'))
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Not logged in")

@syndbb.app.route("/request-invite/")
def request_invite():
    return syndbb.render_template('request_invite.html', title="Request Invite")

@syndbb.app.route("/functions/request_invite/", methods=['GET', 'POST'])
def do_request_invite():
    username = syndbb.request.form['username']
    email = syndbb.request.form['email']
    reason = syndbb.request.form['reason']
    if username and email and reason:
        if not syndbb.re.match(r"[^@]+@[^@]+\.[^@]+", email):
            syndbb.flash('The email you entered was invalid.', 'danger')
            return syndbb.redirect(syndbb.url_for('request_invite'))
        invitecheck = d2_requests.query.filter_by(email=email).first()
        if invitecheck:
            syndbb.flash('An invite for this email has already been requested.', 'danger')
            return syndbb.redirect(syndbb.url_for('request_invite'))
        create_request = d2_requests(username, email, reason)
        syndbb.db.session.add(create_request)
        syndbb.db.session.commit()
        syndbb.flash('Your invite request has been submitted.', 'success')
        return syndbb.redirect(syndbb.url_for('request_invite'))
    else:
        syndbb.flash('Invalid Request.', 'danger')
        return syndbb.redirect(syndbb.url_for('request_invite'))
