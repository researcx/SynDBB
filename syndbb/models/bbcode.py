#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb, bbcode, re

#Initiate BBCode
parser = bbcode.Parser()

#Images
parser.add_simple_formatter('img', '<img src="%(value)s" onclick="window.open(this.src)" class="bbcode-image img-responsive inline-block" alt="[IMG]" />', replace_links=False)

#Lists
parser.add_simple_formatter('ul', '<ul>%(value)s</ul>', swallow_trailing_newline=True)
parser.add_simple_formatter('ol', '<ol>%(value)s</ol>', swallow_trailing_newline=True)
parser.add_simple_formatter('li', '<li>%(value)s</li>', swallow_trailing_newline=True)

#Alignment
parser.add_simple_formatter('left', '<span style="float: left;">%(value)s</span>')
parser.add_simple_formatter('right', '<span style="float: right;">%(value)s</span>')

#Replies
parser.add_simple_formatter('reply', '<a href="#%(value)s" style="border-bottom: 1px dashed #111;">&gt;%(value)s</a>', swallow_trailing_newline=False)

#Ban Message
parser.add_simple_formatter('ban', '<span style="color: #ff0000; font-weight: bold;">%(value)s</span>', swallow_trailing_newline=False)

#YouTube
def youtubelink(tag_name, value, options, parent, context):
    youtube = re.match('^[^v]+v=(.{11}).*', value)
    return '<iframe id="ytplayer" type="text/html" src="//www.youtube.com/embed/'+youtube.group(1)+'" frameborder="0" style="width: 480px; height: 270px;" allowfullscreen></iframe>'
parser.add_formatter('youtube', youtubelink, replace_links=False, strip=True, swallow_trailing_newline=True)

#Text Font
def render_font(tag_name, value, options, parent, context):
    if 'font' in options:
        font = options['font'].strip()
    return '<span style="font-family:'+font+'">'+value+'</span>'
parser.add_formatter('font', render_font)


#Text Size
def render_size(tag_name, value, options, parent, context):
    if 'size' in options:
        size = options['size'].strip()
    elif options:
        size = list(options.keys())[0].strip()
    else:
        return value
    if size == '1':
        size = 'xx-small'
    elif size == '2':
        size = 'x-small'
    elif size == '3':
        size = 'small'
    elif size == '4':
        size = 'medium'
    elif size == '5':
        size = 'large'
    elif size == '6':
        size = 'x-large'
    elif size == '7':
        size = 'xx-large'
    elif size == '8':
        size = '48px'
    elif size == '9':
        size = '48px'
    return '<span style="font-size:%(size)s;">%(value)s</span>' % {
        'size': size,
        'value': value,
    }
parser.add_formatter('size', render_size)
