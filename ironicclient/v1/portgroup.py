# Copyright 2016 SAP Ltd.
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

from __future__ import annotations

from typing import Any

from ironicclient.common import base
from ironicclient.common.i18n import _
from ironicclient.common import utils
from ironicclient import exc


class Portgroup(base.Resource):
    def __repr__(self) -> str:
        return "<Portgroup %s>" % self._info


class PortgroupManager(base.CreateManager):
    resource_class: type[Portgroup] = Portgroup
    _creation_attributes: list[str] = [
        'address', 'extra', 'name', 'node_uuid',
        'standalone_ports_supported', 'mode', 'properties',
        'uuid', 'physical_network', 'category',
    ]
    _resource_name: str = 'portgroups'

    def get(
        self,
        portgroup_id: str,
        fields: list[str] | None = None,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> base.Resource | None:
        """Get a port group with the specified identifier.

        :param portgroup_id: The UUID or name of a portgroup.
        :param fields: Optional, a list with a specified set of fields
                       of the resource to be returned. Can not be used
                       when 'detail' is set.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.

        :returns: a :class:`Portgroup` object.

        """
        return self._get(
            resource_id=portgroup_id,
            fields=fields,
            os_ironic_api_version=os_ironic_api_version,
            global_request_id=global_request_id,
        )

    def get_by_address(
        self,
        address: str,
        fields: list[str] | None = None,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> base.Resource:
        """Get a port group with the specified MAC address.

        :param address: The MAC address of a portgroup.
        :param fields: Optional, a list with a specified set of fields
                       of the resource to be returned. Can not be used
                       when 'detail' is set.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.

        :returns: a :class:`Portgroup` object.

        """
        path = '?address=%s' % address
        if fields is not None:
            path += '&fields=' + ','.join(fields)
        else:
            path = 'detail' + path

        portgroups = self._list(
            self._path(path), 'portgroups',
            os_ironic_api_version=os_ironic_api_version,
            global_request_id=global_request_id,
        )
        # get all the details of the portgroup assuming that
        # filtering by address returns a collection of one portgroup
        # if successful.
        if len(portgroups) == 1:
            return portgroups[0]
        else:
            raise exc.NotFound()

    def delete(
        self,
        portgroup_id: str,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> None:
        """Delete the Portgroup from the DB.

        :param portgroup_id: The UUID or name of a portgroup.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.
        """
        return self._delete(
            resource_id=portgroup_id,
            os_ironic_api_version=os_ironic_api_version,
            global_request_id=global_request_id,
        )

    def update(
        self,
        portgroup_id: str,
        patch: list[dict[str, Any]],
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> base.Resource | None:
        """Update the Portgroup.

        :param portgroup_id: The UUID or name of a portgroup.
        :param patch: The patch request with updates.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.
        """
        return self._update(
            resource_id=portgroup_id,
            patch=patch,
            os_ironic_api_version=os_ironic_api_version,
            global_request_id=global_request_id,
        )

    def list_ports(
        self,
        portgroup_id: str,
        marker: str | None = None,
        limit: int | None = None,
        sort_key: str | None = None,
        sort_dir: str | None = None,
        detail: bool = False,
        fields: list[str] | None = None,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> list[base.Resource]:
        """List all the ports for a given portgroup.

        :param portgroup_id: Name or UUID of the portgroup.
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

        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.

        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.

        :returns: A list of ports.

        """
        if limit is not None:
            limit = int(limit)

        if detail and fields:
            raise exc.InvalidAttribute(
                _("Can't fetch a subset of fields "
                  "with 'detail' set"))

        filters = utils.common_filters(
            marker, limit, sort_key, sort_dir, fields)

        path = "%s/ports" % portgroup_id
        if detail:
            path += '/detail'

        if filters:
            path += '?' + '&'.join(filters)
        if limit is None:
            return self._list(
                self._path(path),
                "ports",
                os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id,
            )
        else:
            return self._list_pagination(
                self._path(path),
                "ports",
                limit=limit,
                os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id,
            )

    def list(
        self,
        node: str | None = None,
        address: str | None = None,
        limit: int | None = None,
        marker: str | None = None,
        sort_key: str | None = None,
        sort_dir: str | None = None,
        detail: bool = False,
        fields: list[str] | None = None,
        shards: list[str] | None = None,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> list[base.Resource]:
        """Retrieve a list of portgroups.

        :param node: Optional, UUID or name of a node, to get
                     the portgroups for that node.
        :param address: Optional, MAC address of a portgroup, to get
                       the portgroup which has this MAC address.
        :param marker: Optional, the UUID of a portgroup, eg the last
                       portgroup from a previous result set. Return
                       the next result set.
        :param limit: The maximum number of results to return per
                      request, if:

            1) limit > 0, the maximum number of portgroups to return.
            2) limit == 0, return the entire list of portgroups.
            3) limit == None, the number of items returned respect the
               maximum imposed by the Ironic API (see Ironic's
               api.max_limit option).

        :param sort_key: Optional, field used for sorting.

        :param sort_dir: Optional, direction of sorting, either 'asc' (the
                         default) or 'desc'.

        :param detail: Optional, boolean whether to return detailed information
                       about portgroups.

        :param fields: Optional, a list with a specified set of fields
                       of the resource to be returned. Can not be used
                       when 'detail' is set.

        :param shards: Optional, a list of shards to filter portgroups by.
                       Only portgroups associated with nodes in these shards
                       will be returned.

        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.

        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.

        :returns: A list of portgroups.
        :raises: InvalidAttribute if a subset of fields is requested with
                 detail option set.

        """
        if limit is not None:
            limit = int(limit)

        if detail and fields:
            raise exc.InvalidAttribute(
                _("Can't fetch a subset of fields "
                  "with 'detail' set"))

        filters = utils.common_filters(
            marker, limit, sort_key, sort_dir, fields)
        if address is not None:
            filters.append('address=%s' % address)
        if node is not None:
            filters.append('node=%s' % node)
        if shards is not None:
            filters.append('shard=%s' % ','.join(shards))

        path = ''
        if detail:
            path += 'detail'
        if filters:
            path += '?' + '&'.join(filters)
        if limit is None:
            return self._list(
                self._path(path),
                "portgroups",
                os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id,
            )
        else:
            return self._list_pagination(
                self._path(path),
                "portgroups",
                limit=limit,
                os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id,
            )
