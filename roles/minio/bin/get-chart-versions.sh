#!/usr/bin/bash
# JMESPATH:
# pip install jmespath-terminal

# JQUERY
# sudo dnf install -y jq
set -e

yaml2json()
{
  python3 -c 'import sys, yaml, json; y=yaml.safe_load(sys.stdin.read()); print(json.dumps(y))'
}

URL=https://charts.bitnami.com/bitnami
NAME=minio

#JSON=$(curl -s "$URL/index.yaml"| python3 -c 'import sys, yaml, json; y=yaml.safe_load(sys.stdin.read()); print(json.dumps(y))')
YAML=$(curl -s "$URL/index.yaml")
JSON=$(echo "$YAML"| yaml2json)
#JSON=$(cat chart.json)

JMESPATH='entries."'$NAME'"[].version'
echo $JSON\
| jp.py "$JMESPATH"

JQUERY='reduce (.entries.'$NAME'[].version) as $item ([]; . + [$item])'
echo $JSON\
| jq "$JQUERY"

