#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb
from syndbb.models.users import d2_user, checkSession

#Get quote rating
@syndbb.app.template_filter('get_quote_rating')
def get_quote_rating(quote_id):
    ratings = d2_quote_ratings.query.filter_by(quote_id=quote_id).all()

    final_count = 0
    for rating in ratings:
        final_count = final_count + rating.type
    return final_count
syndbb.app.jinja_env.globals.update(get_quote_rating=get_quote_rating)

### Rate Quotes ###
@syndbb.app.route('/functions/rate_quote/')
def do_rate_quote():
    quote_id = syndbb.request.args.get('quote_id', '')
    ratingtype = syndbb.request.args.get('type', '')
    uniqid = syndbb.request.args.get('uniqid', '')
    if quote_id and ratingtype and uniqid:
        if 'logged_in' in syndbb.session:
            userid = checkSession(str(uniqid))
            if userid:
                quotecheck = d2_quotes.query.filter_by(id=quote_id).first()
                if quotecheck:
                    ratingcheck = d2_quote_ratings.query.filter_by(quote_id=quote_id).filter_by(user_id=userid).first()
                    if ratingcheck:
                        return "You've already rated this quote."
                    quote_creator = d2_user.query.filter_by(user_id=quotecheck.user_id).first()

                    if ratingtype == "down":
                        quote_creator.karma_negative = quote_creator.karma_negative + 1
                        syndbb.db.session.commit()
                        ratingtype = -1
                    elif ratingtype == "up":
                        quote_creator.karma_positive = quote_creator.karma_positive + 1
                        syndbb.db.session.commit()
                        ratingtype = 1

                    quotecheck.rating = int(quotecheck.rating) + ratingtype
                    syndbb.db.session.commit()

                    submit_rating = d2_quote_ratings(quote_id, userid, ratingtype)
                    syndbb.db.session.add(submit_rating)
                    syndbb.db.session.commit()

                    return str(quotecheck.id)
                else:
                    return "Trying to rate a quote which doesnt exist."
        else:
            return "You are not logged in!"
    else:
        return "Invalid Request"

### MySQL Functions ###
class d2_quotes(syndbb.db.Model):
    id = syndbb.db.Column(syndbb.db.Integer, primary_key=True)
    user_id = syndbb.db.Column(syndbb.db.Integer, syndbb.db.ForeignKey('d2_user.user_id'))
    user = syndbb.db.relationship('d2_user', backref=syndbb.db.backref('d2_quotes', lazy='dynamic'))
    time = syndbb.db.Column(syndbb.db.Integer, unique=True)
    content = syndbb.db.Column(syndbb.db.String, unique=False)
    approved = syndbb.db.Column(syndbb.db.Integer, unique=False)
    rating = syndbb.db.Column(syndbb.db.Integer, unique=False)

    def __init__(self, user_id, time, content, approved, rating):
        self.user_id = user_id
        self.time = time
        self.content = content
        self.approved = approved
        self.rating = rating

    def __repr__(self):
        return '<Quote %r>' % self.id

class d2_quote_ratings(syndbb.db.Model):
    id = syndbb.db.Column(syndbb.db.Integer, primary_key=True)
    quote_id = syndbb.db.Column(syndbb.db.String(50), unique=False)
    user_id = syndbb.db.Column(syndbb.db.String(4), unique=False)
    type = syndbb.db.Column(syndbb.db.String, unique=False)

    def __init__(self, quote_id, user_id, type):
        self.quote_id = quote_id
        self.user_id = user_id
        self.type = type

    def __repr__(self):
        return '<Rating %r>' % self.type
