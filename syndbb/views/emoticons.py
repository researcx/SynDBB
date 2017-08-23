#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb
from io import BytesIO
from PIL import Image
from werkzeug.utils import secure_filename

from syndbb.models.get_emote import get_emote, get_submitted_emote
from syndbb.models.users import d2_user, d2_session, checkSession

@syndbb.app.route("/emoticons/")
def emoticons():
    dynamic_js_footer = ["js/lazyload.transpiled.min.js"]
    emote_list = get_emote()
    return syndbb.render_template('emoticons.html', emote_list=emote_list, dynamic_js_footer=dynamic_js_footer, title="Emoticons", subheading=[""])


@syndbb.app.route("/submit-emoticon/")
def submit_emoticon():
    if 'logged_in' in syndbb.session:
        dynamic_js_footer = ["js/lazyload.transpiled.min.js", "js/bootbox.min.js", "js/delete.js"]
        emote_list = get_submitted_emote()
        return syndbb.render_template('submit-emoticon.html', emote_list=emote_list, dynamic_js_footer=dynamic_js_footer, title="Submit Emoticon", subheading=["Emoticons"])
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Submit Emoticon", subheading=["Emoticons"])


@syndbb.app.route("/functions/delete_emoticon/")
def delete_emoticon():
    emote = syndbb.request.args.get('file', '')
    uniqid = syndbb.request.args.get('uniqid', '')

    if uniqid:
        userid = checkSession(uniqid)
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            emotepath = syndbb.os.getcwd() + "/syndbb/static/data/emoticons/" + user.username + "/" + emote
            if syndbb.os.path.isfile(emotepath):
                syndbb.os.remove(emotepath)
                syndbb.flash('Emoticon deleted successfully.', 'success')
                return syndbb.redirect(syndbb.url_for('submit_emoticon'))
            else:
                syndbb.flash('No such emoticon exists.', 'danger')
                return syndbb.redirect(syndbb.url_for('submit_emoticon'))
        else:
            return "Invalid Session"
    else:
        return "Invalid Request"

@syndbb.app.route('/functions/upload_emoticon', methods=['GET', 'POST'])
def upload_emoticon():
    if syndbb.request.method == 'POST':
        if 'logged_in' in syndbb.session:
            userid = checkSession(str(syndbb.session['logged_in']))
            if userid:
                user = d2_user.query.filter_by(user_id=userid).first()
                uploadfolder = syndbb.os.getcwd() + "/syndbb/static/data/emoticons/" + user.username + "/"
                if 'file' not in syndbb.request.files:
                    syndbb.flash('No emoticon selected.', 'danger')
                    return syndbb.redirect(syndbb.url_for('submit_emoticon'))
                file = syndbb.request.files['file']
                file.seek(0, syndbb.os.SEEK_END)
                file_length = file.tell()
                extension = syndbb.os.path.splitext(file.filename)[1].lower()
                image_types = [".jpg", ".jpeg", ".jpe", ".gif", ".png"]
                if extension not in image_types:
                    syndbb.flash('Uploaded file is not an image.', 'danger')
                    return syndbb.redirect(syndbb.url_for('submit_emoticon'))
                if file_length > 65536:
                    syndbb.flash('Image is over 64kb.', 'danger')
                    return syndbb.redirect(syndbb.url_for('submit_emoticon'))
                img_res = Image.open(file)
                if img_res.size[0] > 100:
                    syndbb.flash('Image width is over 100px.', 'danger')
                    return syndbb.redirect(syndbb.url_for('submit_emoticon'))
                if img_res.size[1] > 32:
                    syndbb.flash('Image height is over 32px.', 'danger')
                    return syndbb.redirect(syndbb.url_for('submit_emoticon'))
                if file.filename == '':
                    syndbb.flash('No emoticon selected.', 'danger')
                    return syndbb.redirect(syndbb.url_for('submit_emoticon'))
                if file:
                    file.seek(0)
                    filename = secure_filename(file.filename)
                    file.save(syndbb.os.path.join(uploadfolder, filename))
                    syndbb.flash('Emoticon uploaded successfully.', 'success')
                    return syndbb.redirect(syndbb.url_for('submit_emoticon'))
        else:
            return "What are you doing?"
