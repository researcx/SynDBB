# SynDBB (Legacy)

SynDBB is a hybridization of different aspects of classic internet forums and imageboards.


**Features:**

*   File uploader with external upload support.
*   Anonymous file uploader.
*   Automatic Exif data removal on uploaded images.
*   Deleted files securely wiped using "shred".
*   File listing with file info and thumbnails.
*   Temporary personal image galleries.
*   Custom user-created channels.
*   List and grid (catalog) view modes for channels.
*   List and gallery view modes for threads.
*   Rating system for threads, quotes and IRC.
*   Site/IRC integration API.
*   Avatar history with the ability to re-use avatars without uploading them.
*   Custom emoticon submission (admin approval required).
*   QDB style quote database for IRC quotes (quotes are admin approved).
*   Simple pastebin.
*   Theme selector.
*   All scripts and styles hosted locally.

## Setup
    chmod +x *.sh
    ./install.sh
    ./run.sh

## Set proper permissions for the data folder

`chmod -R 0700 syndbb/static/data/`

----------

## Information for Developers

### Ranks:

#### Administrator

* Rank Integer: >=900
* Can approve/disapprove emoticons, channels.
* Can change user ranks. (promote/demote)


#### Operator (Tier-1 Moderator)

* Rank Integer: >=500
* Can view admin panel.
* Can view the users list.
* Can ban/unban users.
* Can edit/delete posts/threads.

#### Half-Operator (Tier-2 Moderator)

* Rank Integer: >=100
* *Currently has no extra permissions.*

#### Gold Member

* Rank Integer: >=50
* *Currently has no extra permissions.*

#### Registered User

* Rank Integer: <50
* Can create threads, posts and pastes. 
* Can upload files.
* Can modify their profile.
* Can delete their own threads/posts.
* Can request emoticons and channels.
* Can invite users.

### ZNC/IRC Integration:

Creates a ZNC user with the users' name and the IRC auth key provided in their preferences.

Requires https://github.com/unendingPattern/znc-httpadmin to be installed on the ZNC server and the IRC and ZNC details set properly inside the config file.

You should have a specific ZNC user with admin privileges which only the server's IP has permission to contact.


*This code is released under the **[Q Public License 1.0 (QPL-1.0)](https://tldrlegal.com/license/q-public-license-1.0-(qpl-1.0)#summary "QPL-1.0")**. The full license is included in [LICENSE.md](LICENSE.md).*
