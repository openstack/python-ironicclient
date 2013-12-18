# Copyright 2012 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Base utilities to build API operation managers and objects on top of.
"""

import copy

from ironicclient.openstack.common.apiclient import base


def getid(obj):
    """Abstracts the common pattern of allowing both an object or an
    object's ID (UUID) as a parameter when dealing with relationships.
    """
    try:
        return obj.id
    except AttributeError:
        return obj


class Manager(object):
    """Managers interact with a particular type of API and provide CRUD
    operations for them.
    """
    resource_class = None

    def __init__(self, api):
        self.api = api

    def _create(self, url, body):
        resp, body = self.api.json_request('POST', url, body=body)
        if body:
            return self.resource_class(self, body)

    def _list(self, url, response_key=None, obj_class=None, body=None):
        resp, body = self.api.json_request('GET', url)

        if obj_class is None:
            obj_class = self.resource_class

        if response_key:
            try:
                data = body[response_key]
            except KeyError:
                return []
        else:
            data = body
        if not isinstance(data, list):
            data = [data]

        return [obj_class(self, res, loaded=True) for res in data if res]

    def _update(self, url, body, method='PATCH', response_key=None):
        resp, body = self.api.json_request(method, url, body=body)
        # PATCH/PUT requests may not return a body
        if body:
            return self.resource_class(self, body)

    def _delete(self, url):
        self.api.raw_request('DELETE', url)


class Resource(base.Resource):
    """A resource represents a particular instance of an object (tenant, user,
    etc). This is pretty much just a bag for attributes.
    """

    def to_dict(self):
        return copy.deepcopy(self._info)
