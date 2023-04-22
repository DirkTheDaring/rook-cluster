# Cannot login?
# Reset password
# Enable user (after 10 failed attempts!)


$ echo -n "xxx" >/tmp/x
$ ceph dashboard ac-user-set-password admin -i /tmp/x
{"username": "admin", "password": "--not-shown--", "roles": ["administrator"], "name": null, "email": null, "lastUpdate": 1681560339, "enabled": false, "pwdExpirationDate": null, "pwdUpdateRequired": false}

#  it happened that the user was locked out!!!
ceph dashboard ac-user-enable admin
