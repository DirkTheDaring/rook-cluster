#!/bin/sh
# JMESPATH:
# pip install jmespath-terminal
# JQUERY
# sudo dnf install -y jq

set -ex
URL="https://api.github.com/repos/minio/minio"
MATCH="RELEASE.2021-05"
#MATCH=""

#CONTENT="curl -s $URL/releases"
#$CONTENT >releases.json
CONTENT="cat releases.json"

JMESPATH="[?starts_with(tag_name, '${MATCH}')]|[].tag_name"
JMESPATH="[].tag_name"
$CONTENT\
|jp.py "$JMESPATH"

JQUERY='reduce (.[]|select(.tag_name|startswith("'$MATCH'"))|.tag_name) as $item ([]; . + [$item] )'
$CONTENT\
| jq "$JQUERY"

#|jq --arg match "$MATCH" 'reduce (.[]|select(.tag_name|startswith($match))|.tag_name) as $item ([]; . + [$item] )'
#| jq  'reduce .[].tag_name as $item ([]; . + [$item] )'\
#| jq -r 'map(.tag_name)'
#| jq -r 'map(.tag_name)[0]'

