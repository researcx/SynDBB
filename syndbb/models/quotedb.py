#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb
from syndbb.models.users import d2_user

### MySQL Functions ###
class d2_quotes(syndbb.db.Model):
    id = syndbb.db.Column(syndbb.db.Integer, primary_key=True)
    user_id = syndbb.db.Column(syndbb.db.Integer, syndbb.db.ForeignKey('d2_user.user_id'))
    user = syndbb.db.relationship('d2_user', backref=syndbb.db.backref('d2_quotes', lazy='dynamic'))
    time = syndbb.db.Column(syndbb.db.Integer, unique=True)
    content = syndbb.db.Column(syndbb.db.String, unique=False)
    approved = syndbb.db.Column(syndbb.db.Integer, unique=False)

    def __init__(self, user_id, time, content, approved):
        self.user_id = user_id
        self.time = time
        self.content = content
        self.approved = approved

    def __repr__(self):
        return '<Quote %r>' % self.id
