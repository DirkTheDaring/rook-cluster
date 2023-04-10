Adding certififcates proved to be challening, as we do not want to add a tls certificate, but a root ca.
So any option in the current helm chart fails, as it tries to activate tls options also in the ingress and other things.

The only solution which seems to work is with trick, that we start
with a docker image copy the cacerts file, add the keyas and then mount this
as an replacement for existing file. and then mount this again

(1) cp -ar /opt/bitnami/java/lib/security/ /tmp destination
(2) add certifiactes to cert with keytool
(3) use a second initcontainer to make this result root again
(4) remount the security dir with the added keys

Now Java should trust the added ca from start and we finally can run this stuff in the intranet

default pass is "changeit"
cp -a /opt/bitnami/java/lib/security/cacerts /tmp
keytool -keystore cacerts -storepass changeit -list
keytool -keystore cacerts -storepass changeit -import -alias testCert -file /usr/local/share/ca-certificates/self-signed-certificate.crt -noprompt

Testing
Found it useful to test it
https://matthewdavis111.com/java/poke-ssl-test-java-certs/
https://stackoverflow.com/questions/5871279/ssl-and-cert-keystore
