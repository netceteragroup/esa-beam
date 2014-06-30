#!/bin/bash

FILE="$@"
DIR="$(dirname "$FILE" | sed "s/\\//\\\\\\//g")"

if [ -z "$FILE" ]
then
    echo "$0: filename must be specified" > /dev/stderr
    exit 1;
elif [ ! -f "$FILE" ]
then
    echo "$0: file not found \`${FILE}'" > /dev/stderr
    exit 1;
fi

sed -r -i.bak \
    -e "s/srm [A-Za-z0-9_\\-\.]+ /&${DIR}\\//" \
    -e "s/matmap [A-Za-z0-9_\\-\.]+ /&${DIR}\\//" \
    -e "s/#include /&${DIR}\\//" \
    -e "s/mtllib /&${DIR}\\//" \
    -e "s/-filename /&${DIR}\\//" \
    "$FILE"

