#!/usr/bin/bash
# JMESPATH:
# pip install jmespath-terminal
# JQUERY
# sudo dnf install -y jq
set -e
REPO_NAME="rook/rook"
DAYS=1  # Cache in Days
URL="https://api.github.com/repos/$REPO_NAME/releases"

CACHE_DIR="$HOME/.cache/releases/$REPO_NAME"
CACHE_FILE="$CACHE_DIR/json"

[ -d "$CACHE_DIR" ] || mkdir -p "$CACHE_DIR"
CURRENT_EPOCH=$(date +'%s')
if [ -f "$CACHE_FILE"  ]; then
  EPOCH=$(stat "$CACHE_FILE" --format "%W")

  DIFF=$(($CURRENT_EPOCH - $EPOCH))
  MAX=$(( 24 * 3600 * $DAYS))
  if [ $DIFF -gt $MAX ]; then
    rm -f "$CACHE_FILE"
  fi
fi

if [ ! -f "$CACHE_FILE"  ]; then
  curl -o "$CACHE_FILE" -L "$URL"
fi

VERSION=$(cat $CACHE_FILE | jq -r ".[0].name")
echo $VERSION
if [ "$1" == "-d" ]; then
  URL=$(cat $CACHE_FILE | jq -r ".[0].tarball_url" )
  curl --silent -OL --remote-header-name "$URL"
fi
