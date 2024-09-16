
# INSTALL
pip install kubernetes


# rook-cluster
create rook cluster for storage and a separate cluster as client


releases before helm charts in order to override helm charts if they use an older version

if you use certificates in your container you MUST manage their life cycle
a) Normal life cycle , determine end of certificate and exchange it
b) Security life cycle, exchange certficate on incident
c

# Callback from gitlab
https://argoproj.github.io/argo-events/eventsources/setup/gitlab/


FIXME:
* write a test for traefik, which checks the nameserver really resolves a domain
  (e.g. in my case the nameserver suddenly only answered with forbidden, because the provider switched to a new dns, which i had to find out)


FIXME OIDC for vault
https://www.vaultproject.io/docs/auth/jwt/oidc_providers

FIXME OIDC for vault with DEX
https://discuss.hashicorp.com/t/configuring-a-dex-oidc-auth-provider/23124

# https://argocd.office.kaupon.de/api/dex/.well-known/openid-configuration
# needs to be passed with .well-known--

vault auth enable oidc

vault write auth/oidc/config \
   oidc_client_id="argocd-repo-creds-vault-prod-sso" \
   oidc_client_secret="019d7e3e-2ccc-43b6-918d-76cfca384497" \
   default_role="your_default_role" \
   oidc_discovery_url="https://argocd.office.kaupon.de/api/dex"

vault write auth/oidc/role/your_default_role \
   user_claim="email" \
   allowed_redirect_uris="http://localhost:8250/oidc/callback,https://vault.office.kaupon.de/ui/vault/auth/oidc/oidc/callback"  \
   groups_claim="groups" \
   oidc_scopes="openid,profile,offline_access,email,groups" \
   policies=default

vault read auth/oidc/config


# Version
https://docs.ansible.com/ansible/latest/user_guide/playbooks_tests.html#comparing-versions


FIXME
vault has a wrong Active Node... this should be fixed by deleting all nodes

> vault status
Key                     Value
---                     -----
Seal Type               shamir
Initialized             true
Sealed                  false
Total Shares            5
Threshold               3
Version                 1.12.1
Build Date              2022-10-27T12:32:05Z
Storage Type            raft
Cluster Name            vault-cluster-be9bb80b
Cluster ID              1534a10f-5f71-dba4-2817-88269978cb2e
HA Enabled              true
HA Cluster              https://vault-1.vault-internal:8201
HA Mode                 standby
Active Node Address     http://10.233.67.103:8200
Raft Committed Index    443
Raft Applied Index      443


# https://github.com/databus23/helm-diff
helm plugin install https://github.com/databus23/helm-diff


# Rook Ceph CRD which can change ceph-mon
https://documentation.suse.com/de-de/ses/7/html/ses-all/admin-caasp-crd.html
  mon:
    count: 3
    volumeClaimTemplate:
      spec:
        storageClassName: local-storage
        resources:
          requests:
            storage: 10Gi

# how to keep certain things and not delete it afterwards
   "helm.sh/resource-policy": "keep"
