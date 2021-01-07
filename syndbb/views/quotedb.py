#
# Copyright (c) 2017 - 2020 Keira T (https://kei.info.gf). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb
from syndbb.models.quotedb import d2_quotes
from syndbb.models.users import d2_user, get_avatar_by_id, get_group_style_by_id, check_session_by_id
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
    dynamic_js_footer = ["js/jquery.rangyinputs.js", "js/inline.js", "js/post_ratings.js", "js/bootbox.min.js"] # "js/quotes.js"

    quotes = d2_quotes.query.filter_by(approved=1).order_by(d2_quotes.rating.desc()).order_by(d2_quotes.time.desc()).all()

    return syndbb.render_template('quote_list.html', quotes=quotes, dynamic_js_footer=dynamic_js_footer, title="Quote Database", subheading=[""])

@syndbb.app.route("/functions/create_quote/", methods=['GET', 'POST'])
def create_quotes():
    uniqid = syndbb.request.form['uniqid']
    tpost = syndbb.request.form['post_content']
    if tpost and uniqid:
        userid = check_session_by_id(uniqid)
        if userid:
            lastquote = d2_quotes.query.filter_by(user_id=userid).order_by(d2_quotes.time.desc()).first()
            if lastquote and (unix_time_current() - lastquote.time) <= syndbb.core_config['site']['quote_timeout']:
                return "Trying to submit quotes too quickly, wait a while before trying again."
            else:
                create_quote = d2_quotes(userid, unix_time_current(), tpost, 0, 0)
                syndbb.db.session.add(create_quote)
                syndbb.db.session.commit()
                syndbb.flash('Quote has been submitted.', 'success')
                return syndbb.redirect(syndbb.url_for('view_qdb'))
        else:
            return "Invalid Session"
    else:
        return "Invalid Request"
