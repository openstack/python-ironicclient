# -*- encoding: utf-8 -*-
#
# Copyright 2013 Hewlett-Packard Development Company, L.P.
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

from ironicclient.common import base
from ironicclient import exc


CREATION_ATTRIBUTES = ['chassis_id', 'driver', 'driver_info', 'extra',
                       'node_id', 'properties']


class Node(base.Resource):
    def __repr__(self):
        return "<Node %s>" % self._info


class NodeManager(base.Manager):
    resource_class = Node

    @staticmethod
    def _path(id=None):
        return '/v1/nodes/%s' % id if id else '/v1/nodes'

    def list(self):
        return self._list(self._path(), "nodes")

    def list_ports(self, node_id):
        path = "%s/ports" % node_id
        return self._list(self._path(path), "ports")

    def get(self, node_id):
        try:
            return self._list(self._path(node_id))[0]
        except IndexError:
            return None

    def create(self, **kwargs):
        new = {}
        for (key, value) in kwargs.items():
            if key in CREATION_ATTRIBUTES:
                new[key] = value
            else:
                raise exc.InvalidAttribute()
        return self._create(self._path(), new)

    def delete(self, node_id):
        return self._delete(self._path(node_id))

    def update(self, node_id, patch):
        return self._update(self._path(node_id), patch)

    def set_power_state(self, node_id, state):
        path = "%s/state/power" % node_id
        target = {'target': "power %s" % state}
        return self._update(self._path(path), target, method='PUT')
