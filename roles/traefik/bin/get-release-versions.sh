#!/usr/bin/bash
# JMESPATH:
# pip install jmespath-terminal
# JQUERY
# sudo dnf install -y jq
set -ex
REPO_NAME="traefik/traefik"
URL="https://api.github.com/repos/$REPO_NAME/releases"

CACHE_DIR="$HOME/.cache/releases/$REPO_NAME"
CACHE_FILE="$CACHE_DIR/json"

[ -d "$CACHE_DIR" ] || mkdir -p "$CACHE_DIR"

if [ ! -f "$CACHE_FILE"  ]; then
  curl -o "$CACHE_FILE" -L "$URL"
fi

VERSION=$(cat $CACHE_FILE | jq -r ".[].name" | grep "^v2" |head -1)
echo $VERSION
exit 0
if [ "$1" == "-d" ]; then 
  URL=$(cat $CACHE_FILE | jq -r ".[0].tarball_url" )
  curl --silent -OL --remote-header-name "$URL"
fi
