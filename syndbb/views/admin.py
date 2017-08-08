#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb, glob, shutil
from syndbb.models.users import d2_user, d2_bans, checkSession, is_banned
from syndbb.models.forums import d2_forums, d2_activity
from syndbb.models.quotedb import d2_quotes
from syndbb.models.time import unix_time_current

@syndbb.app.route("/account/admin")
def siteadmin():
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(syndbb.session['logged_in']))
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            if user.rank >= 900:
                usercount = d2_user.query.count()
                postcount = d2_activity.query.filter(d2_activity.replyto != 0).count()
                threadcount = d2_activity.query.filter(d2_activity.category != 0).count()
                bancount = d2_bans.query.count()
                officialforumcount = d2_forums.query.filter(d2_forums.owned_by == 0).count()
                unofficialforumcount = d2_forums.query.filter(d2_forums.owned_by != 0).count()
                unapprovedforumcount = d2_forums.query.filter(d2_forums.approved == 0).count()
                return syndbb.render_template('admin.html', usercount=usercount, postcount=postcount, threadcount=threadcount, bancount=bancount, officialforumcount=officialforumcount, unofficialforumcount=unofficialforumcount, unapprovedforumcount=unapprovedforumcount, title="Administration")
            else:
                return syndbb.render_template('invalid.html', title="Not Found")
        else:
            return syndbb.render_template('error_not_logged_in.html', title="Administration")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Administration")

@syndbb.app.route("/account/admin/users")
def siteadmin_users():
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(syndbb.session['logged_in']))
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            if user.rank >= 500:
                users = d2_user.query.order_by(d2_user.rank.desc()).order_by(d2_user.join_date.asc()).all()
                return syndbb.render_template('admin_users.html', users=users, title="Administration &bull; User List")
            else:
                return syndbb.render_template('invalid.html', title="Not Found")
        else:
            return syndbb.render_template('error_not_logged_in.html', title="Administration")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Administration")

@syndbb.app.route("/account/admin/rank/")
def siteadmin_rank():
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(syndbb.session['logged_in']))
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            if user.rank >= 900:
                rankuser = syndbb.request.args.get('user', '')
                return syndbb.render_template('admin_rank.html', rankuser=rankuser, title="Administration &bull; Change Rank")
            else:
                return syndbb.render_template('invalid.html', title="Not Found")
        else:
            return syndbb.render_template('error_not_logged_in.html', title="Administration")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Administration")

@syndbb.app.route("/account/admin/ban/")
def siteadmin_ban():
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(syndbb.session['logged_in']))
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            if user.rank >= 500:
                banuser = syndbb.request.args.get('user', '')
                banpost = syndbb.request.args.get('post_id', '')
                isbanned = is_banned(banuser)
                return syndbb.render_template('admin_ban.html', isbanned=isbanned, banuser=banuser, banpost=banpost, title="Administration &bull; Ban User")
            else:
                return syndbb.render_template('invalid.html', title="Not Found")
        else:
            return syndbb.render_template('error_not_logged_in.html', title="Administration")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Administration")

@syndbb.app.route("/functions/ban_user/", methods=['GET', 'POST'])
def do_ban_user():
    banuser = syndbb.request.form['user_id']
    bantime = syndbb.request.form['time']

    if 'reason' in syndbb.request.form:
        banreason = syndbb.request.form['reason']
    else:
        banreason = ""

    if 'post_id' in syndbb.request.form:
        banpost = syndbb.request.form['post_id']
    else:
        banpost = 0
    uniqid = syndbb.request.form['uniqid']

    if banuser and bantime and uniqid:
        userid = checkSession(uniqid)
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            if user.rank >= 500:
                if banreason != "":
                    banmessage = "\n\n[ban](User was banned for this post. Reason: " + banreason + ")[/ban]"
                else:
                    banmessage = "\n\n[ban](User was banned for this post.)[/ban]"

                if bantime == 0:
                    banexpire = 0
                else:
                    banexpire = int(bantime) + unix_time_current()

                if banpost and banpost != 0:
                    post = d2_activity.query.filter_by(id=banpost).first()
                    post.content += banmessage
                    syndbb.db.session.commit()

                new_ban = d2_bans(banned_id=banuser, reason=banreason, length=bantime, time=unix_time_current(), expires=banexpire, post=banpost, banner=userid)
                syndbb.db.session.add(new_ban)
                syndbb.db.session.commit()

                syndbb.flash('User banned successfully.', 'success')
                return syndbb.redirect(syndbb.url_for('siteadmin_ban'))
            else:
                return syndbb.render_template('invalid.html', title="Not Found")
        else:
            return "Invalid Session"
    else:
        return "Invalid Request"

