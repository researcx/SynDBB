#
# Copyright (c) 2017 - 2020 Keira T (https://kei.info.gf). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb, json, requests, urllib.parse
from PIL import Image, ImageOps
from io import BytesIO
from operator import itemgetter
from syndbb.models.get_emote import get_emote
from syndbb.models.users import d2_user, get_group_style_by_id, check_session_by_id, get_rank_by_id, get_title_by_rank
from syndbb.models.time import cdn_path
import syndbb.models.bbcode

### General Functions ###
@syndbb.app.context_processor
def get_channel_data(category=None):
    channelcheck = d2_channels.query.filter_by(short_name=category).first()
    if channelcheck:
        return channelcheck
    return []

@syndbb.app.context_processor
@syndbb.cache.memoize(timeout=86400) #get_thread_contents
def get_thread_contents(thread=None):
    threadcheck = d2_activity.query.filter_by(id=thread).first()
    if threadcheck:
        return threadcheck
    return []

@syndbb.app.context_processor
@syndbb.cache.memoize(timeout=86400) #get_thread_list
def get_thread_list(category=None):
    threads = d2_activity.query.filter_by(category=category).order_by(d2_activity.reply_time.desc()).all()
    if threads:
        return threads
    return []


#Channel list
@syndbb.app.context_processor
@syndbb.cache.memoize(timeout=86400) # inject_channels
def inject_channels():
    channels = d2_channels.query.filter_by(approved='1', owned_by='0', nsfw='0').all()
    if channels:
        return {'channels': channels}
    return {'channels': ''}

#Community Channel List
@syndbb.app.context_processor
@syndbb.cache.memoize(timeout=86400) # inject_custom_channels
def inject_custom_channels():
    channels = d2_channels.query.filter(d2_channels.owned_by != '0').filter(d2_channels.approved == '1').all()
    if channels:
        return {'custom_channels': channels}
    return {'custom_channels': ''}

#NSFW Channel List
@syndbb.app.context_processor
@syndbb.cache.memoize(timeout=86400) # inject_nsfw_channels
def inject_nsfw_channels():
    channels = d2_channels.query.filter(d2_channels.nsfw == '1').filter(d2_channels.approved == '1').all()
    if channels:
        return {'nsfw_channels': channels}
    return {'nsfw_channels': ''}

#Get post icons
@syndbb.cache.memoize(timeout=86400) # get_post_icons
def get_post_icons(whitelist):
    iconfolder = syndbb.app.static_folder + "/images/posticons/"
    picon_list = []
    if whitelist:
        allowed_icons = ['art', 'attention', 'banme', 'computers', 'en', 'event', 'fap', 'funny', 'gaming', 'gross', 'help', 'hot', 'letsplay', 'link', 'music', 'newbie', 'news', 'photos', 'politics', 'poll', 'postyour', 'question', 'rant', 'release', 'repeat', 'request', 'school', 'serious', 'shitpost', 'stupid', 'tv', 'unfunny', 'weird', 'whine']
        for picon in allowed_icons:
            filename = picon+".png"
            filepath = iconfolder + "/" + filename
            if syndbb.os.path.isfile(filepath):
                picon_list.append([filename, picon])
    else:
        for picon in syndbb.os.listdir(iconfolder):
            filepath = iconfolder + "/" + picon
            if syndbb.os.path.isfile(filepath):
                code = syndbb.os.path.splitext(picon)[0]
                picon_list.append([picon, code])
                
    picon_list.sort(reverse=False)
    return picon_list
syndbb.app.jinja_env.globals.update(get_post_icons=get_post_icons)

def check_channel_auth(channel):
    rank_access = 1
    username_access = 0
    if ('logged_in' in syndbb.session) and (get_rank_by_id(check_session_by_id(syndbb.session['logged_in'])) < channel.auth):
        rank_access = 0
    if not ('logged_in' in syndbb.session) and channel.auth >= 1:
        rank_access = 0
    if channel.user_list and channel.user_list != "":
        access_list = channel.user_list.split(" ")
        if len(access_list) >= 1 and ('logged_in' in syndbb.session and check_session_by_id(str(syndbb.session['logged_in']))):
            user = d2_user.query.filter_by(user_id=check_session_by_id(str(syndbb.session['logged_in']))).first()
            if user.username in access_list:
                username_access = 1
            else:
                username_access = 0
        else:
            username_access = 0
    if username_access and not rank_access:
        return 0
    if rank_access or username_access:
        return 1

