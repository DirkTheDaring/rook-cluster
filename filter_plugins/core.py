import re
import sys

import yaml


def escape(mystring):
    mystring = mystring.replace(".", "\.")
    mystring = mystring.replace("/", "\/")
    return mystring


def recursive(value, data, path=""):
    if isinstance(value, list):
        i = 0
        for item in value:
            recursive(item, data, path + "[" + str(i) + "]")
            i = i + 1
        return
    elif isinstance(value, dict):
        for key in value.keys():
            recursive(value[key], data, path + "." + escape(str(key)))
        return
    data[path[1:]] = value
    return


# values must be of type string (argo application) --> escape all values with ""
def render_application_section(data, n=8, prefix_str=" "):
    content = ""
    prefix = n * prefix_str

    for item in data:
        key = item[0]
        value = str(item[1])
        force_str = item[2]
        content = content + prefix + "- name: " + key + "\n" + prefix + "  value: "
        if "\n" in value:
            content = content + "|\n"
            lines = value.split("\n")
            line_prefix = (n + 4) * prefix_str
            for line in lines:
                content = content + line_prefix + line + "\n"
        elif "\\" in value or '"' in value:
            value = value.replace("\\", "\\\\")
            value = value.replace('"', '\\"')
            content = content + '"' + value + '"\n'
        else:
            content = content + '"' + value + '"\n'
            if force_str:
                # if value.isnumeric():
                content = content + prefix + "  forceString: true\n"
    return content


def chart_values_to_argo_parameters(
    dictionary, force_string_dict={}, prune_none_value_flag=True, n=8, prefix_str=" "
):
    data = {}
    recursive(dictionary, data, path="")
    # Backward compatibility
    if isinstance(force_string_dict, list):
        force_string_dict = {"path_list": force_string_dict}

    compiled = []
    path_list = []
    if "path_list" in force_string_dict:
        path_list = force_string_dict["path_list"]

    if "path_regex_list" in force_string_dict:
        path_regex_list = force_string_dict["path_regex_list"]
        for pattern in path_regex_list:
            # print("pattern=" + pattern)
            prog = re.compile(pattern)
            compiled.append(prog)

    result = []
    for key, value in list(data.items()):
        force_str = False
        if prune_none_value_flag and value is None:
            continue
        else:
            value = str(value)

        if key in path_list:
            force_str = True

        for regex in compiled:
            ok = regex.match(key)
            # print(ok , key, regex)
            if ok:
                # print("!! match >> " + key)
                force_str = True

        result.append([key, value, force_str])

    content = render_application_section(result, n, prefix_str)

    return content


# prune only leaves with NoneObject
def prune_none_value_only_leaves(_dict):
    if not _dict:
        return _dict

    for key, value in list(_dict.items()):
        if isinstance(value, dict):
            prune_none_value_only_leaves(value)
        elif value is None:
            del _dict[key]
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    prune_none_value_only_leaves(item)
    return _dict


# prune path which contain None Objects and if they leave empty parent dicts remove them too
def __prune_none_value_with_pathes(_dict, preserve_existing_empty_dict=False):
    if isinstance(_dict, dict):
        for key, value in list(_dict.items()):
            # if there is already an existing empty dict ( ==  {} ) we leave it untouched
            if (
                preserve_existing_empty_dict
                and isinstance(value, dict)
                and len(value) == 0
            ):
                continue
            if __prune_none_value_with_pathes(value, preserve_existing_empty_dict):
                del _dict[key]
        if len(_dict) == 0:
            return True

    elif isinstance(_dict, list):
        for value in _dict:
            if isinstance(value, dict):
                __prune_none_value_with_pathes(value, preserve_existing_empty_dict)

    elif _dict is None:
        return True

    return False


def prune_none_value_with_pathes(_dict, preserve_existing_empty_dict=False):
    __prune_none_value_with_pathes(_dict, preserve_existing_empty_dict)
    return _dict


class FilterModule(object):
    def filters(self):
        return {
            "prune_none_value": prune_none_value_with_pathes,
            "prune_none_value_with_pathes": prune_none_value_with_pathes,
            "prune_none_value_only_leaves": prune_none_value_only_leaves,
            "chart_values_to_argo_parameters": chart_values_to_argo_parameters,
        }
