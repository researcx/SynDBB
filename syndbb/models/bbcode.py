#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb, bbcode, re

def d2_linker(url):
    href = url
    if '://' not in href:
        href = 'http://' + href
    return '<a href="%s" class="link-dotted" target="_blank">%s</a>' % (href, url)

#Initiate BBCode
parser = bbcode.Parser(linker=d2_linker)

#Code tag
parser.add_simple_formatter('code', '<code>%(value)s</code>', render_embedded=False, transform_newlines=False,
swallow_trailing_newline=True, replace_links=False)

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
    pattern = r'(?:https?:\/\/)?(?:[0-9A-Z-]+\.)?(?:youtube|youtu|youtube-nocookie)\.(?:com|be)\/(?:watch\?v=|watch\?.+&v=|embed\/|v\/|.+\?v=)?([^&=\n%\?]{11})'
    youtube = re.findall(pattern, value, re.IGNORECASE)
    if youtube and youtube[0]:
        return '<iframe id="ytplayer" type="text/html" src="//www.youtube.com/embed/'+youtube[0]+'" frameborder="0" style="width: 480px; height: 270px;" allowfullscreen></iframe>'
    else:
        return "[Invalid video ID]"
parser.add_formatter('youtube', youtubelink, replace_links=False, strip=True, swallow_trailing_newline=False)

#Text Background
def render_bg(tag_name, value, options, parent, context):
    if 'bg' in options:
        bg = options['bg'].strip()
    return '<span style="background-color:'+bg+'; padding: 1px 4px 1px 4px;">'+value+'</span>'
parser.add_formatter('bg', render_bg)

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

#Dotted links
def _render_url(name, value, options, parent, context):
    if options and 'url' in options:
        # Option values are not escaped for HTML output.
        href = parser._replace(options['url'], parser.REPLACE_ESCAPE)
    else:
        href = value
    # Completely ignore javascript: and data: "links".
    if re.sub(r'[^a-z0-9+]', '', href.lower().split(':', 1)[0]) in ('javascript', 'data', 'vbscript'):
        return ''
    # Only add the missing http:// if it looks like it starts with a domain name.
    if '://' not in href and _domain_re.match(href):
        href = 'http://' + href
    return '<a href="%s" class="link-dotted" target="_blank">%s</a>' % (href.replace('"', '%22'), value)

parser.add_formatter('url', _render_url, replace_links=False, replace_cosmetic=False)