@syndbb.app.route("/functions/admin_change_rank/", methods=['GET', 'POST'])
def do_rank_user():
    rankuser = syndbb.request.form['user_id']
    rank = syndbb.request.form['rank']
    uniqid = syndbb.request.form['uniqid']

    if rankuser and rank and uniqid:
        userid = checkSession(uniqid)
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            if user.rank >= 900:
                changeuser = d2_user.query.filter_by(user_id=rankuser).first()
                changeuser.rank = rank
                syndbb.db.session.commit()

                syndbb.flash('User rank changed successfully.', 'success')
                return syndbb.redirect(syndbb.url_for('siteadmin_users'))
            else:
                return syndbb.render_template('invalid.html', title="Not Found")
        else:
            return "Invalid Session"
    else:
        return "Invalid Request"

@syndbb.app.route("/functions/unban_user/", methods=['GET', 'POST'])
def do_unban_user():
    banuser = syndbb.request.form['user_id']
    uniqid = syndbb.request.form['uniqid']

    if banuser and uniqid:
        userid = checkSession(uniqid)
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            if user.rank >= 500:
                ban = d2_bans.query.filter_by(banned_id=banuser).first()
                if ban.length == 0:
                    ban.length = -1
                ban.expires = unix_time_current()
                syndbb.db.session.commit()

                syndbb.flash('User unbanned successfully.', 'success')
                return syndbb.redirect(syndbb.url_for('siteadmin_ban'))
            else:
                return syndbb.render_template('invalid.html', title="Not Found")
        else:
            return "Invalid Session"
    else:
        return "Invalid Request"

### Approve/Disapprove Emoticons ###
@syndbb.app.route("/account/admin/emoticons")
def siteadmin_emoticons():
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(syndbb.session['logged_in']))
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            if user.rank >= 900:
                emote_list = []
                emotfolder = syndbb.os.getcwd() + "/syndbb/static/data/emoticons/"
                if not syndbb.os.path.exists(emotfolder):
                    syndbb.os.makedirs(emotfolder)

                for emote in glob.glob(emotfolder+"**", recursive=True):
                    filepath = emote.replace(emotfolder, "")
                    if syndbb.os.path.isfile(emote):
                        addtime = int(syndbb.os.stat(emote).st_mtime)
                        code = syndbb.os.path.splitext(emote)[0]
                        code = ":" + syndbb.re.sub(r'.*/', '', code) + ":"
                        emote_list.append([filepath, code])
                emote_list.sort(reverse=False)

                print(emote_list)
                return syndbb.render_template('admin_emoticons.html', emote_list=emote_list, title="Administration &bull; Emoticon List")
            else:
                return syndbb.render_template('invalid.html', title="Not Found")
        else:
            return syndbb.render_template('error_not_logged_in.html', title="Administration")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Administration")

@syndbb.app.route("/functions/approve_emoticon/")
def approve_emoticon():
    emote = syndbb.request.args.get('file', '')
    uniqid = syndbb.request.args.get('uniqid', '')

    if uniqid:
        userid = checkSession(uniqid)
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            if user.rank >= 900:
                emotepath = syndbb.os.getcwd() + "/syndbb/static/data/emoticons/" + emote
                destpath = syndbb.os.getcwd() + "/syndbb/static/images/emots/"
                if syndbb.os.path.isfile(emotepath):
                    shutil.copy2(emotepath, destpath)
                    syndbb.os.remove(emotepath)
                    syndbb.flash('Emoticon approved successfully.', 'success')
                    return syndbb.redirect(syndbb.url_for('siteadmin_emoticons'))
                else:
                    syndbb.flash('No such emoticon exists.', 'danger')
                    return syndbb.redirect(syndbb.url_for('siteadmin_emoticons'))
            else:
                return syndbb.render_template('invalid.html', title="Not Found")
        else:
            return "Invalid Session"
    else:
        return "Invalid Request"

@syndbb.app.route("/functions/disapprove_emoticon/")
def disapprove_emoticon():
    emote = syndbb.request.args.get('file', '')
    uniqid = syndbb.request.args.get('uniqid', '')

    if uniqid:
        userid = checkSession(uniqid)
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            if user.rank >= 900:
                emotepath = syndbb.os.getcwd() + "/syndbb/static/data/emoticons/" + emote
                if syndbb.os.path.isfile(emotepath):
                    syndbb.os.remove(emotepath)
                    syndbb.flash('Emoticon deleted successfully.', 'success')
                    return syndbb.redirect(syndbb.url_for('siteadmin_emoticons'))
                else:
                    syndbb.flash('No such emoticon exists.', 'danger')
                    return syndbb.redirect(syndbb.url_for('siteadmin_emoticons'))
            else:
                return syndbb.render_template('invalid.html', title="Not Found")
        else:
            return "Invalid Session"
    else:
        return "Invalid Request"

