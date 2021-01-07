#
# Copyright (c) 2017 - 2020 Keira T (https://kei.info.gf). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb
from syndbb.models.users import d2_user, check_session_by_id

@syndbb.cache.memoize(timeout=86400) # get_emote
def get_emote():
    emotfolder = syndbb.app.static_folder + "/images/emots/"

    emote_list = []
    for emote in syndbb.os.listdir(emotfolder):
        filepath = emotfolder + "/" + emote
        if syndbb.os.path.isfile(filepath):
            addtime = int(syndbb.os.stat(filepath).st_mtime)
            code = ":" + syndbb.os.path.splitext(emote)[0] + ":"
            emote_list.append([emote, code])
    emote_list.sort(reverse=False)
    return emote_list

@syndbb.cache.memoize(timeout=86400) # get_submitted_emote
def get_submitted_emote():
    emote_list = []
    if 'logged_in' in syndbb.session:
        userid = check_session_by_id(str(syndbb.session['logged_in']))
        if userid:
            user = d2_user.query.filter_by(user_id=userid).first()
            emotfolder = syndbb.app.static_folder + "/data/emoticons/" + user.username + "/"

            if not syndbb.os.path.exists(emotfolder):
                syndbb.os.makedirs(emotfolder)

            for emote in syndbb.os.listdir(emotfolder):
                filepath = emotfolder + "/" + emote
                if syndbb.os.path.isfile(filepath):
                    addtime = int(syndbb.os.stat(filepath).st_mtime)
                    code = ":" + syndbb.os.path.splitext(emote)[0] + ":"
                    emote_list.append([emote, code])
            emote_list.sort(reverse=False)
    return emote_list
