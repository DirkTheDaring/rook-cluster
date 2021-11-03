#!/usr/bin/bash
set -e
export ACCESS_KEY=$(kubectl get secret --namespace minio minio -o jsonpath="{.data.access-key}" | base64 --decode)
export SECRET_KEY=$(kubectl get secret --namespace minio minio -o jsonpath="{.data.secret-key}" | base64 --decode)

echo username: $ACCESS_KEY
echo password: $SECRET_KEY

