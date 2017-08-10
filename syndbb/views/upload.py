#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb, random, string, hashlib, piexif
from PIL import Image
from syndbb.models.users import d2_user, d2_session, checkSession
from werkzeug.utils import secure_filename

@syndbb.app.route("/upload/")
def upload():
    dynamic_js_footer = ["js/bootstrap-filestyle.min.js", "js/bootbox.min.js", "js/delete.js", "js/lazyload.transpiled.min.js"]
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(syndbb.session['logged_in']))
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            uploadfolder = syndbb.os.getcwd() + "/syndbb/static/data/uploads/" + user.username + "/"
            thumbfolder = syndbb.os.getcwd() + "/syndbb/static/data/uploads/.thumbnails/"

            if not syndbb.os.path.exists(uploadfolder):
                syndbb.os.makedirs(uploadfolder)
            if not syndbb.os.path.exists(thumbfolder):
                syndbb.os.makedirs(thumbfolder)

            image_types = [".jpg", ".jpeg", ".jpe", ".gif", ".png", ".bmp"]
            audio_types = [".mp3",".ogg",".wav"]
            video_types = [".webm",".mp4",".avi",".mpg",".mpeg"]
            text_types = [".txt",".pdf",".doc"]
            archive_types = [".zip",".rar",".7z",".tar",".gz"]

            total_size = sum(syndbb.os.path.getsize(uploadfolder+f) for f in syndbb.os.listdir(uploadfolder) if syndbb.os.path.isfile(uploadfolder+f))

            uploadurl = user.upload_url
            if uploadurl == "local":
                uploadurl = syndbb.request.url_root + "static/data/uploads/"
            else:
                uploadurl = "https://" + uploadurl + "/"

            file_list = []
            for fn in syndbb.os.listdir(uploadfolder):
                filepath = uploadfolder + "/" + fn
                if syndbb.os.path.isfile(filepath):
                    filetime = int(syndbb.os.stat(filepath).st_mtime)
                    filesize = syndbb.os.path.getsize(filepath)
                    extension = syndbb.os.path.splitext(fn)[1].lower()
                    hashname = hashlib.sha256(fn.encode()).hexdigest()
                    if extension in image_types:
                        type_icon = '<img src="#" data-original="/static/data/uploads/.thumbnails/'+ hashname +'.png" alt="'+ fn +'" class="uploadimg"></a>'
                        thumbpath = thumbfolder + hashname + ".png"
                        if not syndbb.os.path.isfile(thumbpath):
                            im = Image.open(filepath)
                            im.thumbnail((150,150))
                            im.save(thumbpath, "PNG")
                    elif extension in audio_types:
                        type_icon = '<i class="fa fa-file-audio-o" aria-hidden="true"></i>'
                    elif extension in video_types:
                        type_icon = '<i class="fa fa-file-video-o" aria-hidden="true"></i>'
                    elif extension in text_types:
                        type_icon = '<i class="fa fa-file-text-o" aria-hidden="true"></i>'
                    elif extension in archive_types:
                        type_icon = '<i class="fa fa-file-archive-o" aria-hidden="true"></i>'
                    else:
                        type_icon = '<i class="fa fa-file-o" aria-hidden="true"></i>'

                    file_list.append([filetime, filesize, fn, type_icon])
            file_list.sort(reverse=True)

            return syndbb.render_template('upload.html', uploadurl=uploadurl, filecount=len(file_list), file_list=file_list, total_size=total_size, dynamic_js_footer=dynamic_js_footer, title="Upload")
        else:
            return syndbb.render_template('error_not_logged_in.html', title="Upload")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Upload")

@syndbb.app.route("/upload/album/")
def upload_album():
    uname = syndbb.request.args.get('u', '')
    file_list = syndbb.request.args.get('i', '').split(";")
    image_types = [".jpg", ".jpeg", ".jpe", ".gif", ".png", ".bmp"]
    dynamic_js_footer = ["js/bootbox.min.js", "js/delete.js", "js/lazyload.transpiled.min.js"]

    if uname and file_list:
        user = d2_user.query.filter_by(username=uname).first()
        if user:
            uploadurl = user.upload_url
            if uploadurl == "local":
                uploadurl = syndbb.request.url_root + "static/data/uploads/" + user.username + "/"
            else:
                uploadurl = "https://" + uploadurl + "/" + user.username + "/"

            images = []
            for image in file_list:
                extension = syndbb.os.path.splitext(image)[1].lower()
                if extension in image_types:
                    images.append(image)

            return syndbb.render_template('upload_album.html', filecount=len(images), uploadurl=uploadurl, file_list=images, dynamic_js_footer=dynamic_js_footer, title=user.username + " &bull; Album")
        else:
            return syndbb.render_template('invalid.html', title="Upload &bull; Gallery")
    else:
        return syndbb.render_template('invalid.html', title="Upload &bull; Gallery")

