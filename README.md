## SynDBB

**SynDBB** is a compilation of all the best parts of bulletin boards, intended for IRC/ZNC integration, which is where the name comes from. (Syndication + IRCd + Bulletin Boards)

It is an open-source cross-platform forum software written in Python + Flask. It's primarily intended to be used for the D2K5 website, however users are welcome and encouraged to submit improvements, features, feature requests, fixes and bug reports.

*This code is released under the **[Q Public License 1.0 (QPL-1.0)](https://tldrlegal.com/license/q-public-license-1.0-(qpl-1.0)#summary "QPL-1.0")**. The full license is included in [LICENSE.md](LICENSE.md).*

## Setup
    chmod +x *.sh
    ./install.sh
    ./run.sh

## Set proper permissions for the data folder
This is where the avatars, file uploads, thumbnails and submitted emoticons will go.

`chmod -R 0700 syndbb/static/data/`

----------

## Information for Developers

###Premade test accounts:

    admin:admin
    banneduser:testing
    Poster:testing

###Ranks:

####Administrator

* Rank Integer: >=900
* Has a red name.
* Can approve/disapprove emoticons, channels.
* Can change user ranks. (promote/demote)
* Inherits permissions from lower ranks.


####Operator (Tier-1 Moderator)

* Rank Integer: >=900
* Has a purple name.
* Can view admin panel.
* Can view the users list.
* Can ban/unban users.
* Can edit/delete posts/threads.
* Inherits permissions from lower ranks.

####Half-Operator (Tier-2 Moderator)

* Rank Integer: >=100
* Has a green name.
* Currently has no extra permissions.

####Gold Member

* Rank Integer: >=50
* Has a gold name.
* Currently has no extra permissions.
* *To-do:* Can upload animated avatars.

####Registered User

* Rank Integer: <50
* Has a blue name.
* Can create threads, posts and pastes. 
* Can upload files.
* Can modify their profile.
* Can delete their own threads/posts.
* Can request emoticons and channels.
* Can invite other users.

###ZNC/IRC Integration:

Creates a ZNC user with the users' name and the IRC auth key provided in their preferences.

Requires https://github.com/faggqt/znc-httpadmin to be installed on the ZNC server and the IRC and ZNC details set properly inside the config file.

You should have a specific ZNC user with admin privileges which only the server's IP has permission to contact.
