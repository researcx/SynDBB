#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb
from syndbb.models.quotedb import d2_quotes
from syndbb.models.users import d2_user, get_avatar, get_group_style_from_id, checkSession
from syndbb.models.time import time_ago, human_date, unix_time_current

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

@syndbb.app.route("/quotes/")
def view_qdb():
    dynamic_css_header = ["css/rating.css"]
    dynamic_js_footer = ["js/jquery.rangyinputs.js", "js/quotes.js", "js/inline.js", "js/post_ratings.js", "js/bootbox.min.js"]

    quotes = d2_quotes.query.filter_by(approved=1).order_by(d2_quotes.time.desc()).all()

    return syndbb.render_template('quote_list.html', quotes=quotes, dynamic_css_header=dynamic_css_header, dynamic_js_footer=dynamic_js_footer, title="Quote Database")

@syndbb.app.route("/functions/create_quote/", methods=['GET', 'POST'])
def create_quotes():
    uniqid = syndbb.request.form['uniqid']
    tpost = syndbb.request.form['post_content']
    if tpost and uniqid:
        userid = checkSession(uniqid)
        if userid:
            lastquote = d2_quotes.query.filter_by(user_id=userid).order_by(d2_quotes.time.desc()).first()
            if lastquote and (unix_time_current() - lastquote.time) <= 1:
                return "Trying to submit quotes too quickly, wait a while before trying again."
            else:
                create_quote = d2_quotes(userid, unix_time_current(), tpost, 0)
                syndbb.db.session.add(create_quote)
                syndbb.db.session.commit()
                syndbb.flash('Quote has been submitted.', 'success')
                return syndbb.redirect(syndbb.url_for('view_qdb'))
        else:
            return "Invalid Session"
    else:
        return "Invalid Request"
