#!/usr/bin/bash
# JMESPATH:
# pip install jmespath-terminal
# JQUERY
# sudo dnf install -y jq

# helm repo    add bitnami https://charts.bitnami.com/bitnami
# helm install postgresql bitnami/postgresql

set -e
URL=https://charts.bitnami.com/bitnami
REPO_NAME=postgresql
NAME=postgresql

DAYS=1  # Cache in Days

CACHE_DIR="$HOME/.cache/helm-releases/$REPO_NAME"
CACHE_FILE="$CACHE_DIR/yaml"
yaml2json()
{
  python3 -c 'import sys, yaml, json; y=yaml.safe_load(sys.stdin.read()); print(json.dumps(y))'
}

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
  curl -o "$CACHE_FILE" -L "$URL/index.yaml"
fi

CACHE_FILE_JSON=$CACHE_DIR/json

if [ "$CACHE_FILE" -nt "$CACHE_FILE_JSON" ];then
  cat "$CACHE_FILE"| yaml2json >"$CACHE_FILE_JSON"
fi


JQUERY='reduce (.entries."'$NAME'"[].version) as $item ([]; . + [$item])'
cat "$CACHE_FILE_JSON"\
| jq -r '.entries."'$NAME'"[].version' \
| head -1

JMESPATH='entries."'$NAME'"[].version|[0]'
cat "$CACHE_FILE_JSON"\
| jp.py "$JMESPATH"
