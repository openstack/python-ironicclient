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

    def list(self, driver_type=None, detail=None, os_ironic_api_version=None,
             global_request_id=None):
        """Retrieve a list of drivers.

        :param driver_type: Optional, string to filter the drivers by type.
                            Value should be 'classic' or 'dynamic'.
        :param detail: Optional, flag whether to return detailed information
                       about drivers. Default is None means not to send the arg
                       to the server due to older versions of the server cannot
                       handle filtering on detail.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.
        :returns: A list of drivers.
        """
        filters = []
        if driver_type is not None:
            filters.append('type=%s' % driver_type)
        if detail is not None:
            filters.append('detail=%s' % detail)

        path = ''
        if filters:
            path = '?' + '&'.join(filters)
        return self._list(self._path(path), self._resource_name,
                          os_ironic_api_version=os_ironic_api_version,
                          global_request_id=global_request_id)

    def get(self, driver_name, os_ironic_api_version=None,
            global_request_id=None):
        return self._get(resource_id=driver_name,
                         os_ironic_api_version=os_ironic_api_version,
                         global_request_id=global_request_id)

    def update(self, driver_name, patch, http_method='PATCH',
               os_ironic_api_version=None, global_request_id=None):
        return self._update(resource_id=driver_name, patch=patch,
                            method=http_method,
                            os_ironic_api_version=os_ironic_api_version,
                            global_request_id=global_request_id)

    def delete(self, driver_name, os_ironic_api_version=None,
               global_request_id=None):
        return self._delete(resource_id=driver_name,
                            os_ironic_api_version=os_ironic_api_version,
                            global_request_id=global_request_id)

    def properties(self, driver_name, os_ironic_api_version=None,
                   global_request_id=None):
        return self._get_as_dict('%s/properties' % driver_name,
                                 os_ironic_api_version=os_ironic_api_version,
                                 global_request_id=global_request_id)

    def raid_logical_disk_properties(self, driver_name,
                                     os_ironic_api_version=None,
                                     global_request_id=None):
        """Returns the RAID logical disk properties for the driver.

        :param driver_name: Name of the driver.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.
        :returns: A dictionary containing the properties that can be mentioned
            for RAID logical disks and a textual description for them. It
            returns an empty dictionary on error.
        """
        info = None
        try:
            info = self._list(
                '/v1/drivers/%s/raid/logical_disk_properties' % driver_name,
                os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id)[0]
        except IndexError:
            pass

        if info:
            return info.to_dict()
        return {}

    def vendor_passthru(self, driver_name, method, args=None,
                        http_method=None, os_ironic_api_version=None,
                        global_request_id=None):
        """Issue requests for vendor-specific actions on a given driver.

        :param driver_name: The name of the driver.
        :param method: Name of the vendor method.
        :param args: Optional. The arguments to be passed to the method.
        :param http_method: The HTTP method to use on the request.
                            Defaults to POST.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.
        """
        if args is None:
            args = {}

        if http_method is None:
            http_method = 'POST'

        http_method = http_method.upper()

        header_values = {"os_ironic_api_version": os_ironic_api_version,
                         "global_request_id": global_request_id}

        path = "%s/vendor_passthru/%s" % (driver_name, method)
        if http_method in ('POST', 'PUT', 'PATCH'):
            return self.update(path, args, http_method=http_method,
                               **header_values)
        elif http_method == 'DELETE':
            return self.delete(path, **header_values)
        elif http_method == 'GET':
            return self.get(path, **header_values)
        else:
            raise exc.InvalidAttribute(
                _('Unknown HTTP method: %s') % http_method)

    def get_vendor_passthru_methods(self, driver_name,
                                    os_ironic_api_version=None,
                                    global_request_id=None):
        return self._get_as_dict("%s/vendor_passthru/methods" % driver_name,
                                 os_ironic_api_version=os_ironic_api_version,
                                 global_request_id=global_request_id)
