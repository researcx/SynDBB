#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb
from syndbb.models.users import d2_user, d2_session, checkSession
from syndbb.models.paste import d2_paste
from syndbb.models.time import unix_time_current

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

@syndbb.app.route("/pastebin/")
def pastebin():
    if 'logged_in' in syndbb.session:
        dynamic_js_footer = ["js/bootbox.min.js", "js/delete.js"]
        userid = checkSession(str(syndbb.session['logged_in']))
        if userid:
            getPastes = d2_paste.query.filter(d2_paste.user_id == userid).order_by(syndbb.db.desc(d2_paste.time)).all()
            return syndbb.render_template('pastebin.html', dynamic_js_footer=dynamic_js_footer, paste_list=getPastes, title="Pastebin", subheading=[""])
        else:
            return syndbb.render_template('error_not_logged_in.html', title="Pastebin", subheading=[""])
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Pastebin", subheading=[""])

@syndbb.app.route("/pastebin/<paste>")
def paste(paste):
    getPaste = d2_paste.query.filter(d2_paste.paste_id == paste).first()
    subheading = ['<a href="/pastebin/">Pastebin</a>']
    if getPaste:
        return syndbb.render_template('pastebin.html', paste=getPaste, title="" + getPaste.title, subheading=subheading)
    else:
        return syndbb.render_template('invalid.html', title="Invalid Paste", subheading=subheading)

@syndbb.app.route("/functions/dopaste", methods=['GET', 'POST'])
def dopaste():
    paste_title = syndbb.request.form['paste_title']
    paste_content = syndbb.request.form['paste_content']
    uniqid = syndbb.request.form['uniqid']

    if paste_title and paste_content and uniqid:
        userid = checkSession(uniqid)
        if userid:
            pasteid = str(syndbb.uuid.uuid4().hex)
            new_paste = d2_paste(userid, pasteid, unix_time_current(), html_escape(paste_content), html_escape(paste_title))
            syndbb.db.session.add(new_paste)
            syndbb.db.session.commit()
            syndbb.flash('Paste created successfully.', 'success')
            return syndbb.redirect(syndbb.url_for('pastebin'))
        else:
            return "Invalid Session"
    else:
        return "Invalid Request"

@syndbb.app.route("/functions/undopaste")
def undopastes():
    paste_id = syndbb.request.args.get('paste_id')
    uniqid = syndbb.request.args.get('uniqid')

    if paste_id and uniqid:
        userid = checkSession(uniqid)
        if userid:
            deletePaste = d2_paste.query.filter(d2_paste.user_id == userid).filter(d2_paste.paste_id == paste_id).order_by(syndbb.db.desc(d2_paste.time)).first()
            syndbb.db.session.delete(deletePaste)
            syndbb.db.session.commit()
            syndbb.flash('Paste deleted.', 'success')
            return syndbb.redirect(syndbb.url_for('pastebin'))
        else:
            return "Invalid Session"
    else:
        return "Invalid Request"
