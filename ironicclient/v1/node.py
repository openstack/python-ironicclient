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

CREATION_ATTRIBUTES = ['chassis_uuid', 'driver', 'driver_info', 'extra',
                       'node_id', 'properties']


class Node(base.Resource):
    def __repr__(self):
        return "<Node %s>" % self._info


class NodeManager(base.Manager):
    resource_class = Node

    @staticmethod
    def _path(id=None):
        return '/v1/nodes/%s' % id if id else '/v1/nodes'

    def list(self, associated=None):
        if associated is None:
            return self._list(self._path(), "nodes")
        else:
            path = '?associated=%s' % str(bool(associated))
            return self._list(self._path(path), "nodes")

    def list_ports(self, node_id):
        path = "%s/ports" % node_id
        return self._list(self._path(path), "ports")

    def get(self, node_id):
        try:
            return self._list(self._path(node_id))[0]
        except IndexError:
            return None

    def get_by_instance_uuid(self, instance_uuid):
        path = "?instance_uuid=%s" % instance_uuid
        nodes = self._list(self._path(path), 'nodes')
        # get all the details of the node assuming that
        # filtering by instance_uuid returns a collection
        # of one node if successful.
        if len(nodes) > 0:
            uuid = getattr(nodes[0], 'uuid')
            return self.get(uuid)
        else:
            raise exc.HTTPNotFound()

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
        if state in ['on', 'off']:
            state = "power %s" % state
        if state in ['reboot']:
            state = "rebooting"
        target = {'target': state}
        return self._update(self._path(path), target, method='PUT')

    def validate(self, node_uuid):
        path = "%s/validate" % node_uuid
        return self.get(path)