@syndbb.cache.memoize(timeout=86400) # get_post_thumbnail
def get_post_thumbnail(id, method="crop", recheck=False):
    timg = cdn_path() + "/images/noimage-grid.png"
    link = timg
    thumbfolder = syndbb.app.static_folder + "/data/threadimg/grid/"
    post = d2_activity.query.filter_by(id=id).first()
    if post:
        hashname = str(post.id)+"-"+method
        thumbpath = thumbfolder + hashname + ".png"  

        lists = ["(?<=\[img\]).*?(?=\[/img\])", "(?<=\[t\]).*?(?=\[/t\])", "(?<=\[ct\]).*?(?=\[/ct\])"]            
        for type in lists:
            images = syndbb.re.findall(type, post.content, syndbb.re.IGNORECASE)
            if images:
                    if method == "imageboard-thumb":
                        timg = syndbb.os.path.splitext(images[0])[0]+"s.jpg"
                        link = images[0]
                        return {'src': timg, 'href': link}
                    if method == "imageboard-source":
                        link = images[0]
                        return {'src': link, 'href': link}
                    if syndbb.os.path.isfile(thumbpath):
                        timg = cdn_path() + "/data/threadimg/grid/" + hashname + ".png"
                        link = images[0]
                        return {'src': timg, 'href': link}
                    if not syndbb.os.path.isfile(thumbpath):
                        threadimg = requests.get(images[0], verify=False, timeout=5)
                        try:
                            im = Image.open(BytesIO(threadimg.content))
                            if method == "crop":
                                im = ImageOps.fit(im, (150, 150),  Image.ANTIALIAS)
                            elif method == "resize":
                                im.thumbnail((195, 195), Image.ANTIALIAS)
                            im.save(thumbpath, "PNG")
                        except:
                            pass
                        timg = cdn_path() + "/data/threadimg/grid/" + hashname + ".png"
                        link = images[0]
                        return {'src': timg, 'href': link}

    return {'src': timg, 'href': link}
syndbb.app.jinja_env.globals.update(get_post_thumbnail=get_post_thumbnail)

# #Channel icons
# @syndbb.app.template_filter('get_channel_logo')
# @syndbb.cache.memoize(timeout=60) # get_channel_logo
# def get_channel_logo(short_name):
#     channel_icon = '/images/logos/{}.png'.format(short_name)
#     channel_icon_default = '/images/logos/blank.png'
#     root_path = syndbb.app.static_folder
#
#     if syndbb.os.path.isfile(root_path+channel_icon):
#         return cdn_path() + channel_icon
#     else:
#         return cdn_path() + channel_icon_default
# syndbb.app.jinja_env.globals.update(get_channel_logo=get_channel_logo)
#
# #Channel icons 2
# @syndbb.app.template_filter('get_channel_icon')
# @syndbb.cache.memoize(timeout=60) # get_channel_icon
# def get_channel_icon(short_name):
#     channel_icon = '/images/channelicons/{}.png'.format(short_name)
#     channel_icon_default = '/images/channelicons/blank.png'
#     root_path = syndbb.app.static_folder
#
#     if syndbb.os.path.isfile(root_path+channel_icon):
#         return cdn_path() + channel_icon
#     else:
#         return cdn_path() + channel_icon_default
# syndbb.app.jinja_env.globals.update(get_channel_icon=get_channel_icon)

#Reply IDs for a post
@syndbb.app.template_filter('replies_to_post')
@syndbb.cache.memoize(timeout=86400) # replies_to_post
def replies_to_post(post_id):
    replies = d2_activity.query.filter_by(replyToPost=post_id).all()
    if replies:
        return replies
    else:
        return False
syndbb.app.jinja_env.globals.update(replies_to_post=replies_to_post)

#Get post rating
@syndbb.app.template_filter('get_post_rating')
@syndbb.cache.memoize(timeout=86400) # get_post_rating
def get_post_rating(post_id):
    ratings = d2_post_ratings.query.filter_by(post_id=post_id).all()

    final_count = 0
    for rating in ratings:
        final_count = final_count + rating.type
    return final_count
syndbb.app.jinja_env.globals.update(get_post_rating=get_post_rating)

