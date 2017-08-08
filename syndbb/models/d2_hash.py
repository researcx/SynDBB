#
# Copyright (c) 2017 by faggqt (https://faggqt.pw). All Rights Reserved.
# You may use, distribute and modify this code under the QPL-1.0 license.
# The full license is included in LICENSE.md, which is distributed as part of this project.
#

import syndbb
import hashlib

def d2_hash(string):
    pw_hash = syndbb.hashkey;
    return hashlib.sha256(pw_hash.encode()+string.encode()).hexdigest()
