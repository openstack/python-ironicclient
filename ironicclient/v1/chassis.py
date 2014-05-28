# -*- coding: utf-8 -*-
#
# Copyright © 2013 Red Hat, Inc
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


CREATION_ATTRIBUTES = ['description', 'extra']


class Chassis(base.Resource):
    def __repr__(self):
        return "<Chassis %s>" % self._info


class ChassisManager(base.Manager):
    resource_class = Chassis

    @staticmethod
    def _path(id=None):
        return '/v1/chassis/%s' % id if id else '/v1/chassis'

    def list(self):
        return self._list(self._path(), "chassis")

    def list_nodes(self, chassis_id):
        path = "%s/nodes" % chassis_id
        return self._list(self._path(path), "nodes")

    def get(self, chassis_id):
        try:
            return self._list(self._path(chassis_id))[0]
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

    def delete(self, chassis_id):
        return self._delete(self._path(chassis_id))

    def update(self, chassis_id, patch):
        return self._update(self._path(chassis_id), patch)
