#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb
from syndbb.models.users import d2_user, checkSession

def give_currency(userid, amount):
    user = d2_user.query.filter_by(user_id=userid).first()
    if user:
        user.points = int(user.points) + int(amount)
        syndbb.db.session.commit()

def take_currency(userid, amount):
    user = d2_user.query.filter_by(user_id=userid).first()
    if user:
        user.points = int(user.points) - int(amount)
        syndbb.db.session.commit()

def get_currency(userid):
    user = d2_user.query.filter_by(user_id=userid).first()
    if user:
        return user.points
    else:
        return 0

def give_posts(userid, amount):
    user = d2_user.query.filter_by(user_id=userid).first()
    if user:
        user.post_count = int(user.post_count) + int(amount)
        syndbb.db.session.commit()

def take_posts(userid, amount):
    user = d2_user.query.filter_by(user_id=userid).first()
    if user:
        user.post_count = int(user.post_count) - int(amount)
        syndbb.db.session.commit()
