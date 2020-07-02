# Copyright 2016 Hitachi, Ltd.
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


class VolumeTarget(base.Resource):
    def __repr__(self):
        return "<VolumeTarget %s>" % self._info


class VolumeTargetManager(base.CreateManager):
    resource_class = VolumeTarget
    _creation_attributes = ['extra', 'node_uuid', 'volume_type',
                            'properties', 'boot_index', 'volume_id',
                            'uuid']
    _resource_name = 'volume/targets'

    def list(self, node=None, limit=None, marker=None, sort_key=None,
             sort_dir=None, detail=False, fields=None,
             os_ironic_api_version=None, global_request_id=None):
        """Retrieve a list of volume target.

        :param node:   Optional, UUID or name of a node, to get volume
                       targets for this node only.
        :param marker: Optional, the UUID of a volume target, eg the last
                       volume target from a previous result set. Return
                       the next result set.
        :param limit: The maximum number of results to return per
                      request, if:

            1) limit > 0, the maximum number of volume targets to return.
            2) limit == 0, return the entire list of volume targets.
            3) limit param is NOT specified (None), the number of items
               returned respect the maximum imposed by the Ironic API
               (see Ironic's api.max_limit option).

        :param sort_key: Optional, field used for sorting.

        :param sort_dir: Optional, direction of sorting, either 'asc' (the
                         default) or 'desc'.

        :param detail: Optional, boolean whether to return detailed information
                       about volume targets.

        :param fields: Optional, a list with a specified set of fields
                       of the resource to be returned. Can not be used
                       when 'detail' is set.

        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.

        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.

        :returns: A list of volume targets.

        """
        if limit is not None:
            limit = int(limit)

        if detail and fields:
            raise exc.InvalidAttribute(_("Can't fetch a subset of fields "
                                         "with 'detail' set"))

        filters = utils.common_filters(marker=marker, limit=limit,
                                       sort_key=sort_key, sort_dir=sort_dir,
                                       fields=fields, detail=detail)
        if node is not None:
            filters.append('node=%s' % node)

        path = ''
        if filters:
            path += '?' + '&'.join(filters)
        header_values = {"os_ironic_api_version": os_ironic_api_version,
                         "global_request_id": global_request_id}
        if limit is None:
            return self._list(self._path(path), "targets", **header_values)
        else:
            return self._list_pagination(self._path(path), "targets",
                                         limit=limit, **header_values)

    def get(self, volume_target_id, fields=None, os_ironic_api_version=None,
            global_request_id=None):
        return self._get(resource_id=volume_target_id, fields=fields,
                         os_ironic_api_version=os_ironic_api_version,
                         global_request_id=global_request_id)

    def delete(self, volume_target_id, os_ironic_api_version=None,
               global_request_id=None):
        return self._delete(resource_id=volume_target_id,
                            os_ironic_api_version=os_ironic_api_version,
                            global_request_id=global_request_id)

    def update(self, volume_target_id, patch, os_ironic_api_version=None,
               global_request_id=None):
        return self._update(resource_id=volume_target_id, patch=patch,
                            os_ironic_api_version=os_ironic_api_version,
                            global_request_id=global_request_id)
