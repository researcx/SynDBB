#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb

### MySQL Functions ###
class d2_paste(syndbb.db.Model):
    id = syndbb.db.Column(syndbb.db.Integer, primary_key=True)
    user_id = syndbb.db.Column(syndbb.db.Integer, unique=False)
    paste_id = syndbb.db.Column(syndbb.db.String, unique=True)
    time = syndbb.db.Column(syndbb.db.Integer, unique=False)
    content = syndbb.db.Column(syndbb.db.String, unique=False)
    title = syndbb.db.Column(syndbb.db.String, unique=False)

    def __init__(self, user_id, paste_id, time, content, title):
        self.user_id = user_id
        self.paste_id = paste_id
        self.time = time
        self.content = content
        self.title = title

    def __repr__(self):
        return '<Forum %r>' % self.title
