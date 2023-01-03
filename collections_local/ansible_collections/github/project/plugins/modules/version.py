#!/usr/bin/python
#from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: my_test

short_description: This is my test module

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: This is my longer description explaining my test module.

options:
    name:
        description: This is the message to send to the test module.
        required: true
        type: str
    new:
        description:
            - Control to demo if the result of this module is changed or not.
            - Parameter description can be a list as well.
        required: false
        type: bool
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - my_namespace.my_collection.my_doc_fragment_name

author:
    - Your Name (@yourGitHubHandle)
'''

EXAMPLES = r'''
# Pass in a message
- name: Test with a message
  my_namespace.my_collection.my_test:
    name: hello world

# pass in a message and have changed true
- name: Test with a message and changed output
  my_namespace.my_collection.my_test:
    name: hello world
    new: true

# fail the module
- name: Test failure of the module
  my_namespace.my_collection.my_test:
    name: fail me
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original name param that was passed in.
    type: str
    returned: always
    sample: 'hello world'
message:
    description: The output message that the test module generates.
    type: str
    returned: always
    sample: 'goodbye'
'''

from ansible.module_utils.basic import AnsibleModule
import os
import urllib.request
import yaml
import time
import re
import json

GITHUB_PROJECT_NAME="name"
GITHUB_PROJECT_VERSION="version"
CACHE_TIME="cache_time"

def is_cachefile_expired_epoch(filename, maximum):
    current_epoch = time.time()
    epoch = os.stat(filename).st_ctime
    diff = current_epoch - epoch
    return (diff > maximum)

def is_cachefile_expired(filename, days):
    maximum = 24 * 3600 * days
    return is_cachefile_expired_epoch(filename, maximum)

def project_version(config):
    version = config[GITHUB_PROJECT_VERSION]

    regex = ""
    if version.startswith("~"):
        regex = version[1:]
    elif version != "":
        return version

    project_name = config[GITHUB_PROJECT_NAME]
    prefix = "https://api.github.com/repos/"
    if project_name.startswith(prefix):
        array = project_name[len(prefix):].split("/")
        if len(array) > 1:
            project_name = array[0] + "/" + array[1]
        else:
           return ""

    cache_dir = os.environ['HOME'] + "/.cache/github-releases/" + project_name
    cache_file = cache_dir + "/releases.json"

    if not os.path.isdir(cache_dir):
        os.makedirs( cache_dir , 0o0755 )

    cache_time = config[CACHE_TIME]

    if os.path.isfile(cache_file) and is_cachefile_expired(cache_file, cache_time):
        os.remove(cache_file)

    url = "https://api.github.com/repos/" + project_name + "/releases"

    if not os.path.isfile(cache_file):
        urllib.request.urlretrieve(url, cache_file)

    with open(cache_file, 'r') as fp:
        repos=json.load(fp);

    versions=[]
    # strip addeded names, as we found an occation in v0.13.7 of metallb which
    # has a leading space

    if regex != "":
        regexc = re.compile(regex)
        for repo in repos:
            name = repo['name']
            if regexc.match(name):
                 versions.append(name.strip())
    else:
        for repo in repos:
            versions.append(repo['name'].strip())

    if len(versions) == 0:
        return ""

    natsort = lambda s: [int(t) if t.isdigit() else t.lower() for t in re.split("(\d+)", s)]
    result = sorted(versions,key=natsort)

    return result[len(result)-1]

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        name=dict(type='str', required=True),
        version=dict(type='str', required=False, default=""),
        cache_time=dict(type='int', required=False, default=1)
    )
    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        github_project_version='',
        ansible_facts=dict()
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    version = project_version(module.params)

    #result['original_message'] = module.params['url']
    result['github_project_version'] = version
    result['ansible_facts'] = { 'github_project_version': version }

    # use whatever logic you need to determine whether or not this module
    # made any modifications to your target
    #if module.params['new']:
    #    result['changed'] = True

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    #if module.params['name'] == 'fail me':
    #    module.fail_json(msg='You requested this to fail', **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
