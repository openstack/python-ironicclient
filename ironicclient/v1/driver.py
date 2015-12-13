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
from ironicclient.common.i18n import _
from ironicclient import exc


class Driver(base.Resource):
    def __repr__(self):
        return "<Driver %s>" % self._info


class DriverManager(base.Manager):
    resource_class = Driver
    _resource_name = 'drivers'

    def list(self):
        return self._list('/v1/drivers', self._resource_name)

    def get(self, driver_name):
        return self._get(resource_id=driver_name)

    def update(self, driver_name, patch, http_method='PATCH'):
        return self._update(resource_id=driver_name, patch=patch,
                            method=http_method)

    def delete(self, driver_name):
        return self._delete(resource_id=driver_name)

    def properties(self, driver_name):
        return self._get(resource_id='%s/properties' % driver_name).to_dict()

    def vendor_passthru(self, driver_name, method, args=None,
                        http_method=None):
        """Issue requests for vendor-specific actions on a given driver.

        :param driver_name: The name of the driver.
        :param method: Name of the vendor method.
        :param args: Optional. The arguments to be passed to the method.
        :param http_method: The HTTP method to use on the request.
                            Defaults to POST.
        """
        if args is None:
            args = {}

        if http_method is None:
            http_method = 'POST'

        http_method = http_method.upper()

        path = "%s/vendor_passthru/%s" % (driver_name, method)
        if http_method in ('POST', 'PUT', 'PATCH'):
            return self.update(path, args, http_method=http_method)
        elif http_method == 'DELETE':
            return self.delete(path)
        elif http_method == 'GET':
            return self.get(path)
        else:
            raise exc.InvalidAttribute(
                _('Unknown HTTP method: %s') % http_method)

    def get_vendor_passthru_methods(self, driver_name):
        path = "%s/vendor_passthru/methods" % driver_name
        return self.get(path).to_dict()
