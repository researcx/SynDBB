#
# Copyright (c) 2017 - 2020 Keira T (https://kei.info.gf). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb, random, string, hashlib, piexif, math
from PIL import Image
from syndbb.models.users import d2_user, check_session_by_id
from syndbb.models.time import cdn_path
from syndbb.models.d2_hash import d2_hash
from werkzeug.utils import secure_filename
from flask_paginate import Pagination
from flask import send_from_directory, make_response

@syndbb.cache.memoize(timeout=86400) # get_user_files
def get_user_files(userid, anon=0, gallery=0, album=0):
    user = d2_user.query.filter_by(user_id=userid).first()
    
    if anon:
        uname = d2_hash(user.username + user.password)[:10]
    else:
        uname = user.username
    
    uploadfolder = syndbb.app.static_folder + "/data/uploads/" + uname + "/"
    thumbfolder = syndbb.app.static_folder + "/data/uploads/.thumbnails/"

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
        uploadurl = cdn_path() + "/data/uploads/"
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
                if anon:
                    type_icon = '<i class="silk-icon icon_picture" aria-hidden="true"></i>'
                else:           
                    type_icon = '<img src="'+cdn_path()+'/data/uploads/.thumbnails/'+ hashname +'.png" alt="'+ fn +'" class="uploadimg"></a>'
                    thumbpath = thumbfolder + hashname + ".png"
                    if not syndbb.os.path.isfile(thumbpath):
                        im = Image.open(filepath)
                        im.thumbnail((150,150))
                        im.save(thumbpath, "PNG")
            elif extension in audio_types:
                type_icon = '<i class="fa fa-file-audio-o" aria-hidden="true"></i>'
            elif extension in video_types:
                type_icon = '<i class="ffa fa-file-video-o" aria-hidden="true"></i>'
            elif extension in text_types:
                type_icon = '<i class="fa fa-file-text-o" aria-hidden="true"></i>'
            elif extension in archive_types:
                type_icon = '<i class="fa fa-file-archive-o" aria-hidden="true"></i>'
            else:
                type_icon = '<i class="fa fa-file-o" aria-hidden="true"></i>'

            file_list.append([filetime, filesize, fn, type_icon])
            
    file_list.sort(reverse=True)
    
    return {'file_list': file_list, 'uploadurl': uploadurl, 'file_count': len(file_list), 'total_size': total_size, 'user_name': uname}
            

@syndbb.app.route("/upload/")
def upload():
    page = syndbb.request.args.get('page', type=int, default=1)
    per_page = syndbb.request.args.get('amount', type=int, default=25)
    dynamic_css_header = []
    dynamic_js_footer = ["js/bootstrap-filestyle.min.js", "js/bootbox.min.js", "js/delete.js", "js/lazyload.transpiled.min.js"]
    if 'logged_in' in syndbb.session:
        userid = check_session_by_id(str(syndbb.session['logged_in']))
        if userid:
            cached_list = get_user_files(userid)
            file_list = cached_list['file_list']
            
            page_count = math.ceil(len(file_list)/per_page)
            pagination = Pagination(page=page, per_page=per_page, css_framework='bootstrap3', total=len(file_list))

            amount_options = ["25", "50", "100", "500", "1000", "1500", "2000"]

            countselector = ''
            for amount in amount_options:
                if str(per_page) == amount:
                    countselector += '<option value="'+amount+'" selected>'+amount+'</option>'
                else:
                    countselector += '<option value="'+amount+'">'+amount+'</option>'

            start_index = (page*per_page) - per_page
            end_index = start_index + per_page
            if end_index > len(file_list):
                end_index = len(file_list)
            file_list = file_list[start_index:end_index]
            
            return syndbb.render_template('upload.html', uploadurl=cached_list['uploadurl'], filecount=cached_list['file_count'], file_list=file_list, pagination=pagination, countselector=countselector, uploader_name=cached_list['user_name'], total_size=cached_list['total_size'], dynamic_js_footer=dynamic_js_footer, dynamic_css_header=dynamic_css_header, title="Upload", subheading=[""])
        else:
            return syndbb.render_template('error_not_logged_in.html', title="Upload", subheading=[""])
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Upload", subheading=[""])