#Parse channel BBCode
@syndbb.app.template_filter('parse_bbcode')
@syndbb.cache.memoize(timeout=86400) # parse_bbcode
def parse_bbcode(text):
    # Do the bbcode parsing
    if not text: return "NO TEXT"
    text = syndbb.models.bbcode.parser.format(text)
    # Get @usernames and turn them into links
    postname = syndbb.re.findall('(@\w+)', text, syndbb.re.IGNORECASE)
    for user in postname:
        highlighted_user = user[1:]
        d2user = d2_user.query.filter_by(username=highlighted_user).first()
        if d2user:
            user_link = '<a href="/user/'+d2user.username+'" class="username '+get_group_style_by_id(d2user.user_id)+' link-postname profile-inline">'+d2user.username+'</a>'
            text = syndbb.re.sub(user, user_link, text)
    # Add in emotes
    for k, v in get_emote():
        text = text.replace(v, '<img src="'+cdn_path()+'/images/emots/'+k+'" alt="'+k+'" title="'+v+'" class="emoticon" />')
    return text
syndbb.app.jinja_env.globals.update(parse_bbcode=parse_bbcode)

#Get channel info
@syndbb.app.template_filter('get_channel_list')
@syndbb.cache.memoize(timeout=86400) # get_channel_list
def get_channel_list(type):
    channels = []
    chlist = ""
    if type == 0:
        channel_list = d2_channels.query.filter_by(owned_by=0,nsfw=0,approved=1).all()
    elif type == 1:
        channel_list = d2_channels.query.filter(d2_channels.nsfw != 0).filter(d2_channels.approved != 0).all()
    elif type == 2:
        channel_list = d2_channels.query.filter(d2_channels.owned_by != 0).filter(d2_channels.approved != 0).all()
        
    for channel in channel_list:
        threadcount = 0
        messagecount = 0
        channel_icon = '/images/channelicons/{}.png'.format(channel.short_name)
        channel_icon_default = '/images/channelicons/blank.png'
        root_path = syndbb.app.static_folder
        if syndbb.os.path.isfile(root_path+channel_icon):
            channel_icon = cdn_path() + channel_icon
        else:
            channel_icon = cdn_path() + channel_icon_default
        threadcount = d2_activity.query.filter(d2_activity.category == channel.id).count()
        threadlist = d2_activity.query.filter(d2_activity.category == channel.id).all()
        
        for thread in threadlist:
            messagecount += d2_activity.query.filter(d2_activity.replyto == thread.id).count()
            
        messagecount = threadcount + messagecount
            
        channels.append({"id": channel.id, "name": channel.name, "description": channel.description, "alias": channel.short_name, "anon": channel.anon, "auth": channel.auth, "owned_by": channel.owned_by, "nsfw": channel.nsfw, "alias": channel.short_name, "icon": channel_icon, "messages": messagecount, "chat_url": channel.chat_url})
    channels.sort(key=itemgetter('id'))

    for channel in channels:
        modes = ""
        
        if channel['auth'] >= 1:
            modes += '<i title="Authorization required. (>='+get_title_by_rank(channel['auth'])+')" class="fa fa-lock" aria-hidden="true"></i> '
        if channel['anon'] == 1:
            modes += ' <i title="Anonymous posting allowed." class="fa fa-eye-slash" aria-hidden="true"></i> '
        if channel['nsfw'] == 1:
            modes += '<i title="Not safe for work. (18+)" class="fa fa-ban" aria-hidden="true"></i>'

        options = ""

        # display message counts on channel listings
        if syndbb.core_config['site']['display_message_counts']:
            options += '''<td class="home-channel home-channel-threads" title="Messages" style="padding-right: 9px !important;">
                    <span style="float: right;">
                    ''' + str(channel['messages']) + '''
                    </span>
                </td>'''


        options += '<td class="home-channel small home-channel-options" style="padding-right: 9px !important;">'
        
        if 'chat_url' in channel and channel['chat_url']: options += '''
                    <a href="'''+channel['chat_url']+'''" title="Join Chat">
                        <i class="silk-icon icon_comment" aria-hidden="true"></i>
                    </a>'''

        options += '''
                    <a href="/''' + str(channel['alias']) + '''/grid" title="Grid/Catalog View">
                        <i class="silk-icon icon_application_view_tile" aria-hidden="true"></i>
                    </a>
                    
                    <a href="/''' + str(channel['alias']) + '''/new_thread" title="Create A New Thread">
                        <i class="silk-icon icon_add" aria-hidden="true"></i>
                    </a>'''

        options += '</td>'
        
        if 'description' in channel and channel['description'] != "":
            has_description = "home-channel-desc"
        else:
            has_description = "home-channel-nodesc"

        chlist += '''<tr>
            <td class="home-channel home-channel-icon"><a href="/''' + str(channel['alias']) + '''"><img src="'''+ str(channel['icon']) + '''" alt=""/></a></td>
            <td class="home-channel '''+ has_description +'''"><a href="/''' + str(channel['alias']) + '''"><b>''' + str(channel['name']) + '''</b></a>
            <br/><span class="small">''' + str(channel['description']) + '''</span>
            </td>
            <td class="home-channel home-channel-modes" style="padding-right: 9px !important;">
                <span style="float: right;">
                   <span class="text-muted">''' + modes + '''</span>
                </span>
            </td>
            
            ''' + options + '''
            
          </tr>'''
    return chlist
