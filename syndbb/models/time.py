#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb

intervals = (
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hours', 3600),    # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
    )

def display_time(seconds, granularity=2):
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])

#Code for the "page generation took x seconds" thing.
@syndbb.app.before_request
def before_request():
    syndbb.g.request_start_time = syndbb.time.time()
    syndbb.g.request_time = lambda: "%.5f" % (syndbb.time.time() - syndbb.g.request_start_time)

#Current time as a part of the code
@syndbb.app.context_processor
def inject_now():
    return {'now': syndbb.datetime.utcnow()}

#Current time in UNIX format
def unix_time_current():
    return int(syndbb.time.time())

#Display how long ago something happened in a readable format
@syndbb.app.template_filter('time_ago')
def time_ago(unixtime):
    return syndbb.humanize.naturaltime(syndbb.datetime.now() - syndbb.timedelta(seconds=unix_time_current() - int(unixtime)))
syndbb.app.jinja_env.globals.update(time_ago=time_ago)

#Display a somewhat normal date
@syndbb.app.template_filter('human_date')
def human_date(unixtime):
    return syndbb.datetime.fromtimestamp(int(unixtime)).strftime('%Y-%m-%d %H:%M:%S')
syndbb.app.jinja_env.globals.update(human_date=human_date)

#Display a somewhat normal size
@syndbb.app.template_filter('human_size')
def human_size(filesize):
    return syndbb.humanize.naturalsize(filesize)
syndbb.app.jinja_env.globals.update(human_size=human_size)
