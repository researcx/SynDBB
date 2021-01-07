#!/bin/bash
# Simple bash file and screenshot uploader by Keira T (https://kei.info.gf)
# Automatically generated for {{ get_core_config()['site']['branding'] }} ({{ get_core_config()['site']['domain'] }})

# Usage:
#   File: upload.sh <filename.ext>
#   Screenshot: upload.sh <full|active|selection>

# Dependencies:
#   scrot (for screenshotting)
#   curl (for uploading)
#   xclip (for copying the link to your clipboard)

#Configuration:
#   This script requires your {{ get_core_config()['site']['branding'] }} username and your upload auth key.
#   Go to https://{{ get_core_config()['site']['domain'] }}/account/preferences to set your upload auth key.

USERNAME=''
AUTH=''

FILENAME="$(date +%s)-$((RANDOM%100000+999999)).png"
IMGPATH="~/Screenshots/$FILENAME"


if [ "$1" == "full" ]; then
    MODE=""
elif [ "$1" == "active" ]; then
    MODE="-u"
elif [ "$1" == "selection" ]; then
    MODE="-s"
else
    FILENAME=$1
    notify-send "{{ get_core_config()['site']['branding'] }} Upload" "Upload of file '$FILENAME' started."
    res=$(curl -s -F "file=@$FILENAME" "https://{{ get_core_config()['site']['domain'] }}/functions/upload/external?username=$USERNAME&auth=$AUTH")
    echo $res | xclip -sel clip
    notify-send "{{ get_core_config()['site']['branding'] }} Upload" $res
    exit
fi

scrot $MODE -z $IMGPATH || exit
notify-send "{{ get_core_config()['site']['branding'] }} Upload" "Upload of file '$FILENAME' started."
res=$(curl -s -F "file=@$IMGPATH" "https://{{ get_core_config()['site']['domain'] }}/functions/upload/external?username=$USERNAME&auth=$AUTH")
echo $res | xclip -sel clip
notify-send "{{ get_core_config()['site']['branding'] }} Upload" $res