@syndbb.app.route("/upload/anonymous/")
def upload_anon():
    page = syndbb.request.args.get('page', type=int, default=1)
    per_page = syndbb.request.args.get('amount', type=int, default=25)
    dynamic_css_header = []
    dynamic_js_footer = ["js/bootstrap-filestyle.min.js", "js/bootbox.min.js", "js/delete.js", "js/lazyload.transpiled.min.js"]
    if 'logged_in' in syndbb.session:
        userid = check_session_by_id(str(syndbb.session['logged_in']))
        if userid:
            cached_list = get_user_files(userid, anon=1)
            file_list = cached_list['file_list']
            
            page_count = math.ceil(len(file_list)/per_page)
            pagination = Pagination(page=page, per_page=per_page, css_framework='bootstrap3', total=len(file_list))

            amount_options = ["25", "50", "100", "500", "1000", "1500", "2000"]

            countselector = ''
            for amount in amount_options:
                if str(per_page) == amount:
                    countselector += '<option value="'+amount+'" selected>'+amount+'</option>'
                else:
                    countselector += '<option value="'+amount+'">'+amount+'</option>'

            start_index = (page*per_page) - per_page
            end_index = start_index + per_page
            if end_index > len(file_list):
                end_index = len(file_list)
            file_list = file_list[start_index:end_index]
            
            return syndbb.render_template('upload_anon.html', uploadurl=cached_list['uploadurl'], filecount=cached_list['file_count'], file_list=file_list, pagination=pagination, countselector=countselector, total_size=cached_list['total_size'], uploader_name=cached_list['user_name'], dynamic_js_footer=dynamic_js_footer, dynamic_css_header=dynamic_css_header, title="Anonymous Upload", subheading=['<a href="/upload/">Upload</a>'])
        else:
            return syndbb.render_template('error_not_logged_in.html', title="Anonymous Upload", subheading=['<a href="/upload/">Upload</a>'])
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Upload", subheading=[""])
      
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
                uploadurl = cdn_path() + "/data/uploads/" + user.username + "/"
            else:
                uploadurl = "https://" + uploadurl + "/" + user.username + "/"

            images = []
            for image in file_list:
                extension = syndbb.os.path.splitext(image)[1].lower()
                if extension in image_types:
                    images.append(image)

            return syndbb.render_template('upload_album.html', filecount=len(images), uploadurl=uploadurl, file_list=images, dynamic_js_footer=dynamic_js_footer, title=user.username + " &bull; Album", subheading=[""])
        else:
            return syndbb.render_template('invalid.html', title="Upload &bull; Gallery", subheading=[""])
    else:
        return syndbb.render_template('invalid.html', title="Upload &bull; Gallery", subheading=[""])

@syndbb.app.route("/upload/gallery/")
def upload_gallery():
    dynamic_js_footer = ["js/bootstrap-filestyle.min.js", "js/uploadgallery.js", "js/bootbox.min.js", "js/delete.js", "js/lazyload.transpiled.min.js"]
    if 'logged_in' in syndbb.session:
        userid = check_session_by_id(str(syndbb.session['logged_in']))
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            uploadfolder = syndbb.app.static_folder + "/data/uploads/" + user.username + "/"
            thumbfolder = syndbb.app.static_folder + "/data/uploads/.thumbnails/"

            if not syndbb.os.path.exists(uploadfolder):
                syndbb.os.makedirs(uploadfolder)
            if not syndbb.os.path.exists(thumbfolder):
                syndbb.os.makedirs(thumbfolder)

            image_types = [".jpg", ".jpeg", ".jpe", ".gif", ".png", ".bmp"]
            total_size = sum(syndbb.os.path.getsize(uploadfolder+f) for f in syndbb.os.listdir(uploadfolder) if syndbb.os.path.isfile(uploadfolder+f) and syndbb.os.path.splitext(f)[1].lower() in image_types)

            uploadurl = user.upload_url
            if uploadurl == "local":
                uploadurl = str(cdn_path) + "/data/uploads/" 
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
                        type_icon = cdn_path() + '/data/uploads/.thumbnails/'+ hashname + '.png'
                        thumbpath = thumbfolder + hashname + ".png"
                        if not syndbb.os.path.isfile(thumbpath):
                            im = Image.open(filepath)
                            im.thumbnail((150,150))
                            im.save(thumbpath, "PNG")
                        file_list.append([filetime, filesize, fn, type_icon])
            file_list.sort(reverse=True)

            return syndbb.render_template('upload_gallery.html', uploadurl=uploadurl, filecount=len(file_list), file_list=file_list, total_size=total_size, dynamic_js_footer=dynamic_js_footer, title="Upload &bull; Gallery", subheading=[""])
        else:
            return syndbb.render_template('error_not_logged_in.html', title="Upload &bull; Gallery", subheading=[""])
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Upload &bull; Gallery", subheading=[""])

