#!/usr/bin/bash
# last test v1.7.7
NAMESPACE=rook-ceph
# Delete all secrets and configmaps in order to a new rolled out ceph server, with new credentials

kubectl -n $NAMESPACE delete secrets\
 rgw-admin-ops-user\
 rook-ceph-mon\
 rook-csi-cephfs-node\
 rook-csi-cephfs-provisioner\
 rook-csi-rbd-node\
 rook-csi-rbd-provisioner

kubectl -n $NAMSEPACE delete configmaps\
  rook-ceph-mon-endpoints
