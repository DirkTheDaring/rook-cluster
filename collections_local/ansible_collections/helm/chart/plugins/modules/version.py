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

from pathlib import Path
from typing import Dict, List, Union, Any
from dataclasses import dataclass


# Just played around with the parameter names
REPO_NAME="repo_name"
REPO_URL="repo_url"
CHART_NAME="name"
CHART_VERSION="version"
CACHE_TIME="cachetime"

CACHE_DIR = Path.home() / ".cache" / "helm-releases"
CACHE_FILE = "index.yaml"


class HttpException(Exception):
    "Raised when response status != 200 "
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg


@dataclass
class Config:
    repo_name: str
    repo_url: str
    name: str
    version: str
    cachetime: int = 1 # days

class CacheManager:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.cache_dir = CACHE_DIR / self.config.repo_name / self.config.name
        self.cache_file = self.cache_dir / CACHE_FILE

    def is_expired(self) -> bool:
        return not self.cache_file.exists() or time.time() - self.cache_file.stat().st_ctime > 24 * 3600 * self.config.cachetime

    def clear_expired_cache(self) -> None:
        if self.is_expired():
            self.cache_file.unlink(missing_ok=True)

    def ensure_cache(self, data: bytes) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file.write_bytes(data)

class HelmRelease:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.cache_manager = CacheManager(config)

    def fetch_repo_data(self) -> Dict[str, Any]:
        self.cache_manager.clear_expired_cache()

        if not self.cache_manager.cache_file.exists():
            data = requests.get(f"{self.config.repo_url}/{CACHE_FILE}").content
            self.cache_manager.ensure_cache(data)

        with self.cache_manager.cache_file.open() as f:
            return yaml.safe_load(f)

    @staticmethod
    def natural_sort(s: str) -> List[Union[int, str]]:
        return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]

    def get_latest_version(self) -> str:
        version = self.config.version

        if version == "":
            version = "~[0-9]+\\.[0-9]+\\.[0-9]+$"

        if not version.startswith("~"):
            return version

        repo_data = self.fetch_repo_data()
        chart_data = repo_data.get('entries', {}).get(self.config.name, [])

        if not chart_data:
            return f"Chart {self.config.name} not found in repo data"

        versions = [repo['version'] for repo in chart_data if 'version' in repo]

        if version.startswith("~"):
            regex = re.compile(version[1:])
            versions = [v for v in versions if regex.match(v)]
        #print(sorted(versions, key=self.natural_sort))
        return sorted(versions, key=self.natural_sort)[-1] if versions else "No valid versions found"


def chart_version(params) -> str:
    config = Config(
        params['repo_name'],
        params['repo_url'],
        params['name'],
        params['version'],
    )

    version = HelmRelease(config).get_latest_version()
    return version


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        repo_name=dict(type='str', required=True),
        repo_url=dict(type='str', required=True),
        name=dict(type='str', required=True),
        version=dict(type='str', required=False, default=""),
        cachetime=dict(type='int', required=False, default=1)
    )
    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        chart_version='',
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
    try:

        version = chart_version(module.params)
        #result['original_message'] = module.params['url']
        result['helm_chart_version'] = version
        result['ansible_facts'] = { 'helm_chart_version': version }
    except HttpException as e:
        module.fail_json(msg=str(e), **result)
        return

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
