#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb

# Core Pages
import syndbb.views.basic

# User Pages
import syndbb.views.auth
import syndbb.views.invites
import syndbb.views.profile

# Forums, upload, pastebin
import syndbb.views.forums
import syndbb.views.events
import syndbb.views.upload
import syndbb.views.pastebin
import syndbb.views.quotedb
import syndbb.views.emoticons

# Management
import syndbb.views.admin

# Miscellaneous
import syndbb.views.irc_api
import syndbb.views.xmlfeed


#Run the main app...
if __name__ == '__main__':
    import logging
    logging.basicConfig(filename='error.log',level=logging.DEBUG)

    syndbb.app.run()