@syndbb.app.route("/upload/simple/")
def upload_simple():
    if 'logged_in' in syndbb.session:
        userid = check_session_by_id(str(syndbb.session['logged_in']))
        if userid:
            dynamic_js_footer = ["js/bootstrap-filestyle.min.js", "js/bootbox.min.js", "js/delete.js", "js/lazyload.transpiled.min.js"]
            user = d2_user.query.filter_by(user_id=userid).first()
            uploadfolder = syndbb.app.static_folder + "/data/uploads/" + user.username + "/"
            thumbfolder = syndbb.app.static_folder + "/data/uploads/.thumbnails/"
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
                    uploadurl = cdn_path() + "/data/uploads/"
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
                        type_icon = '<img src="'+cdn_path()+'/data/uploads/.thumbnails/'+ hashname +'.png" alt="'+ ufile +'" class="uploadimg"></a>'
                        thumbpath = thumbfolder + hashname + ".png"
                        if not syndbb.os.path.isfile(thumbpath):
                            im = Image.open(filepath)
                            im.thumbnail((150,150))
                            im.save(thumbpath, "PNG")
                        file_list.append([filetime, filesize, ufile, type_icon])
                return syndbb.render_template('upload_simple.html', uploadurl=uploadurl, file_list=file_list, dynamic_js_footer=dynamic_js_footer, title="Upload", subheading=[""])
            else:
                return syndbb.render_template('upload_simple.html', dynamic_js_footer=dynamic_js_footer, title="Upload", subheading=[""])
        else:
            return syndbb.render_template('error_not_logged_in.html', title="Upload", subheading=[""])
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Upload", subheading=[""])
    
@syndbb.app.route("/upload/view")
def upload_viewer():
    dynamic_js_footer = ["js/bootstrap-filestyle.min.js", "js/bootbox.min.js", "js/delete.js", "js/lazyload.transpiled.min.js"]
    ufile = syndbb.request.args.get('file', '')
    uploadfolder = syndbb.app.static_folder + "/data/uploads/"

    if ufile:
        image_types = [".jpg", ".jpeg", ".jpe", ".gif", ".png", ".bmp"]
        audio_types = [".mp3",".ogg",".wav"]
        video_types = [".webm",".mp4",".avi",".mpg",".mpeg"]
        text_types = [".txt",".pdf",".doc"]
        archive_types = [".zip",".rar",".7z",".tar",".gz"]
        
        uploadurl = cdn_path() + "/data/uploads/"
        
        uploaduser = ufile.split('/')[0]
        uploadfile = ufile.split('/')[1]
        
        user = d2_user.query.filter_by(username=uploaduser).first()
        
        if user:
            if 'logged_in' in syndbb.session:
                userid = check_session_by_id(str(syndbb.session['logged_in']))
                user = d2_user.query.filter_by(user_id=userid).first()

                uploadurl = user.upload_url
                if uploadurl == "local":
                    uploadurl = cdn_path() + "/data/uploads/"
                else:
                    uploadurl = "https://" + uploadurl + "/"
            else:
                uploadurl = cdn_path() + "/data/uploads/"
        else:
            uploadurl = cdn_path() + "/data/uploads/"
                    
        file_list = []
        filepath = uploadfolder + "/" + ufile
        if syndbb.os.path.isfile(filepath):
            type_icon = ''
            filetime = int(syndbb.os.stat(filepath).st_mtime)
            filesize = syndbb.os.path.getsize(filepath)
            extension = syndbb.os.path.splitext(ufile)[1].lower()
            hashname = hashlib.sha256(ufile.encode()).hexdigest()
            if extension in image_types:
                type_icon = '<img src="'+ uploadurl + ufile +'" alt="'+ ufile +'" class="bbcode-image img-thumb"\>'
            elif extension in audio_types:
                type_icon = '<i class="fa fa-file-audio-o" aria-hidden="true"></i><div style="margin-top: -0.8em;"><audio controls><source src="'+ uploadurl + ufile +'" type="audio/mpeg"></audio></div>'
            elif extension in video_types:
                type_icon = '<video width="720" height="480" controls><source src="'+ uploadurl + ufile +'" type="video/mp4"></video>'
            elif extension in text_types:
                type_icon = '<i class="fa fa-file-text-o" aria-hidden="true"></i>'
            elif extension in archive_types:
                type_icon = '<i class="fa fa-file-archive-o" aria-hidden="true"></i>'
            else:
                type_icon = '<i class="fa fa-file-o" aria-hidden="true"></i>'
                
            file_list.append([filetime, filesize, ufile, type_icon])
        return syndbb.render_template('upload_viewer.html', uploadurl=uploadurl, file_list=file_list, dynamic_js_footer=dynamic_js_footer, title=ufile, subheading=["Upload"])
    else:
        return syndbb.render_template('upload_viewer.html', dynamic_js_footer=dynamic_js_footer, title="View File", subheading=["Upload"])

