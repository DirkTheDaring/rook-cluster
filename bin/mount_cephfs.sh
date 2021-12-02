#!/usr/bin/bash
#set -x
if [ "$1" == "" ]; then
  echo "need rook/config.json"
  exit 1
fi 
if [ "$2" == "" ]; then
  echo "need mountpoint. e.g. /opt/ceph"
  exit 2
fi 
JSON=$(cat "$1")
MNT=$2
ROOK_EXTERNAL_CEPH_MON_DATA=$(jq -r ".rook_external_ceph_mon_data" <<< "$JSON")
ROOK_EXTERNAL_CEPH_MON_DATA=${ROOK_EXTERNAL_CEPH_MON_DATA//[a-c]=/}
ROOK_EXTERNAL_ADMIN_SECRET=$(jq -r ".rook_external_admin_secret" <<<"$JSON")

mkdir -p "$MNT"
sudo mount -t ceph -o mds_namespace=ceph-filesystem,name=admin,secret=$ROOK_EXTERNAL_ADMIN_SECRET $ROOK_EXTERNAL_CEPH_MON_DATA:/ "$MNT"
