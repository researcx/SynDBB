#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb, shutil, base64, requests, json
from syndbb.models.users import d2_user
from flask import make_response

@syndbb.app.route("/api/irc/")
def irc_api():
    apikey = syndbb.request.args.get('api', '')
    if apikey == syndbb.ircapi:
        nick = syndbb.request.args.get('nick', '')
        if nick:
            if not syndbb.re.search('^[a-z][a-z0-9-_]{2,32}$', nick, syndbb.re.IGNORECASE):
                return "Invalid nick (must match IRC standards)."
            user = d2_user.query.filter_by(username=nick).first()

            # Get user profile in XML
            # /api/irc/?api=<api>&nick=<nick>&get_profile=1
            get_profile = syndbb.request.args.get('get_profile', '')
            if get_profile:
                template = syndbb.render_template('userinfo.xml', user=user)
                response = make_response(template)
                response.headers['Content-Type'] = 'application/xml'
                return response

            # Count lines spoken
            # /api/irc/?api=<api>&nick=<nick>&count_lines=<amount>
            count_lines = syndbb.request.args.get('count_lines', '')
            if count_lines:
                if int(count_lines) >= 5:
                    user.points = user.points + (int(count_lines) / 2)
                user.line_count = user.line_count + int(count_lines)
                syndbb.db.session.commit()
                return str(user.line_count)

            # Count words used
            # /api/irc/?api=<api>&nick=<nick>&count_words=<amount>
            count_words = syndbb.request.args.get('count_words', '')
            if count_words:
                if int(count_words) >= 50:
                    user.points = user.points + (int(count_words) / 2)
                user.word_count = user.word_count + int(count_words)
                syndbb.db.session.commit()
                return str(user.word_count)

            # Count profanity used
            # /api/irc/?api=<api>&nick=<nick>&count_profanity=<amount>
            count_profanity = syndbb.request.args.get('count_profanity', '')
            if count_profanity:
                user.profanity_count = user.profanity_count + int(count_profanity)
                syndbb.db.session.commit()
                return str(user.profanity_count)

            # Add positive karma
            # /api/irc/?api=<api>&nick=<nick>&karma_positive=<amount>
            karma_positive = syndbb.request.args.get('karma_positive', '')
            if karma_positive:
                user.karma_positive = user.karma_positive + int(karma_positive)
                syndbb.db.session.commit()
                return str(user.karma_positive)

            # Add negative karma
            # /api/irc/?api=<api>&nick=<nick>&karma_negative=<amount>
            karma_negative = syndbb.request.args.get('karma_negative', '')
            if karma_negative:
                user.karma_negative = user.karma_negative + int(karma_negative)
                syndbb.db.session.commit()
                return str(user.karma_negative)

            # Give currency
            # /api/irc/?api=<api>&nick=<nick>&give_currency=<amount>
            give_currency = syndbb.request.args.get('give_currency', '')
            if give_currency:
                user.points = user.points + int(give_currency)
                syndbb.db.session.commit()
                return str(user.points)

            # Take currency
            # /api/irc/?api=<api>&nick=<nick>&take_currency=<amount>
            take_currency = syndbb.request.args.get('take_currency', '')
            if take_currency:
                user.points = user.points + int(take_currency)
                syndbb.db.session.commit()
                return str(user.points)

            return "Nothing to do."
        else:
            # Do the IRC user count thing
            # /api/irc/?api=<api>&do_usercount
            do_usercount = syndbb.request.args.get('do_usercount', '')
            if do_usercount:
                try:
                    zncrequest = requests.get("https://" + syndbb.znc_address + ":" + syndbb.znc_port + "/mods/global/httpadmin/listusers", auth=(syndbb.znc_user, syndbb.znc_password), verify=False)
                    count_data = json.loads(zncrequest.text)
                    count = str(count_data["count"])

                    with open("logs/irc_users.log", "w") as text_file:
                        text_file.write(count)

                    return count
                except requests.exceptions.RequestException:
                    return "0"

            return "No nickname defined."
    else:
        return "Invalid API Key"