syndbb.app.jinja_env.globals.update(get_channel_list=get_channel_list)

### MySQL Functions ###
class d2_channels(syndbb.db.Model):
    id = syndbb.db.Column(syndbb.db.Integer, primary_key=True)
    name = syndbb.db.Column(syndbb.db.String(50), unique=True)
    short_name = syndbb.db.Column(syndbb.db.String(4), unique=True)
    description = syndbb.db.Column(syndbb.db.String, unique=False)
    chat_url = syndbb.db.Column(syndbb.db.String, unique=False)
    owned_by = syndbb.db.Column(syndbb.db.Integer, unique=False)
    nsfw = syndbb.db.Column(syndbb.db.Integer, unique=False)
    approved = syndbb.db.Column(syndbb.db.Integer, unique=False)
    auth = syndbb.db.Column(syndbb.db.Integer, unique=False)
    anon = syndbb.db.Column(syndbb.db.Integer, unique=False)
    user_list = syndbb.db.Column(syndbb.db.String, unique=False)
    mod_list = syndbb.db.Column(syndbb.db.String, unique=False)
    type = syndbb.db.Column(syndbb.db.Integer, unique=False)

    def __init__(self, name, short_name, description, chat_url, nsfw, owned_by, approved, auth, anon, user_list, mod_list, type):
        self.name = name
        self.short_name = short_name
        self.description = description
        self.chat_url = chat_url
        self.owned_by = owned_by
        self.nsfw = nsfw
        self.approved = approved
        self.auth = auth
        self.anon = anon
        self.user_list = user_list
        self.mod_list = mod_list
        self.type = type

    def __repr__(self):
        return '<Channel %r>' % self.name

class d2_activity(syndbb.db.Model):
    id = syndbb.db.Column(syndbb.db.Integer, primary_key=True)
    user_id = syndbb.db.Column(syndbb.db.String, unique=False)
    time = syndbb.db.Column(syndbb.db.Integer, unique=False)
    content = syndbb.db.Column(syndbb.db.String, unique=False)
    replyto = syndbb.db.Column(syndbb.db.Integer, unique=False)
    replyToPost = syndbb.db.Column(syndbb.db.Integer, unique=False)
    title = syndbb.db.Column(syndbb.db.String, unique=False)
    category = syndbb.db.Column(syndbb.db.Integer, unique=False)
    reply_time = syndbb.db.Column(syndbb.db.Integer, unique=False)
    reply_count = syndbb.db.Column(syndbb.db.Integer, unique=False)
    rating = syndbb.db.Column(syndbb.db.Integer, unique=False)
    post_icon = syndbb.db.Column(syndbb.db.String, unique=False)
    anonymous = syndbb.db.Column(syndbb.db.Integer, unique=False)

    def __init__(self, user_id, time, content, replyto, replyToPost, title, category, reply_time, reply_count, rating, post_icon, anonymous):
        self.user_id = user_id
        self.time = time
        self.content = content
        self.replyto = replyto
        self.replyToPost = replyToPost
        self.title = title
        self.category = category
        self.reply_time = reply_time
        self.reply_count = reply_count
        self.rating = rating
        self.post_icon = post_icon
        self.anonymous = anonymous

    def __repr__(self):
        return '<Post %r>' % self.id

class d2_post_ratings(syndbb.db.Model):
    id = syndbb.db.Column(syndbb.db.Integer, primary_key=True)
    post_id = syndbb.db.Column(syndbb.db.String(50), unique=False)
    user_id = syndbb.db.Column(syndbb.db.String(4), unique=False)
    type = syndbb.db.Column(syndbb.db.String, unique=False)

    def __init__(self, post_id, user_id, type):
        self.post_id = post_id
        self.user_id = user_id
        self.type = type

    def __repr__(self):
        return '<Rating %r>' % self.type
