## SynDBB

**SynDBB** is a compilation of all the best parts of bulletin boards, intended for IRC/ZNC integration, which is where the name comes from (Syndication + IRCd + Bulletin Boards)

It is an open-source cross-platform forum software written in Python + Flask. It's primarily intended to be used for the D2K5 website, however users are welcome and encouraged to submit improvements, features, feature requests, fixes and bug reports.

*This code is released under the **[Q Public License 1.0 (QPL-1.0)](https://tldrlegal.com/license/q-public-license-1.0-(qpl-1.0)#summary "QPL-1.0")**. The full license is included in [LICENSE.md](LICENSE.md).*

## Setup
`chmod +x *.sh`

`./install.sh`

`./run.sh`

## Set proper permissions for the data folder
This is where the avatars, file uploads, thumbnails and submitted emoticons will go.

`chmod -R 0700 syndbb/static/data/`

----------

## Information for Developers

**Test accounts:**

    admin:admin
    banneduser:testing
    Poster:testing

**Ranks:**

    >=900 = Administrator
Red name.

Can approve/disapprove emoticons, channels + change user ranks (promote/demote) + inherits permissions from lower ranks.


    >=500 = Operator (Tier-1 Moderator)

Purple name.

Can view admin panel, users list, ban/unban users, edit/delete posts/threads + inherits permissions from lower ranks.


    >=100 = Half-Op (Tier-2 Moderator)

Green name.

Currently has no permissions.


    >=50 = Gold Member

Golden name.

Currently has no extra permissions (future idea: can upload animated avatars)


    <50 = Regular User / Member
Blue name.

Can create threads, posts, pastes, upload files, modify their profile, delete own threads/posts, request emoticons and channels, invite other users.

**ZNC/IRC Integration:**

Creates a ZNC user with the users' name and the IRC auth key provided in their preferences.

Requires https://github.com/prawnsalad/znc-httpadmin to be installed on the ZNC server and the IRC and ZNC details set properly inside the config file.

You should have a specific ZNC user with admin privileges which only the server's IP has permission to contact.

