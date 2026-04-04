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

from __future__ import annotations

from collections.abc import Callable
import logging
import os
from typing import Any, cast

from oslo_utils import strutils

from ironicclient.common import base
from ironicclient.common.i18n import _
from ironicclient.common import utils
from ironicclient import exc
from ironicclient.v1 import volume_connector
from ironicclient.v1 import volume_target

_power_states: dict[str, str] = {
    'on': 'power on',
    'off': 'power off',
    'reboot': 'rebooting',
    'soft off': 'soft power off',
    'soft reboot': 'soft rebooting',
}


LOG: logging.Logger = logging.getLogger(__name__)
_DEFAULT_POLL_INTERVAL: int = 2


class Node(base.Resource):
    def __repr__(self) -> str:
        return "<Node %s>" % self._info


class NodeManager(base.CreateManager[Node]):
    resource_class: type[Node] = Node
    _creation_attributes: list[str] = [
        'chassis_uuid', 'driver', 'driver_info',
        'extra', 'uuid', 'properties', 'name',
        'bios_interface', 'boot_interface',
        'console_interface', 'deploy_interface',
        'disable_power_off', 'inspect_interface',
        'management_interface', 'network_interface',
        'power_interface', 'raid_interface',
        'rescue_interface', 'storage_interface',
        'vendor_interface', 'firmware_interface',
        'resource_class', 'conductor_group',
        'automated_clean', 'network_data', 'parent_node',
        'owner', 'lessee', 'shard', 'description',
        'instance_name',
    ]
    _resource_name: str = 'nodes'

    def list_ports(
        self,
        node_id: str,
        marker: str | None = None,
        limit: int | None = None,
        sort_key: str | None = None,
        sort_dir: str | None = None,
        detail: bool = False,
        fields: list[str] | None = None,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> list[Node]:
        """List all the ports for a given node.

        :param node_id: Name or UUID of the node.
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
            raise exc.InvalidAttribute(_("Can't fetch a subset of fields "
                                         "with 'detail' set"))

        filters = utils.common_filters(marker, limit, sort_key, sort_dir,
                                       fields)

        path = "%s/ports" % node_id
        if detail:
            path += '/detail'

        if filters:
            path += '?' + '&'.join(filters)
        if limit is None:
            return self._list(
                self._path(path), "ports",
                os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id,
            )
        else:
            return self._list_pagination(
                self._path(path), "ports", limit=limit,
                os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id,
            )

    def list_volume_connectors(
        self,
        node_id: str,
        marker: str | None = None,
        limit: int | None = None,
        sort_key: str | None = None,
        sort_dir: str | None = None,
        detail: bool = False,
        fields: list[str] | None = None,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> list[volume_connector.VolumeConnector]:
        """List all the volume connectors for a given node.

        :param node_id: Name or UUID of the node.
        :param marker: Optional, the UUID of a volume connector, eg the last
                       volume connector from a previous result set. Return
                       the next result set.
        :param limit: The maximum number of results to return per
                      request, if:

            1) limit > 0, the maximum number of volume connectors to return.
            2) limit == 0, return the entire list of volume connectors.
            3) limit param is NOT specified (None), the number of items
               returned respect the maximum imposed by the Ironic API
               (see Ironic's api.max_limit option).

        :param sort_key: Optional, field used for sorting.

        :param sort_dir: Optional, direction of sorting, either 'asc' (the
                         default) or 'desc'.

        :param detail: Optional, boolean whether to return detailed information
                       about volume connectors.

        :param fields: Optional, a list with a specified set of fields
                       of the resource to be returned. Can not be used
                       when 'detail' is set.

        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.

        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.

        :returns: A list of volume connectors.

        """
        if limit is not None:
            limit = int(limit)

        if detail and fields:
            raise exc.InvalidAttribute(_("Can't fetch a subset of fields "
                                         "with 'detail' set"))

        filters = utils.common_filters(marker=marker, limit=limit,
                                       sort_key=sort_key, sort_dir=sort_dir,
                                       fields=fields, detail=detail)

        path = "%s/volume/connectors" % node_id
        if filters:
            path += '?' + '&'.join(filters)
        vc = volume_connector.VolumeConnector
        if limit is None:
            return self._list(
                self._path(path), response_key="connectors",
                obj_class=vc,
                os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id,
            )
        else:
            return self._list_pagination(
                self._path(path), response_key="connectors",
                limit=limit,
                obj_class=vc,
                os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id,
            )

    def list_volume_targets(
        self,
        node_id: str,
        marker: str | None = None,
        limit: int | None = None,
        sort_key: str | None = None,
        sort_dir: str | None = None,
        detail: bool = False,
        fields: list[str] | None = None,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> list[volume_target.VolumeTarget]:
        """List all the volume targets for a given node.

        :param node_id: Name or UUID of the node.
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

        path = "%s/volume/targets" % node_id
        if filters:
            path += '?' + '&'.join(filters)
        vt = volume_target.VolumeTarget
        if limit is None:
            return self._list(
                self._path(path), response_key="targets",
                obj_class=vt,
                os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id,
            )
        else:
            return self._list_pagination(
                self._path(path), response_key="targets",
                limit=limit,
                obj_class=vt,
                os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id,
            )

    def list_children_of_node(
        self,
        node_id: str,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> list[str]:
        """Get a list of child nodes for the supplied node_id.

        :param node_id: The name or UUID of a node.

        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.

        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.

        :returns: A list of UUIDs representing child nodes for the supplied
                  node_id..
        """
        path = "%s/children" % node_id
        return cast(list[str], self._list_primitives(
            self._path(path), "children",
            os_ironic_api_version=os_ironic_api_version,
            global_request_id=global_request_id,
        ))

    def get(
        self,
        node_id: str,
        fields: list[str] | None = None,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> Node | None:
        return self._get(resource_id=node_id, fields=fields,
                         os_ironic_api_version=os_ironic_api_version,
                         global_request_id=global_request_id)

    def get_by_instance_uuid(
        self,
        instance_uuid: str,
        fields: list[str] | None = None,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> Node:
        path = '?instance_uuid=%s' % instance_uuid
        if fields is not None:
            path += '&fields=' + ','.join(fields)
        else:
            path = 'detail' + path

        nodes = self._list(
            self._path(path), 'nodes',
            os_ironic_api_version=os_ironic_api_version,
            global_request_id=global_request_id)
        # get all the details of the node assuming that
        # filtering by instance_uuid returns a collection
        # of one node if successful.
        if len(nodes) == 1:
            return nodes[0]
        else:
            raise exc.NotFound()

    def delete(
        self,
        node_id: str,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> None:
        self._delete(
            resource_id=node_id,
            os_ironic_api_version=os_ironic_api_version,
            global_request_id=global_request_id)

    def update(
        self,
        node_id: str,
        patch: list[dict[str, Any]] | dict[str, Any] | None,
        http_method: str = 'PATCH',
        os_ironic_api_version: str | None = None,
        reset_interfaces: bool | None = None,
        global_request_id: str | None = None,
    ) -> Node | None:
        params: dict[str, bool] = {}
        if reset_interfaces is not None:
            params['reset_interfaces'] = reset_interfaces
        return self._update(
            resource_id=node_id,
            patch=patch,  # type: ignore[arg-type]
            method=http_method,
            os_ironic_api_version=os_ironic_api_version,
            global_request_id=global_request_id,
            params=params,
        )

    def vendor_passthru(
        self,
        node_id: str,
        method: str,
        args: dict[str, Any] | None = None,
        http_method: str | None = None,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> Node | None:
        """Issue requests for vendor-specific actions on a given node.

        :param node_id: The UUID of the node.
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

        path = "%s/vendor_passthru/%s" % (node_id, method)
        if http_method in ('POST', 'PUT', 'PATCH'):
            return self.update(
                path, args, http_method=http_method,
                os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id,
            )
        elif http_method == 'DELETE':
            self.delete(
                path,
                os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id,
            )
            return None
        elif http_method == 'GET':
            return self.get(
                path,
                os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id,
            )
        else:
            raise exc.InvalidAttribute(
                _('Unknown HTTP method: %s') % http_method)

    def vif_list(
        self,
        node_ident: str,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> list[Node]:
        """List VIFs attached to a given node.

        :param node_ident: The UUID or Name of the node.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.
        """
        path = "%s/vifs" % node_ident

        return self._list(self._path(path), "vifs",
                          os_ironic_api_version=os_ironic_api_version,
                          global_request_id=global_request_id)

    def vif_attach(
        self,
        node_ident: str,
        vif_id: str,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
        **kwargs: str,
    ) -> None:
        """Attach VIF to a given node.

        :param node_ident: The UUID or Name of the node.
        :param vif_id: The UUID or Name of the VIF to attach.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.
        :param kwargs: A dictionary containing the attributes of the resource
                       that will be created.
        """
        path = "%s/vifs" % node_ident
        data: dict[str, str] = {"id": vif_id}
        if 'id' in kwargs:
            raise exc.InvalidAttribute("The attribute 'id' can't be "
                                       "specified in vif-info")
        data.update(kwargs)
        # TODO(vdrok): cleanup places doing custom path and http_method
        self.update(path, data, http_method="POST",
                    os_ironic_api_version=os_ironic_api_version,
                    global_request_id=global_request_id)

    def vif_detach(
        self,
        node_ident: str,
        vif_id: str,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> None:
        """Detach VIF from a given node.

        :param node_ident: The UUID or Name of the node.
        :param vif_id: The UUID or Name of the VIF to detach.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.
        """
        path = "%s/vifs/%s" % (node_ident, vif_id)
        self.delete(path, os_ironic_api_version=os_ironic_api_version,
                    global_request_id=global_request_id)

    def set_maintenance(
        self,
        node_id: str,
        state: bool | str,
        maint_reason: str | None = None,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> Node | None:
        """Set the maintenance mode for the node.

        :param node_id: The UUID of the node.
        :param state: the maintenance mode; either a Boolean or a string
                      representation of a Boolean (eg, 'true', 'on', 'false',
                      'off'). True to put the node in maintenance mode; False
                      to take the node out of maintenance mode.
        :param maint_reason: Optional string. Reason for putting node
                             into maintenance mode.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.

        :raises: InvalidAttribute if state is an invalid string (that doesn't
                 represent a Boolean).
        """
        if isinstance(state, bool):
            maintenance_mode = state
        else:
            try:
                maintenance_mode = strutils.bool_from_string(state, True)
            except ValueError as e:
                raise exc.InvalidAttribute(_("Argument 'state': %(err)s") %
                                           {'err': e})
        path = "%s/maintenance" % node_id
        if maintenance_mode:
            reason = {'reason': maint_reason}
            return self.update(
                path, reason, http_method='PUT',
                os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id,
            )
        else:
            self.delete(
                path,
                os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id,
            )
            return None

    def set_power_state(
        self,
        node_id: str,
        state: str,
        soft: bool = False,
        timeout: int | None = None,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> Node | None:
        """Sets power state for a node.

        :param node_id: Node identifier
        :param state: One of target power state, 'on', 'off', or 'reboot'
        :param soft: The flag for graceful power 'off' or 'reboot'
        :param timeout: The timeout (in seconds) positive integer value (> 0)
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.

        :raises: ValueError if 'soft' or 'timeout' option is invalid
        :returns: The status of the request
        """
        if state == 'on' and soft:
            raise ValueError(
                _("'soft' option is invalid for the power-state 'on'"))

        path = "%s/states/power" % node_id

        requested_state = 'soft ' + state if soft else state
        target = _power_states.get(requested_state, state)

        body: dict[str, str | int] = {'target': target}
        if timeout is not None:
            msg = _("'timeout' option for setting power state must have "
                    "positive integer value (> 0)")
            try:
                timeout = int(timeout)
            except (ValueError, TypeError):
                raise ValueError(msg)

            if timeout <= 0:
                raise ValueError(msg)
            body = {'target': target, 'timeout': timeout}

        return self.update(path, body, http_method='PUT',
                           os_ironic_api_version=os_ironic_api_version,
                           global_request_id=global_request_id)

    def set_boot_mode(
        self,
        node_id: str,
        state: str,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> Node | None:
        """Sets boot mode for a node.

        :param node_id: Node identifier
        :param state: One of target boot modes, 'uefi' or 'bios'
        :param os_ironic_api_version: String version (e.g. "1.76") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.

        :raises: ValueError if boot mode is not one of 'uefi' / 'bios'
        :returns: The status of the request
        """
        if state not in ('uefi', 'bios'):
            raise ValueError(
                _("Valid boot modes are 'uefi' or 'bios'"))

        path = "%s/states/boot_mode" % node_id
        target = state
        body = {'target': target}

        return self.update(path, body, http_method='PUT',
                           os_ironic_api_version=os_ironic_api_version,
                           global_request_id=global_request_id)

    def set_secure_boot(
        self,
        node_id: str,
        state: bool | str,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> Node | None:
        """Set the secure boot state for the node.

        :param node_id: The UUID of the node.
        :param state: the secure boot state; either a Boolean or a string
                      representation of a Boolean (eg, 'true', 'on', 'false',
                      'off'). True to turn secure boot on; False
                      to turn secure boot off.
        :param os_ironic_api_version: String version (e.g. "1.76") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.

        :raises: InvalidAttribute if state is an invalid string (that doesn't
                 represent a Boolean).
        """
        if isinstance(state, bool):
            target = state
        else:
            try:
                target = strutils.bool_from_string(state, strict=True)
            except ValueError as e:
                raise exc.InvalidAttribute(_("Argument 'state': %(err)s") %
                                           {'err': e})
        path = "%s/states/secure_boot" % node_id
        body = {'target': target}

        return self.update(path, body, http_method='PUT',
                           os_ironic_api_version=os_ironic_api_version,
                           global_request_id=global_request_id)

    def set_target_raid_config(
        self,
        node_ident: str,
        target_raid_config: dict[str, Any],
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> Node | None:
        """Sets target_raid_config for a node.

        :param node_ident: Node identifier
        :param target_raid_config: A dictionary with the target RAID
            configuration; may be empty.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.

        :returns: status of the request
        """
        path = "%s/states/raid" % node_ident
        return self.update(path, target_raid_config, http_method='PUT',
                           os_ironic_api_version=os_ironic_api_version,
                           global_request_id=global_request_id)

    def validate(
        self,
        node_uuid: str,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> Node | None:
        path = "%s/validate" % node_uuid
        return self.get(path, os_ironic_api_version=os_ironic_api_version,
                        global_request_id=global_request_id)

    def set_provision_state(
        self,
        node_uuid: str,
        state: str,
        configdrive: str | dict[str, Any] | list[Any] | bytes | None = None,
        cleansteps: list[dict[str, Any]] | None = None,
        rescue_password: str | None = None,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
        deploysteps: list[dict[str, Any]] | None = None,
        servicesteps: list[dict[str, Any]] | None = None,
        runbook: str | None = None,
        disable_ramdisk: bool | str | None = None,
    ) -> Node | None:
        """Set the provision state for the node.

        :param node_uuid: The UUID or name of the node.
        :param state: The desired provision state. One of 'active', 'deleted',
             'rebuild', 'inspect', 'provide', 'manage', 'clean', 'abort',
             'rescue', 'unrescue'.
        :param configdrive: One of:

            * a gzipped, base64-encoded configuration drive string
            * a dictionary to build config drive from
            * a path to the configuration drive file (ISO 9660 or VFAT)
            * a path to a directory containing the config drive files
            * a path to a JSON file to build config from

            In case it's a directory, a config drive will be generated from
            it. In case it's a dictionary or a JSON file, a config drive will
            be generated on the server side (requires API version 1.56).
            This is only valid when setting state to 'active'.
        :param cleansteps: The clean steps as a list of clean-step
            dictionaries; each dictionary should have keys 'interface' and
            'step', and optional key 'args'. This must be specified (and is
            only valid) when setting provision-state to 'clean'.
        :param rescue_password: A string to be used as the login password
            inside the rescue ramdisk once a node is rescued. This must be
            specified (and is only valid) when setting 'state' to 'rescue'.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.
        :param deploysteps: The deploy steps as a list of deploy-step
            dictionaries; each dictionary should have keys 'interface', 'step',
            'priority', and optional key 'args'. This is optional and is
            only valid when setting provision-state to 'active' or 'rebuild'.
        :param servicesteps: The service steps as list of service-step
            dictionaries; each dictionary should have keys 'interface', 'step',
            and optional key 'args' when setting an 'active' nodes to
            'service'.
        :param runbook: The identifier of a predefined runbook to use for
            provisioning.
        :param disable_ramdisk: Boolean if set to true will not boot the
            ironic-python-agent for cleaning. Only valid when setting 'state'
            to 'clean' or 'service' and only for steps explicitly marked as
            not requiring the ironic-python-agent can use this.
        :raises: InvalidAttribute if there was an error with the clean steps or
            deploy steps
        :returns: The status of the request
        """

        path = "%s/states/provision" % node_uuid
        body: dict[str, Any] = {'target': state}
        if configdrive:
            if isinstance(configdrive, str):
                if os.path.isfile(configdrive):
                    with open(configdrive, 'rb') as f:
                        configdrive = f.read()
                    json_data = utils.get_json_data(configdrive)
                    if json_data is not None:
                        configdrive = json_data
                elif os.path.isdir(configdrive):
                    configdrive = utils.make_configdrive(configdrive)
                else:
                    raise ValueError('Config drive seems to refer to a file '
                                     'or directory but this file/directory '
                                     'does not exist: %s.' % configdrive)

            if isinstance(configdrive, bytes):
                try:
                    configdrive = configdrive.decode('utf-8')
                except UnicodeError:
                    raise ValueError('Config drive must be a dictionary or '
                                     'a base64 encoded string')
            body['configdrive'] = configdrive
        elif cleansteps:
            body['clean_steps'] = cleansteps
        elif rescue_password:
            body['rescue_password'] = rescue_password

        if deploysteps:
            body['deploy_steps'] = deploysteps

        if servicesteps:
            body['service_steps'] = servicesteps

        if runbook:
            body['runbook'] = runbook

        if isinstance(disable_ramdisk, bool):
            body['disable_ramdisk'] = disable_ramdisk
        elif disable_ramdisk:
            try:
                body['disable_ramdisk'] = strutils.bool_from_string(
                    disable_ramdisk, True)
            except ValueError as e:
                raise exc.InvalidAttribute(_("Argument 'disable_ramdisk': "
                                             "%(err)s") % {'err': e})

        return self.update(path, body, http_method='PUT',
                           os_ironic_api_version=os_ironic_api_version,
                           global_request_id=global_request_id)

    def states(
        self,
        node_uuid: str,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> Node | None:
        path = "%s/states" % node_uuid
        return self.get(path, os_ironic_api_version=os_ironic_api_version,
                        global_request_id=global_request_id)

    def get_console(
        self,
        node_uuid: str,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> dict[str, bool | dict[str, str] | None]:
        path = "%s/states/console" % node_uuid
        return cast(
            dict[str, bool | dict[str, str] | None],
            self._get_as_dict(
                path, os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id),
        )

    def set_console_mode(
        self,
        node_uuid: str,
        enabled: bool | str,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> Node | None:
        """Set the console mode for the node.

        :param node_uuid: The UUID of the node.
        :param enabled: Either a Boolean or a string representation of a
                        Boolean. True to enable the console; False to disable.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.
        """
        path = "%s/states/console" % node_uuid
        target = {'enabled': enabled}
        return self.update(path, target, http_method='PUT',
                           os_ironic_api_version=os_ironic_api_version,
                           global_request_id=global_request_id)

    def set_boot_device(
        self,
        node_uuid: str,
        boot_device: str,
        persistent: bool = False,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> Node | None:
        path = "%s/management/boot_device" % node_uuid
        target = {'boot_device': boot_device, 'persistent': persistent}
        return self.update(path, target, http_method='PUT',
                           os_ironic_api_version=os_ironic_api_version,
                           global_request_id=global_request_id)

    def get_boot_device(
        self,
        node_uuid: str,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> dict[str, str | bool]:
        path = "%s/management/boot_device" % node_uuid
        return cast(
            dict[str, str | bool],
            self._get_as_dict(
                path, os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id),
        )

    def inject_nmi(
        self,
        node_uuid: str,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> Node | None:
        path = "%s/management/inject_nmi" % node_uuid
        return self.update(path, {}, http_method='PUT',
                           os_ironic_api_version=os_ironic_api_version,
                           global_request_id=global_request_id)

    def get_supported_boot_devices(
        self,
        node_uuid: str,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> dict[str, list[str]]:
        path = "%s/management/boot_device/supported" % node_uuid
        return cast(
            dict[str, list[str]],
            self._get_as_dict(
                path, os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id),
        )

    def get_vendor_passthru_methods(
        self,
        node_ident: str,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> dict[str, dict[str, bool | str | list[str]]]:
        path = "%s/vendor_passthru/methods" % node_ident
        return cast(
            dict[str, dict[str, bool | str | list[str]]],
            self._get_as_dict(
                path, os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id),
        )

    def get_traits(
        self,
        node_ident: str,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> list[str]:
        """Get traits for a node.

        :param node_ident: node UUID or name.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.
        """
        path = "%s/traits" % node_ident
        return cast(list[str], self._list_primitives(
            self._path(path), 'traits',
            os_ironic_api_version=os_ironic_api_version,
            global_request_id=global_request_id))

    def add_trait(
        self,
        node_ident: str,
        trait: str,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> Node | None:
        """Add a trait to a node.

        :param node_ident: node UUID or name.
        :param trait: trait to add to the node.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.
        """
        path = "%s/traits/%s" % (node_ident, trait)
        return self.update(path, None, http_method='PUT',
                           os_ironic_api_version=os_ironic_api_version,
                           global_request_id=global_request_id)

    def set_traits(
        self,
        node_ident: str,
        traits: list[str],
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> Node | None:
        """Set traits for a node.

        Removes any existing traits and adds the traits passed in to this
        method.

        :param node_ident: node UUID or name.
        :param traits: list of traits to add to the node.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.
        """
        path = "%s/traits" % node_ident
        body = {'traits': traits}
        return self.update(path, body, http_method='PUT',
                           os_ironic_api_version=os_ironic_api_version,
                           global_request_id=global_request_id)

    def remove_trait(
        self,
        node_ident: str,
        trait: str,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> None:
        """Remove a trait from a node.

        :param node_ident: node UUID or name.
        :param trait: trait to remove from the node.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.
        """
        path = "%s/traits/%s" % (node_ident, trait)
        self.delete(path, os_ironic_api_version=os_ironic_api_version,
                    global_request_id=global_request_id)

    def remove_all_traits(
        self,
        node_ident: str,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> None:
        """Remove all traits from a node.

        :param node_ident: node UUID or name.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.
        """
        path = "%s/traits" % node_ident
        self.delete(path, os_ironic_api_version=os_ironic_api_version,
                    global_request_id=global_request_id)

    def get_bios_setting(
        self,
        node_ident: str,
        name: str,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> dict[str, str] | None:
        """Get a BIOS setting from a node.

        :param node_ident: node UUID or name.
        :param name: BIOS setting name to get from the node.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.
        """
        path = "%s/bios/%s" % (node_ident, name)
        return cast(
            dict[str, str] | None,
            self._get_as_dict(
                path, os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id).get(name),
        )

    def list_bios_settings(
        self,
        node_ident: str,
        detail: bool = False,
        fields: list[str] | None = None,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> list[dict[str, str | int | bool | list[str] | None]]:
        """List all BIOS settings from a node.

        :param node_ident: node UUID or name.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.
        :param detail: Optional, boolean whether to return detailed information
                       about bios settings.
        :param fields: Optional, a list with a specified set of fields
                       of the resource to be returned. Can not be used
                       when 'detail' is set.

        """
        if detail and fields:
            raise exc.InvalidAttribute(_("Can't fetch a subset of fields "
                                         "with 'detail' set"))

        filters = utils.common_filters(detail=detail, fields=fields)
        path = "%s/bios" % node_ident

        if filters:
            path += '?' + '&'.join(filters)

        return cast(
            list[dict[str, str | int | bool | list[str] | None]],
            self._list_primitives(
                self._path(path), 'bios',
                os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id),
        )

    def _check_one_provision_state(
        self,
        node_ident: str,
        expected_state: str,
        fail_on_unexpected_state: bool = True,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> bool:
        # TODO(dtantsur): use version negotiation to request API 1.8 and use
        # the "fields" argument to reduce amount of data sent.
        node = self.get(
            node_ident, os_ironic_api_version=os_ironic_api_version,
            global_request_id=global_request_id)
        if node is None:
            return False
        if node.provision_state == expected_state:
            LOG.debug('Node %(node)s reached provision state %(state)s',
                      {'node': node_ident, 'state': expected_state})
            return True

        # Note that if expected_state == 'error' we still succeed
        if (node.provision_state == 'error'
                or node.provision_state.endswith(' failed')):
            raise exc.StateTransitionFailed(
                _('Node %(node)s failed to reach state %(state)s. '
                    'It\'s in state %(actual)s, and has error: %(error)s') %
                {'node': node_ident, 'state': expected_state,
                    'actual': node.provision_state, 'error': node.last_error})

        if fail_on_unexpected_state and not node.target_provision_state:
            raise exc.StateTransitionFailed(
                _('Node %(node)s failed to reach state %(state)s. '
                    'It\'s in unexpected stable state %(actual)s') %
                {'node': node_ident, 'state': expected_state,
                 'actual': node.provision_state})

        LOG.debug('Still waiting for node %(node)s to reach state '
                  '%(state)s, the current state is %(actual)s',
                  {'node': node_ident, 'state': expected_state,
                   'actual': node.provision_state})

        return False

    def wait_for_provision_state(
        self,
        node_ident: str | list[str],
        expected_state: str,
        timeout: int | float = 0,
        poll_interval: int | float = _DEFAULT_POLL_INTERVAL,
        poll_delay_function: Callable[[int | float], object] | None = None,
        fail_on_unexpected_state: bool = True,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> None:
        """Helper function to wait for nodes to reach a given state.

        Polls Ironic API in a loop until node gets to a requested state.

        Fails in the following cases:
        * Timeout (if provided) is reached
        * Node's last_error gets set to a non-empty value
        * Unexpected stable state is reached and fail_on_unexpected_state is on
        * Error state is reached (if it's not equal to expected_state)

        :param node_ident: node UUID or name (one or a list)
        :param expected_state: expected final provision state
        :param timeout: timeout in seconds, no timeout if 0
        :param poll_interval: interval in seconds between 2 poll
        :param poll_delay_function: function to use to wait between polls
            (defaults to time.sleep). Should take one argument - delay time
            in seconds. Any exceptions raised inside it will abort the wait.
        :param fail_on_unexpected_state: whether to fail if the nodes
            reaches a different stable state.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.

        :raises: StateTransitionFailed if node reached an error state
        :raises: StateTransitionTimeout on timeout
        """
        expected_state = expected_state.lower()
        if not isinstance(node_ident, list):
            node_ident = [node_ident]
        unfinished = node_ident

        def _timeout() -> str:
            return (
                _('Node(s) %(node)s failed to reach state %(state)s in '
                  '%(timeout)s seconds')
                % {'node': ', '.join(unfinished),
                   'state': expected_state,
                   'timeout': timeout}
            )

        for _count in utils.poll(timeout, poll_interval, poll_delay_function,
                                 _timeout):
            current, unfinished = unfinished, []
            for node in current:
                if not self._check_one_provision_state(
                        node,
                        expected_state,
                        fail_on_unexpected_state=fail_on_unexpected_state,
                        os_ironic_api_version=os_ironic_api_version,
                        global_request_id=global_request_id):
                    unfinished.append(node)
            if not unfinished:
                break

    def get_history_list(
        self,
        node_ident: str,
        detail: bool = False,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> list[dict[str, str]]:
        """Get node history event list.

        Provides the ability to query a node event history list from
        the API and return the API response to the caller.

        Requires API version 1.78.

        :param node_ident: The name or UUID of the node.
        :param detail: If detailed data should be returned in the
                       event list entry. Default False.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.
        """
        path = "%s/history" % node_ident

        if detail:
            path = path + '?detail=%s' % detail

        return cast(
            list[dict[str, str]],
            self._list_primitives(
                self._path(path), 'history',
                os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id),
        )

    def get_history_event(
        self,
        node_ident: str,
        event: str,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> dict[str, str]:
        """Get a single event record for a node.

        Provides the ability to request, and return
        a node's single event history entry.

        :param node_ident: The name or UUID of the node.
        :param event: The UUID of the event entry as listed
                      in the node event history list.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.
        """
        path = "%s/history/%s" % (node_ident, event)
        return cast(
            dict[str, str],
            self._get_as_dict(
                path, os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id),
        )

    def get_inventory(
        self,
        node_ident: str,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> dict[str, Any]:
        """Get the hardware inventory of the node.

        Requires API version 1.81.

        :param node_ident: The name or UUID of the node.
        :param os_ironic_api_version: String version (e.g. "1.81") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.
        """
        path = "%s/inventory" % node_ident
        return self._get_as_dict(
            path, os_ironic_api_version=os_ironic_api_version,
            global_request_id=global_request_id)

    def list_firmware_components(
        self,
        node_ident: str,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> list[dict[str, str]]:
        """List all firmware components from a node.

        :param node_ident: node UUID or name.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.
        """
        path = "%s/firmware" % node_ident

        return cast(
            list[dict[str, str]],
            self._list_primitives(
                self._path(path), 'firmware',
                os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id),
        )

    def list(
        self,
        associated: bool | str | None = None,
        maintenance: bool | str | None = None,
        marker: str | None = None,
        limit: int | None = None,
        detail: bool = False,
        sort_key: str | None = None,
        sort_dir: str | None = None,
        fields: list[str] | None = None,
        provision_state: str | None = None,
        driver: str | None = None,
        resource_class: str | None = None,
        chassis: str | None = None,
        fault: str | None = None,
        os_ironic_api_version: str | None = None,
        conductor_group: str | None = None,
        conductor: str | None = None,
        owner: str | None = None,
        retired: bool | str | None = None,
        lessee: str | None = None,
        shards: list[str] | None = None,
        sharded: bool | str | None = None,
        parent_node: str | None = None,
        include_children: bool | None = None,
        description_contains: str | None = None,
        global_request_id: str | None = None,
        instance_name: str | None = None,
    ) -> list[Node]:
        """Retrieve a list of nodes.

        :param associated: Optional. Either a Boolean or a string
                           representation of a Boolean that indicates whether
                           to return a list of associated (True or "True") or
                           unassociated (False or "False") nodes.
        :param maintenance: Optional. Either a Boolean or a string
                            representation of a Boolean that indicates whether
                            to return nodes in maintenance mode (True or
                            "True"), or not in maintenance mode (False or
                            "False").
        :param retired: Optional. Either a Boolean or a string representation
                        of a Boolean that indicates whether to return retired
                        nodes (True or "True").
        :param provision_state: Optional. String value to get only nodes in
                                that provision state.
        :param marker: Optional, the UUID of a node, eg the last
                       node from a previous result set. Return
                       the next result set.
        :param limit: The maximum number of results to return per
                      request, if:

            1) limit > 0, the maximum number of nodes to return.
            2) limit == 0, return the entire list of nodes.
            3) limit param is NOT specified (None), the number of items
               returned respect the maximum imposed by the Ironic API
               (see Ironic's api.max_limit option).

        :param detail: Optional, boolean whether to return detailed information
                       about nodes.

        :param sort_key: Optional, field used for sorting.

        :param sort_dir: Optional, direction of sorting, either 'asc' (the
                         default) or 'desc'.

        :param fields: Optional, a list with a specified set of fields
                       of the resource to be returned. Can not be used
                       when 'detail' is set.

        :param driver: Optional. String value to get only nodes using that
                       driver.

        :param resource_class: Optional. String value to get only nodes
                               with the given resource class set.

        :param chassis: Optional, the UUID of a chassis. Used to get only
                        nodes of this chassis.

        :param fault: Optional. String value to get only nodes with
                      specified fault.

        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.

        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.

        :param conductor_group: Optional. String value to get only nodes
                                with the given conductor group set.
        :param conductor: Optional. String value to get only nodes
                          mapped to the given conductor.
        :param owner: Optional. String value to get only nodes
                      mapped to a specific owner.
        :param lessee: Optional. String value to get only nodes
                       mapped to a specific lessee.
        :param shards: Optional. A list with a specified set of shards
                      to limit node returns to.
        :param sharded: Optional. Boolean value, when true get only nodes
                        with a non-null node.shard value, when false get only
                        nodes with a null node.shard value. None is a noop.
                        with a non-null node.shard value.
        :param parent_node: Optional. String value used to retrieve child
                            nodes with the supplied parent node.
        :param include_children: Optional. Boolean Value, only True is valid.
                                 Tells the ironic API to enumerate all child
                                 nodes which are normally hidden from the
                                 node list.
        :param description_contains: Optional. String value to get nodes
                                 with description contains specified value.
        :param instance_name: Optional. String value to get only nodes with
                               the given instance_name set.
        :returns: A list of nodes.

        """
        if limit is not None:
            limit = int(limit)

        if detail and fields:
            raise exc.InvalidAttribute(_("Can't fetch a subset of fields "
                                         "with 'detail' set"))

        filters = utils.common_filters(marker, limit, sort_key, sort_dir,
                                       fields)
        if associated is not None:
            filters.append('associated=%s' % associated)
        if maintenance is not None:
            filters.append('maintenance=%s' % maintenance)
        if retired is not None:
            filters.append('retired=%s' % retired)
        if fault is not None:
            filters.append('fault=%s' % fault)
        if provision_state is not None:
            filters.append('provision_state=%s' % provision_state)
        if driver is not None:
            filters.append('driver=%s' % driver)
        if resource_class is not None:
            filters.append('resource_class=%s' % resource_class)
        if chassis is not None:
            filters.append('chassis_uuid=%s' % chassis)
        if conductor_group is not None:
            filters.append('conductor_group=%s' % conductor_group)
        if conductor is not None:
            filters.append('conductor=%s' % conductor)
        if owner is not None:
            filters.append('owner=%s' % owner)
        if lessee is not None:
            filters.append('lessee=%s' % lessee)
        if sharded is not None:
            filters.append('sharded=%s' % sharded)
        if shards is not None:
            filters.append('shard=%s' % ','.join(shards))
        if parent_node is not None:
            filters.append('parent_node=%s' % parent_node)
        if include_children:
            # NOTE(TheJulia): Only valid if True.
            filters.append('include_children=True')
        if description_contains is not None:
            filters.append('description_contains=%s' % description_contains)
        if instance_name is not None:
            filters.append('instance_name=%s' % instance_name)

        path = ''
        if detail:
            path += 'detail'
        if filters:
            path += '?' + '&'.join(filters)
        if limit is None:
            return self._list(
                self._path(path), "nodes",
                os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id,
            )
        else:
            return self._list_pagination(
                self._path(path), "nodes", limit=limit,
                os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id,
            )
