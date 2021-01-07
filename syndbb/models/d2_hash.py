#
# Copyright (c) 2017 - 2020 Keira T (https://kei.info.gf). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb
import hashlib


def d2_hash(string):
    pw_hash = syndbb.core_config['server']['hash']
    return hashlib.sha256(pw_hash.encode()+string.encode()).hexdigest()

if syndbb.core_config['ldap']['enabled'] :
    from passlib.hash import ldap_salted_sha1
    def ldap_hash(string):
        return ldap_salted_sha1.hash(string)

def get_ip_hash(addr):
    return d2_hash(addr)[:10]