### Approve/Disapprove Quotes ###
@syndbb.app.route("/account/admin/quotes")
def siteadmin_quotes():
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(syndbb.session['logged_in']))
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            if user.rank >= 500:
                unapproved = d2_quotes.query.filter_by(approved=0).order_by(d2_quotes.time.desc()).all()
                return syndbb.render_template('admin_quotes.html', unapproved=unapproved, title="Administration &bull; Unapproved Quotes")
            else:
                return syndbb.render_template('invalid.html', title="Not Found")
        else:
            return syndbb.render_template('error_not_logged_in.html', title="Administration")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Administration")

@syndbb.app.route("/functions/approve_quote/")
def approve_quote():
    quote = syndbb.request.args.get('quote', '')
    uniqid = syndbb.request.args.get('uniqid', '')

    if quote and uniqid:
        userid = checkSession(uniqid)
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            if user.rank >= 900:
                quote = d2_quotes.query.filter_by(id=quote).first()
                if quote:
                    quote.approved = 1
                    syndbb.db.session.commit()

                    syndbb.flash('Quote has been approved.', 'success')
                    return syndbb.redirect(syndbb.url_for('siteadmin_quotes'))
                else:
                    syndbb.flash('No such quote exists.', 'danger')
                    return syndbb.redirect(syndbb.url_for('siteadmin_quotes'))
            else:
                return "You are not an administrator"
        else:
            return "Invalid Session"
    else:
        return "Invalid Request"

@syndbb.app.route("/functions/disapprove_quote/")
def disapprove_quote():
    quote = syndbb.request.args.get('quote', '')
    uniqid = syndbb.request.args.get('uniqid', '')

    if quote and uniqid:
        userid = checkSession(uniqid)
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            if user.rank >= 900:
                quote = d2_quotes.query.filter_by(id=quote).first()
                if quote:
                    syndbb.db.session.delete(quote)
                    syndbb.db.session.commit()

                    syndbb.flash('Quote has been disapproved.', 'danger')
                    return syndbb.redirect(syndbb.url_for('siteadmin_quotes'))
                else:
                    syndbb.flash('No such quote exists.', 'danger')
                    return syndbb.redirect(syndbb.url_for('siteadmin_quotes'))
            else:
                return "You are not an administrator"
        else:
            return "Invalid Session"
    else:
        return "Invalid Request"

### Approve/Disapprove Channels ###
@syndbb.app.route("/account/admin/channels")
def siteadmin_channels():
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(syndbb.session['logged_in']))
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            if user.rank >= 900:
                unapproved = d2_forums.query.filter(d2_forums.approved == 0).all()
                return syndbb.render_template('admin_channels.html', unapproved=unapproved, title="Administration &bull; Unapproved Channels")
            else:
                return syndbb.render_template('invalid.html', title="Not Found")
        else:
            return syndbb.render_template('error_not_logged_in.html', title="Administration")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Administration")

@syndbb.app.route("/functions/approve_channel/")
def approve_channel():
    channel = syndbb.request.args.get('channel', '')
    uniqid = syndbb.request.args.get('uniqid', '')

    if channel and uniqid:
        userid = checkSession(uniqid)
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            if user.rank >= 900:
                channel = d2_forums.query.filter_by(id=channel).first()
                if channel:
                    channel.approved = 1
                    syndbb.db.session.commit()

                    syndbb.flash('Channel has been approved.', 'success')
                    return syndbb.redirect(syndbb.url_for('siteadmin_channels'))
                else:
                    syndbb.flash('No such channel exists.', 'danger')
                    return syndbb.redirect(syndbb.url_for('siteadmin_channels'))
            else:
                return "You are not an administrator"
        else:
            return "Invalid Session"
    else:
        return "Invalid Request"

@syndbb.app.route("/functions/disapprove_channel/")
def disapprove_channel():
    channel = syndbb.request.args.get('channel', '')
    uniqid = syndbb.request.args.get('uniqid', '')

    if channel and uniqid:
        userid = checkSession(uniqid)
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            if user.rank >= 900:
                channel = d2_forums.query.filter_by(id=channel).first()
                if channel:
                    syndbb.db.session.delete(channel)
                    syndbb.db.session.commit()

                    syndbb.flash('Channel has been disapproved.', 'danger')
                    return syndbb.redirect(syndbb.url_for('siteadmin_channels'))
                else:
                    syndbb.flash('No such channel exists.', 'danger')
                    return syndbb.redirect(syndbb.url_for('siteadmin_channels'))
            else:
                return "You are not an administrator"
        else:
            return "Invalid Session"
    else:
        return "Invalid Request"