@syndbb.app.route("/upload/gallery/")
def upload_gallery():
    dynamic_js_footer = ["js/bootstrap-filestyle.min.js", "js/uploadgallery.js", "js/bootbox.min.js", "js/delete.js", "js/lazyload.transpiled.min.js"]
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(syndbb.session['logged_in']))
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            uploadfolder = syndbb.os.getcwd() + "/syndbb/static/data/uploads/" + user.username + "/"
            thumbfolder = syndbb.os.getcwd() + "/syndbb/static/data/uploads/.thumbnails/"

            if not syndbb.os.path.exists(uploadfolder):
                syndbb.os.makedirs(uploadfolder)
            if not syndbb.os.path.exists(thumbfolder):
                syndbb.os.makedirs(thumbfolder)

            image_types = [".jpg", ".jpeg", ".jpe", ".gif", ".png", ".bmp"]
            total_size = sum(syndbb.os.path.getsize(uploadfolder+f) for f in syndbb.os.listdir(uploadfolder) if syndbb.os.path.isfile(uploadfolder+f) and syndbb.os.path.splitext(f)[1].lower() in image_types)

            uploadurl = user.upload_url
            if uploadurl == "local":
                uploadurl = syndbb.request.url_root + "static/data/uploads/"
            else:
                uploadurl = "https://" + uploadurl + "/"

            file_list = []
            for fn in syndbb.os.listdir(uploadfolder):
                filepath = uploadfolder + "/" + fn
                if syndbb.os.path.isfile(filepath):
                    filetime = int(syndbb.os.stat(filepath).st_mtime)
                    filesize = syndbb.os.path.getsize(filepath)
                    extension = syndbb.os.path.splitext(fn)[1].lower()
                    hashname = hashlib.sha256(fn.encode()).hexdigest()
                    if extension in image_types:
                        type_icon = '/static/data/uploads/.thumbnails/'+ hashname + '.png'
                        thumbpath = thumbfolder + hashname + ".png"
                        if not syndbb.os.path.isfile(thumbpath):
                            im = Image.open(filepath)
                            im.thumbnail((150,150))
                            im.save(thumbpath, "PNG")
                        file_list.append([filetime, filesize, fn, type_icon])
            file_list.sort(reverse=True)

            return syndbb.render_template('upload_gallery.html', uploadurl=uploadurl, filecount=len(file_list), file_list=file_list, total_size=total_size, dynamic_js_footer=dynamic_js_footer, title="Upload &bull; Gallery")
        else:
            return syndbb.render_template('error_not_logged_in.html', title="Upload &bull; Gallery")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Upload &bull; Gallery")

@syndbb.app.route("/upload/simple/")
def upload_simple():
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(syndbb.session['logged_in']))
        if userid:
            dynamic_js_footer = ["js/bootstrap-filestyle.min.js", "js/bootbox.min.js", "js/delete.js", "js/lazyload.transpiled.min.js"]
            user = d2_user.query.filter_by(user_id=userid).first()
            uploadfolder = syndbb.os.getcwd() + "/syndbb/static/data/uploads/" + user.username + "/"
            thumbfolder = syndbb.os.getcwd() + "/syndbb/static/data/uploads/.thumbnails/"
            ufile = syndbb.request.args.get('file', '')

            if not syndbb.os.path.exists(uploadfolder):
                syndbb.os.makedirs(uploadfolder)
            if not syndbb.os.path.exists(thumbfolder):
                syndbb.os.makedirs(thumbfolder)

            if ufile:
                image_types = [".jpg", ".jpeg", ".jpe", ".gif", ".png", ".bmp"]
                audio_types = [".mp3",".ogg",".wav"]
                video_types = [".webm",".mp4",".avi",".mpg",".mpeg"]
                text_types = [".txt",".pdf",".doc"]
                archive_types = [".zip",".rar",".7z",".tar",".gz"]

                uploadurl = user.upload_url
                if uploadurl == "local":
                    uploadurl = syndbb.request.url_root + "static/data/uploads/"
                else:
                    uploadurl = "https://" + uploadurl + "/"

                file_list = []
                filepath = uploadfolder + "/" + ufile
                if syndbb.os.path.isfile(filepath):
                    filetime = int(syndbb.os.stat(filepath).st_mtime)
                    filesize = syndbb.os.path.getsize(filepath)
                    extension = syndbb.os.path.splitext(ufile)[1].lower()
                    hashname = hashlib.sha256(ufile.encode()).hexdigest()
                    if extension in image_types:
                        type_icon = '<img src="/static/data/uploads/.thumbnails/'+ hashname +'.png" alt="'+ ufile +'" class="uploadimg"></a>'
                        thumbpath = thumbfolder + hashname + ".png"
                        if not syndbb.os.path.isfile(thumbpath):
                            im = Image.open(filepath)
                            im.thumbnail((150,150))
                            im.save(thumbpath, "PNG")
                        file_list.append([filetime, filesize, ufile, type_icon])
                return syndbb.render_template('upload_simple.html', uploadurl=uploadurl, file_list=file_list, dynamic_js_footer=dynamic_js_footer, title="Upload")
            else:
                return syndbb.render_template('upload_simple.html', dynamic_js_footer=dynamic_js_footer, title="Upload")
        else:
            return syndbb.render_template('error_not_logged_in.html', title="Upload")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Upload")

