# Copyright (c) 2015 Mirantis, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import six


def get_dict_from_output(output):
    """Parse list of dictionaries, return a dictionary.

    :param output: list of dictionaries
    """
    obj = {}
    for item in output:
        obj[item['Property']] = six.text_type(item['Value'])
    return obj


def get_object(object_list, object_value):
    """Get Ironic object by value from list of Ironic objects.

    :param object_list: the output of the cmd
    :param object_value: value to get
    """
    for obj in object_list:
        if object_value in obj.values():
            return obj
