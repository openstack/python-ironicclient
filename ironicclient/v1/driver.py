# Copyright 2013 Red Hat, Inc.
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

from ironicclient.common import base


class Driver(base.Resource):
    def __repr__(self):
        return "<Driver %s>" % self._info


class DriverManager(base.Manager):
    resource_class = Driver
    _resource_name = 'drivers'

    def list(self):
        return self._list('/v1/drivers', self._resource_name)

    def properties(self, driver_name):
        return self.get('%s/properties' % driver_name).to_dict()

    def get_vendor_passthru_methods(self, driver_name):
        path = "%s/vendor_passthru/methods" % driver_name
        return self.get(path).to_dict()