@syndbb.app.route('/functions/upload', methods=['GET', 'POST'])
def upload_file():
    if syndbb.request.method == 'POST':
        image_types = [".jpg", ".jpeg", ".jpe"]
        if 'logged_in' in syndbb.session:
            userid = checkSession(str(syndbb.session['logged_in']))
            uploader = syndbb.request.form['uploader']
            if userid:
                user = d2_user.query.filter_by(user_id=userid).first()
                uploadfolder = syndbb.os.getcwd() + "/syndbb/static/data/uploads/" + user.username + "/"
                if 'file' not in syndbb.request.files:
                    syndbb.flash('No file selected.', 'danger')
                    return syndbb.redirect(syndbb.url_for(uploader))
                file = syndbb.request.files['file']
                if file.filename == '':
                    syndbb.flash('No file selected.', 'danger')
                    return syndbb.redirect(syndbb.url_for(uploader))
                if file:
                    filename = secure_filename(file.filename)
                    extension = syndbb.os.path.splitext(filename)[1]
                    newname = ''.join(random.sample("-_"+string.ascii_uppercase+string.ascii_lowercase+string.digits,20)) + extension
                    file.save(syndbb.os.path.join(uploadfolder, newname))
                    if extension in image_types:
                        piexif.remove(uploadfolder + newname)
                    if uploader == 'upload_simple':
                        return "/upload/simple/?file=" + newname
                    else:
                        syndbb.flash('File uploaded successfully.', 'success')
                        return syndbb.redirect(syndbb.url_for(uploader))

@syndbb.app.route('/functions/upload/external', methods=['GET', 'POST'])
def upload_file_external():
    if syndbb.request.method == 'POST':
        image_types = [".jpg", ".jpeg", ".jpe"]
        username = syndbb.request.form['username']
        password = syndbb.request.form['password']
        user = d2_user.query.filter_by(username=username).filter_by(uploadauth=password).first()
        if user:
            uploadfolder = syndbb.os.getcwd() + "/syndbb/static/data/uploads/" + user.username + "/"
            if 'file' not in syndbb.request.files:
                return "No file selected."
            file = syndbb.request.files['file']
            if file.filename == '':
                return "No file selected."
            if file:
                filename = secure_filename(file.filename)
                extension = syndbb.os.path.splitext(filename)[1]
                newname = ''.join(random.sample("-_"+string.ascii_uppercase+string.ascii_lowercase+string.digits,20)) + extension
                file.save(syndbb.os.path.join(uploadfolder, newname))
                if extension in image_types:
                    piexif.remove(uploadfolder + newname)

                uploadurl = user.upload_url
                if uploadurl == "local":
                    uploadurl = syndbb.request.url_root + "static/data/uploads/" + user.username + "/" + newname
                else:
                    uploadurl = "https://" + uploadurl + "/" + user.username + "/" + newname

                return uploadurl
        else:
            return "Invalid details or not logged in."
    else:
        return "Invalid request, must be POST."

@syndbb.app.route('/functions/delete_file')
def delete_file():
    ufile = syndbb.request.args.get('file', '')
    uniqid = syndbb.request.args.get('uniqid', '')
    uploader = syndbb.request.args.get('uploader', '')
    if 'logged_in' in syndbb.session:
        userid = checkSession(str(uniqid))
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            uploaded_file = syndbb.os.getcwd() + "/syndbb/static/data/uploads/" + user.username + "/" + ufile
            if syndbb.os.path.isfile(uploaded_file):
                syndbb.os.system("shred -u "+uploaded_file)
                syndbb.flash('File deleted successfully.', 'success')
                return syndbb.redirect(syndbb.url_for(uploader))
            else:
                syndbb.flash('No such file exists.', 'danger')
                return syndbb.redirect(syndbb.url_for(uploader))
        else:
            return syndbb.render_template('error_not_logged_in.html', title="Upload")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Upload")
