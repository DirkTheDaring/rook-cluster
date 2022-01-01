#!/usr/bin/bash
set -ex
# Requires: 
# pip install --user kubernetes

ANSIBLE_MIN_VERSION=2.11.5

check_ansible_min_version()
{
  local MIN_VERSION=$1
  # old version string: ansible 2.9.27
  # new version string  ansible [core 2.11.6]
  local VERSION=($(ansible --version | grep -m1 '^ansible ' | awk 'match($0,/([0-9]+\.[0-9]+\.[0-9]+)/,a) {print a[1]}'))
  local VERSION_ARRAY=($(echo $VERSION|sed 's/\./ /g'))
  local MIN_VERSION_ARRAY=($(echo $MIN_VERSION|sed 's/\./ /g'))
  #  at least mininum version of ansible, otherwise endless troubles with collections!
  OK=0
  if  [      ${VERSION_ARRAY[0]} -ge ${MIN_VERSION_ARRAY[0]} ]\
        && [ ${VERSION_ARRAY[1]} -ge ${MIN_VERSION_ARRAY[1]} ]\
        && [ ${VERSION_ARRAY[2]} -ge ${MIN_VERSION_ARRAY[2]} ]; then
     OK=1
  fi

  if [ $OK == 0 ]; then
    echo "install at least ansible version $MIN_VERSION, current: $VERSION"
    echo "e.g. pip install -U ansible"
    echo "# make sure that you then your path set and also removed any other ansible"
    return 1
  fi
  return 0
}

BASENAME=$(basename -s .sh "$0")
DIRNAME=$(dirname "$0")
REALPATH=$(realpath "$0")

cd "$DIRNAME"
ARRAY=(${BASENAME//-/ })

CONFIG_NAME=${ARRAY[1]}
CONFIG_STAGE=${ARRAY[2]}

if [ -z "${ARRAY[3]}" ]; then
  PLAYBOOK=playbook.yaml
else
  PLAYBOOK=playbook-${ARRAY[3]}.yaml
fi

KUBECONFIG=${KUBECONFIG:="$HOME/.kube/admin.conf.$CONFIG_STAGE"}
if [ ! -f "$KUBECONFIG" ]; then
  echo "file reference in KUBECONFIG($KUBECONFIG) does not exist."
  exit 1
fi
export KUBECONFIG

check_ansible_min_version "$ANSIBLE_MIN_VERSION"

#ansible-galaxy collection install --force -r collections/requirements.yml 
ansible-galaxy collection install -r collections/requirements.yml 

INVENTORY_DIR=inventory/$CONFIG_NAME/$CONFIG_STAGE
if [ ! -d "$INVENTORY_DIR" ]; then
    echo inventory directory does not exist: $INVENTORY_DIR
    exit 1
fi
#export ANSIBLE_LIBRARY=$(realpath "$DIRNAME/modules")
ansible-playbook "$PLAYBOOK" -e config_name=$CONFIG_NAME -e config_stage=$CONFIG_STAGE -i "$INVENTORY_DIR" $*
