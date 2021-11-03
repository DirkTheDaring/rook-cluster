#!/bin/sh
set -x
helm repo add bitnami https://charts.bitnami.com/bitnami

helm uninstall --namespace minio minio 
DEBUG=
#DEBUG=--debug
# drwxrwx---  1  1001 root   64 Oct 13 23:10 minio.prod1
helm install $DEBUG --namespace minio --create-namespace minio bitnami/minio\
 --version 8.1.9\
 --set ingress.enabled=true\
 --set ingress.hostname=minio.office.kaupon.de\
 --set        'ingress.annotations.traefik\.ingress\.kubernetes\.io/router\.entrypoints=websecure'\
 --set-string 'ingress.annotations.traefik\.ingress\.kubernetes\.io/router\.tls=true'\
 --set apiIngress.enabled=true\
 --set apiIngress.hostname=minio-api.office.kaupon.de\
 --set 'apiIngress.annotations.traefik\.ingress\.kubernetes\.io/router\.entrypoints=websecure'\
 --set-string 'apiIngress.annotations.traefik\.ingress\.kubernetes\.io/router\.tls=true'\


