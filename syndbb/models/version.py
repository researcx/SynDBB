#
# Copyright (c) 2017 - 2020 Keira T (https://kei.info.gf). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb
import subprocess

#Fetch syndbb, Python and Flask versions
@syndbb.app.context_processor
def inject_version():
    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}
        for k in ['SYSTEMROOT', 'PATH']:
            v = syndbb.os.environ.get(k)
            if v is not None:
                env[k] = v
        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'
        out = subprocess.Popen(cmd, stdout = subprocess.PIPE, env=env).communicate()[0]
        return out

    try:
        gfhash = _minimal_ext_cmd(['git', 'rev-parse', 'HEAD'])
        gshash = _minimal_ext_cmd(['git', 'rev-parse', '--short', 'HEAD'])
        gcount = _minimal_ext_cmd(['git', 'rev-list', '--count', 'HEAD'])
        git_fhash = gfhash.strip().decode('ascii')
        git_shash = gshash.strip().decode('ascii')
        git_version = "r" + gcount.strip().decode('ascii')
    except OSError:
        git_fhash = "Unknown"
        git_shash = "Unknown"
        git_version = "r0"

    core_config = syndbb.core_config

    return core_config

#Get core config variables
@syndbb.cache.memoize(timeout=86400) # get_core_config
def get_core_config():
    return syndbb.core_config
syndbb.app.jinja_env.globals.update(get_core_config=get_core_config)

@syndbb.app.context_processor
def inject_debug():
    return dict(debug=syndbb.app.debug)