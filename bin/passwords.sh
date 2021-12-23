#!/usr/bin/bash
set -e
DIRNAME=$(dirname "$0")
cd "$DIRNAME/.."
LIST=$(find credentials/ -name web.json)

for FILE in $LIST; do
#echo $FILE
URL=$(jq -r ".url" "$FILE")
USERNAME=$(jq -r .username "$FILE")
PASSWORD=$(jq -r .password "$FILE")

cat<<EOF

-----------------------------------------------------------------------------
URL:      $URL
USERNAME: $USERNAME
PASSWORD: $PASSWORD
EOF
done