# ShareX Script
@syndbb.app.route("/upload/sharex")
@syndbb.cache.memoize(timeout=86400) # provide_sharex_script
def provide_sharex_script():
    template = syndbb.render_template('sharex.json')
    response = make_response(template)
    response.headers['Content-Type'] = 'application/json'
    return response

# Bash Script
@syndbb.app.route("/upload/bash")
@syndbb.cache.memoize(timeout=86400) # provide_bash_script
def provide_bash_script():
    template = syndbb.render_template('bash-upload.sh')
    response = make_response(template)
    response.headers['Content-Type'] = 'text/plain'
    return response


@syndbb.app.route('/functions/upload', methods=['GET', 'POST'])
def upload_file():
    if syndbb.request.method == 'POST':
        image_types = [".jpg", ".jpeg", ".jpe"]
        if 'logged_in' in syndbb.session:
            userid = check_session_by_id(str(syndbb.session['logged_in']))
            uploader = syndbb.request.form['uploader']
            
            if 'anonymous' in syndbb.request.form:
                anonymous = 1
            else:
                anonymous = 0
                
            if 'timedelete' in syndbb.request.form:
                timedelete = 1
            else:
                timedelete = 0
            
            if userid:
                user = d2_user.query.filter_by(user_id=userid).first()
                if anonymous:
                  uploadfolder = syndbb.app.static_folder + "/data/uploads/" + d2_hash(user.username + user.password)[:10] + "/"
                else:
                  uploadfolder = syndbb.app.static_folder + "/data/uploads/" + user.username + "/"
                if not syndbb.os.path.exists(uploadfolder):
                  syndbb.os.makedirs(uploadfolder)
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
                        syndbb.cache.delete_memoized(syndbb.views.upload.get_user_files)
                        
                        if anonymous:
                            fpath = d2_hash(user.username + user.password)[:10] + "/" + newname
                        else:
                            fpath = user.username + "/" + newname

                        return syndbb.redirect('/upload/view?file='+fpath)

@syndbb.app.route('/functions/upload/external', methods=['GET', 'POST'])
def upload_file_external():
    if syndbb.request.method == 'POST':
        image_types = [".jpg", ".jpeg", ".jpe"]
        username = syndbb.request.form['username']
        if 'auth' in syndbb.request.form:
            password = syndbb.request.form['auth']
        elif 'password' in syndbb.request.form:
            password = syndbb.request.form['password']
        else:
            return "No password set."
        user = d2_user.query.filter_by(username=username).filter_by(upload_auth=password).first()
        if user:
#            ban_check = check_ban_by_id(user.user_id)
#            if ban_check:
#                return "This user or IP address is banned."
            uploadfolder = syndbb.app.static_folder + "/data/uploads/" + user.username + "/"
            if not syndbb.os.path.exists(uploadfolder):
                syndbb.os.makedirs(uploadfolder)
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
                    uploadurl = cdn_path() + "/data/uploads/" + user.username + "/" + newname
                else:
                    uploadurl = "https://" + uploadurl + "/" + user.username + "/" + newname
                syndbb.cache.delete_memoized(syndbb.views.upload.get_user_files)

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
        userid = check_session_by_id(str(uniqid))
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            if uploader == "upload_anon":
                uploaded_file = syndbb.app.static_folder + "/data/uploads/" + d2_hash(user.username + user.password)[:10] + "/" + ufile
            else:
                uploaded_file = syndbb.app.static_folder + "/data/uploads/" + user.username + "/" + ufile
            if syndbb.os.path.isfile(uploaded_file):
                syndbb.os.system("shred -u "+uploaded_file)
                syndbb.flash('File deleted successfully.', 'success')
                syndbb.cache.delete_memoized(syndbb.views.upload.get_user_files)
                return syndbb.redirect(syndbb.url_for(uploader))
            else:
                syndbb.flash('No such file exists.', 'danger')
                return syndbb.redirect(syndbb.url_for(uploader))
        else:
            return syndbb.render_template('error_not_logged_in.html', title="Upload")
    else:
        return syndbb.render_template('error_not_logged_in.html', title="Upload")
