# SynDBB

SynDBB is a compilation of all the best parts of bulletin boards, intended for IRC/ZNC integration.  
Code, layout and templates written from scratch. Images that are part of the design are also all custom-made.  

**Features:**

*   All scripts and styles are hosted locally.
*   Passwords are hashed client-side before they are submitted to the server, then hashed again server-side.
*   File uploading system where you can upload files on-site or externally using curl/ShareX.
*   File listing for all of your uploads with file info and thumbnails, sorted by date.
*   Forum/channel system with the ability to create your own custom forums/channels with admin approval.
*   Custom forums/channels can be made to have their own guidelines and description.
*   List/grid view toggle for file uploads and forums/threads.
*   Thread gallery/image view mode.
*   Light/dark theme selector (easy to create/add themes).
*   QDB style quote database for IRC quotes.
*   Avatar history with the ability to re-use avatars without uploading them.
*   Users can submit their own emoticons and have them admin approved.
*   Uploaded files get shredded (secure erased) when the user chooses to delete them.
*   Pastebin system with a listing of all of your pastes.
*   Thread/post karma (upvoting and downvoting).
*   Karma positive/negative/total system for IRC.
*   IRC statistics tracking for lines and words spoken.
*   Lightweight.

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

### Premade test accounts:

    admin:admin
    banneduser:testing
    Poster:testing

### Ranks:

#### Administrator

* Rank Integer: >=900
* Has a red name.
* Can approve/disapprove emoticons, channels.
* Can change user ranks. (promote/demote)
* Inherits permissions from lower ranks.


#### Operator (Tier-1 Moderator)

* Rank Integer: >=500
* Has a purple name.
* Can view admin panel.
* Can view the users list.
* Can ban/unban users.
* Can edit/delete posts/threads.
* Inherits permissions from lower ranks.

#### Half-Operator (Tier-2 Moderator)

* Rank Integer: >=100
* Has a green name.
* Currently has no extra permissions.

#### Gold Member

* Rank Integer: >=50
* Has a gold name.
* Currently has no extra permissions.
* *To-do:* Can upload animated avatars.

#### Registered User

* Rank Integer: <50
* Has a blue name.
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
