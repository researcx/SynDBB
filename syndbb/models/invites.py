#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb

### MySQL Functions ###
class d2_invites(syndbb.db.Model):
    id = syndbb.db.Column(syndbb.db.Integer, primary_key=True)
    code = syndbb.db.Column(syndbb.db.String, unique=False)
    user_id = syndbb.db.Column(syndbb.db.Integer, unique=False)
    used_by = syndbb.db.Column(syndbb.db.Integer, unique=False)

    def __init__(self, code, user_id, used_by):
        self.code = code
        self.user_id = user_id
        self.used_by = used_by

    def __repr__(self):
        return '<Code %r>' % self.code

class d2_requests(syndbb.db.Model):
    id = syndbb.db.Column(syndbb.db.Integer, primary_key=True)
    username = syndbb.db.Column(syndbb.db.String, unique=False)
    email = syndbb.db.Column(syndbb.db.String, unique=False)
    reason = syndbb.db.Column(syndbb.db.String, unique=False)

    def __init__(self, username, email, reason):
        self.username = username
        self.email = email
        self.reason = reason

    def __repr__(self):
        return '<Username %r>' % self.username
