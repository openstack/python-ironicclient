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
from ironicclient.common.i18n import _
from ironicclient.common import utils
from ironicclient import exc


class Port(base.Resource):
    def __repr__(self):
        return "<Port %s>" % self._info


class PortManager(base.CreateManager):
    resource_class = Port
    _creation_attributes = ['address', 'extra', 'local_link_connection',
                            'node_uuid', 'physical_network', 'portgroup_uuid',
                            'pxe_enabled', 'uuid', 'is_smartnic']
    _resource_name = 'ports'

    def list(self, address=None, limit=None, marker=None, sort_key=None,
             sort_dir=None, detail=False, fields=None, node=None,
             portgroup=None, os_ironic_api_version=None,
             global_request_id=None):
        """Retrieve a list of ports.

        :param address: Optional, MAC address of a port, to get
                       the port which has this MAC address
        :param marker: Optional, the UUID of a port, eg the last
                       port from a previous result set. Return
                       the next result set.
        :param limit: The maximum number of results to return per
                      request, if:

            1) limit > 0, the maximum number of ports to return.
            2) limit == 0, return the entire list of ports.
            3) limit param is NOT specified (None), the number of items
               returned respect the maximum imposed by the Ironic API
               (see Ironic's api.max_limit option).

        :param sort_key: Optional, field used for sorting.

        :param sort_dir: Optional, direction of sorting, either 'asc' (the
                         default) or 'desc'.

        :param detail: Optional, boolean whether to return detailed information
                       about ports.

        :param fields: Optional, a list with a specified set of fields
                       of the resource to be returned. Can not be used
                       when 'detail' is set.

        :param node: Optional, name or UUID of a node. Used to get
                     ports of this node.

        :param portgroup: Optional, name or UUID of a portgroup. Used to get
                          ports of this portgroup.

        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.

        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.

        :returns: A list of ports.

        """
        if limit is not None:
            limit = int(limit)

        if detail and fields:
            raise exc.InvalidAttribute(_("Can't fetch a subset of fields "
                                         "with 'detail' set"))

        filters = utils.common_filters(marker, limit, sort_key, sort_dir,
                                       fields)
        if address is not None:
            filters.append('address=%s' % address)
        if node is not None:
            filters.append('node=%s' % node)
        if portgroup is not None:
            filters.append('portgroup=%s' % portgroup)

        path = ''
        if detail:
            path += 'detail'
        if filters:
            path += '?' + '&'.join(filters)
        header_values = {"os_ironic_api_version": os_ironic_api_version,
                         "global_request_id": global_request_id}
        if limit is None:
            return self._list(self._path(path), "ports", **header_values)
        else:
            return self._list_pagination(self._path(path), "ports",
                                         limit=limit, **header_values)

    def get(self, port_id, fields=None, os_ironic_api_version=None,
            global_request_id=None):
        return self._get(resource_id=port_id, fields=fields,
                         os_ironic_api_version=os_ironic_api_version,
                         global_request_id=global_request_id)

    def get_by_address(self, address, fields=None, os_ironic_api_version=None,
                       global_request_id=None):
        path = '?address=%s' % address
        if fields is not None:
            path += '&fields=' + ','.join(fields)
        else:
            path = 'detail' + path

        ports = self._list(self._path(path), 'ports',
                           os_ironic_api_version=os_ironic_api_version,
                           global_request_id=global_request_id)
        # get all the details of the port assuming that filtering by
        # address returns a collection of one port if successful.
        if len(ports) == 1:
            return ports[0]
        else:
            raise exc.NotFound()

    def delete(self, port_id, os_ironic_api_version=None,
               global_request_id=None):
        return self._delete(resource_id=port_id,
                            os_ironic_api_version=os_ironic_api_version,
                            global_request_id=global_request_id)

    def update(self, port_id, patch, os_ironic_api_version=None,
               global_request_id=None):
        return self._update(resource_id=port_id, patch=patch,
                            os_ironic_api_version=os_ironic_api_version,
                            global_request_id=global_request_id)
