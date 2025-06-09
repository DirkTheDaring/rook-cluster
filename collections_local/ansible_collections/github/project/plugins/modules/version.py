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
#import urllib3.request
import requests
import yaml
import time
import re
import json
#import sys

GITHUB_PROJECT_NAME="name"
GITHUB_PROJECT_VERSION="version"
CACHE_TIME="cache_time"
ASSET_NAME="asset_name"
#FILTER_BY_NAME="filter_by_name"

class HttpException(Exception):
    "Raised when response status != 200 "
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

class VersionException(Exception):
    "Raised when no version found"
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

class AssetNotFoundException(Exception):
    "Raised when asset matches"
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg


def is_cachefile_expired_epoch(filename, maximum):
    current_epoch = time.time()
    epoch = os.stat(filename).st_ctime
    diff = current_epoch - epoch
    return (diff > maximum)

def is_cachefile_expired(filename, days):
    maximum = 24 * 3600 * days
    return is_cachefile_expired_epoch(filename, maximum)

def download_file(url, cache_file):
    resp = requests.get(url)

    if resp.status_code != 200:
        raise HttpException(f'URL {url} returned: {resp.status_code}')

    try:
        data = resp.json()
    except json.JSONDecodeError:
        raise HttpException(f"Invalid JSON returned from GitHub: {resp.text[:200]}")

    with open(cache_file, 'w') as out:
        json.dump(data, out)

def load_json(cache_file):
    with open(cache_file, 'r') as fp:
        data = json.load(fp)
    return data

def get_keys(container, keyname):
    _list = []
    for item in container:
        name = item[keyname]
        name = name.strip()
        if name == "":
            continue
        _list.append(name)
    return _list

def extract_project(project_name):
    github_prefix = "https://github.com/"
    api_prefix = "https://api.github.com/repos/"
    if project_name.startswith(github_prefix):
        start = len(github_prefix)
        project_name = project_name[start:]
    elif project_name.startswith(api_prefix):
        start = len(api_prefix)
        project_name = project_name[start:]

    array = project_name.split("/")
    if len(array) < 2:
        return ""
    return array[0] + "/" + array[1]

def get_object_by_key(dicts, key, search_value):
    for item in dicts:
        value = item[key]
        if value == search_value:
            return item
    return None

def filter_list(_list, filter):

    if filter == "":
        return _list

    filtered_list = []

    if filter.startswith("~"):
        regex = filter[1:]
        regexc = re.compile(regex)
        for item in _list:
            if not regexc.match(item):
                continue
            filtered_list.append(item)
        return filtered_list

    for item in _list:
        if item == filter:
            filtered_list.append(item)
    return filtered_list

def last_of_nat_sorted_list(_list):
    natsort = lambda s: [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]
    sorted_list = sorted(_list, key=natsort)
    return sorted_list[-1]

def project_version(config):
    version = config[GITHUB_PROJECT_VERSION]

    # extract regex from version string by convention. When the string starts with ~
    # then it is a regex
    regex = ""
    if version.startswith("~"):
        regex = version[1:]

    project_name = config[GITHUB_PROJECT_NAME]
    project_name = extract_project(project_name)
    if project_name == "":
        return ("", "", "")

    cache_dir = os.environ['HOME'] + "/.cache/github-releases/" + project_name
    cache_file = cache_dir + "/releases.json"

    if not os.path.isdir(cache_dir):
        os.makedirs( cache_dir , 0o0755 )

    cache_time = config[CACHE_TIME]

    if os.path.isfile(cache_file) and is_cachefile_expired(cache_file, cache_time):
        os.remove(cache_file)

    url = "https://api.github.com/repos/" + project_name + "/releases"

    if not os.path.isfile(cache_file):
        download_file(url, cache_file)

    repos = load_json(cache_file)

    versions = get_keys(repos, 'tag_name')

    filtered_versions = filter_list(versions, version)

    if len(filtered_versions) == 0:
        raise VersionException("No version matched out of: " + str(versions))

    version = last_of_nat_sorted_list(filtered_versions)

    repo = get_object_by_key(repos, 'tag_name', version)

    if not 'assets' in repo:
        return (version, '', '')

    assets = repo['assets']

    if len(assets) ==  0:
        return (version, '', '')

    names = get_keys(assets, 'name')

    if len(names) == 0:
        return (version, '', '')

    asset_name = config[ASSET_NAME]

    filtered_names = filter_list(names, asset_name)

    if len(filtered_names) == 0:
        raise AssetNotFoundException("No asset matched out of: " + str(names))

    if len(filtered_names) == 1:
        name = filtered_names[0]
    else:
        name = last_of_nat_sorted_list(names)

    asset = get_object_by_key(assets, 'name', name)

    if not 'browser_download_url' in asset:
        return (version, name, "")

    url = asset['browser_download_url']
    return (version, name, url)

def run_module():

    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        name=dict(type='str', required=True),
        version=dict(type='str', required=False, default=""),
        cache_time=dict(type='int', required=False, default=1),
        asset_name=dict(type='str', required=False, default="")
    )
    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        ansible_facts=dict()
    )
        #github_project_version='',

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

    try:
        version, asset_name,url = project_version(module.params)
        #result['github_project_version'] = version
        result['ansible_facts'] = {
            'github_project_version': version,
            'github_asset_name': asset_name,
            'github_download_url': url
        }
    except HttpException as e:
        module.fail_json(msg=str(e), **result)
        return
    except VersionException as e:
        module.fail_json(msg=str(e), **result)
    except AssetNotFoundException as e:
        module.fail_json(msg=str(e), **result)


    #result['original_message'] = module.params['url']

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
