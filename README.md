# SynDBB (Cyndi)

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
*   Improved site and IRC API.
*   LDAP Authentication support (+ automatic migration)
*   JSON based configuration file.
*   Most aspects of the site configurable in config.json.
*   Display names (+ display name generator).
*   Username generator.
*   Summary cards for user profiles.
*   Profile and user tags.
*   NSFW profile toggle.
*   Tall avatar support (original avatar source image is used) for profiles (all members) and posts (donators).
*   Various configuration options for custom channels (access control, moderator list, NSFW toggle, anon posting toggle, imageboard toggle, etc)
*   Channel and thread info displayed on sidebar.
*   User flairs.
*   Multi-user/profile support (accounts can be linked together and switched between with ease).
*   Mobile layout.
*   Theme selector.
*   All scripts and styles hosted locally.

## Setup
    chmod +x *.sh
    chmod -R 0700 syndbb/static/data/
    ./run.sh install
    ./run.sh [http|uwsgi|windows]


----------


## Information for Developers

### Premade test accounts:

    synop:password (root admin)
    council:password (regular admin)
    peacekeeper:password
    supporter:password
    staff:password
    citizen:password
    tourist:password
    banned:password 

### Ranks:

#### Special Operations

* Rank Integer: >=900
* Has a red name.
* Can approve/disapprove emoticons, channels.
* Can change user ranks. (promote/demote)


#### Federation Council

* Rank Integer: >=500
* Has a purple name.
* Can view admin panel.
* Can view the users list.
* Can ban/unban users.
* Can edit/delete posts/threads.

#### Peacekeeper

* Rank Integer: >=100
* Has a green name.
* Can ban/unban users.
* Can edit/delete posts/threads.

#### Citizen (Supporter)

* Rank Integer: >=50
* Has a light blue name.
* Can have animated and full size (tall) avatars in threads and on profile.
* (Group name configurable in site config.)

#### Citizen (Staff)

* Rank Integer: >=20
* Has a light red name.
* Currently has no extra permissions.

#### Citizen

* Rank Integer: >=10
* Has a light blue name.
* Currently has no extra permissions.

#### Tourist

* Rank Integer: 1
* Has a grey blue name.
* Can create threads, posts and pastes. 
* Can upload files.
* Can modify their profile.
* Can delete their own threads/posts.
* Can request emoticons and channels.
* Can invite other users.

### ZNC/IRC Integration:

Creates a ZNC user with the users' name and the IRC auth key provided in their preferences.

Requires https://github.com/unendingPattern/znc-httpadmin to be installed on the ZNC server and the IRC and ZNC details set properly inside the config file.

You should have a specific ZNC user with admin privileges which only the server's IP has permission to contact.


*This code is released under the **[Q Public License 1.0 (QPL-1.0)](https://tldrlegal.com/license/q-public-license-1.0-(qpl-1.0)#summary "QPL-1.0")**. The full license is included in [LICENSE.md](LICENSE.md).*