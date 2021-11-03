#!/usr/bin/bash
set -ex
DIRNAME=$(dirname "$0")
cd "$DIRNAME/.."
LIST=$(find credentials/ -name web.json)

for FILE in $LIST; do
URL=$(cat $FILE |jq -r ".url")
USERNAME=$(cat $FILE |jq -r .username)
PASSWORD=$(cat $FILE |jq -r .password)

cat<<EOF

-----------------------------------------------------------------------------
URL:      $URL
USERNAME: $USERNAME
PASSWORD: $PASSWORD
EOF
done
