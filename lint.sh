#!/usr/bin/env bash
# only with these environment variables the collections_local and the filter_plugins are found
export ANSIBLE_COLLECTIONS_PATHS=./collections_local:./collections
export ANSIBLE_FILTER_PLUGINS=./filter_plugins
exec ansible-lint
