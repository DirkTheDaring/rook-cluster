#!/bin/sh
curl -s  https://helm.traefik.io/traefik/index.yaml |\
python3 -c 'import sys, yaml, json; y=yaml.safe_load(sys.stdin.read()); print(json.dumps(y))'|
jq -r  '.entries.traefik[].version'   


