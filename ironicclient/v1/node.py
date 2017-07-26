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

import logging
import os
import time

from oslo_utils import strutils

from ironicclient.common import base
from ironicclient.common.i18n import _
from ironicclient.common import utils
from ironicclient import exc
from ironicclient.v1 import volume_connector
from ironicclient.v1 import volume_target

_power_states = {
    'on': 'power on',
    'off': 'power off',
    'reboot': 'rebooting',
    'soft off': 'soft power off',
    'soft reboot': 'soft rebooting',
}


LOG = logging.getLogger(__name__)
_DEFAULT_POLL_INTERVAL = 2


class Node(base.Resource):
    def __repr__(self):
        return "<Node %s>" % self._info


class NodeManager(base.CreateManager):
    resource_class = Node
    _creation_attributes = ['chassis_uuid', 'driver', 'driver_info',
                            'extra', 'uuid', 'properties', 'name',
                            'boot_interface', 'console_interface',
                            'deploy_interface', 'inspect_interface',
                            'management_interface', 'network_interface',
                            'power_interface', 'raid_interface',
                            'storage_interface', 'vendor_interface',
                            'resource_class']
    _resource_name = 'nodes'

    def list(self, associated=None, maintenance=None, marker=None, limit=None,
             detail=False, sort_key=None, sort_dir=None, fields=None,
             provision_state=None, driver=None, resource_class=None,
             chassis=None):
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
        if provision_state is not None:
            filters.append('provision_state=%s' % provision_state)
        if driver is not None:
            filters.append('driver=%s' % driver)
        if resource_class is not None:
            filters.append('resource_class=%s' % resource_class)
        if chassis is not None:
            filters.append('chassis_uuid=%s' % chassis)

        path = ''
        if detail:
            path += 'detail'
        if filters:
            path += '?' + '&'.join(filters)

        if limit is None:
            return self._list(self._path(path), "nodes")
        else:
            return self._list_pagination(self._path(path), "nodes",
                                         limit=limit)

    def list_ports(self, node_id, marker=None, limit=None, sort_key=None,
                   sort_dir=None, detail=False, fields=None):
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
            return self._list(self._path(path), "ports")
        else:
            return self._list_pagination(self._path(path), "ports",
                                         limit=limit)

    def list_volume_connectors(self, node_id, marker=None, limit=None,
                               sort_key=None, sort_dir=None, detail=False,
                               fields=None):
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

        if limit is None:
            return self._list(self._path(path), response_key="connectors",
                              obj_class=volume_connector.VolumeConnector)
        else:
            return self._list_pagination(
                self._path(path), response_key="connectors", limit=limit,
                obj_class=volume_connector.VolumeConnector)

    def list_volume_targets(self, node_id, marker=None, limit=None,
                            sort_key=None, sort_dir=None, detail=False,
                            fields=None):
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

        if limit is None:
            return self._list(self._path(path), response_key="targets",
                              obj_class=volume_target.VolumeTarget)
        else:
            return self._list_pagination(
                self._path(path), response_key="targets", limit=limit,
                obj_class=volume_target.VolumeTarget)

    def get(self, node_id, fields=None):
        return self._get(resource_id=node_id, fields=fields)

    def get_by_instance_uuid(self, instance_uuid, fields=None):
        path = '?instance_uuid=%s' % instance_uuid
        if fields is not None:
            path += '&fields=' + ','.join(fields)
        else:
            path = 'detail' + path

        nodes = self._list(self._path(path), 'nodes')
        # get all the details of the node assuming that
        # filtering by instance_uuid returns a collection
        # of one node if successful.
        if len(nodes) == 1:
            return nodes[0]
        else:
            raise exc.NotFound()

    def delete(self, node_id):
        return self._delete(resource_id=node_id)

    def update(self, node_id, patch, http_method='PATCH'):
        return self._update(resource_id=node_id, patch=patch,
                            method=http_method)

    def vendor_passthru(self, node_id, method, args=None,
                        http_method=None):
        """Issue requests for vendor-specific actions on a given node.

        :param node_id: The UUID of the node.
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

        path = "%s/vendor_passthru/%s" % (node_id, method)
        if http_method in ('POST', 'PUT', 'PATCH'):
            return self.update(path, args, http_method=http_method)
        elif http_method == 'DELETE':
            return self.delete(path)
        elif http_method == 'GET':
            return self.get(path)
        else:
            raise exc.InvalidAttribute(
                _('Unknown HTTP method: %s') % http_method)

    def vif_list(self, node_ident):
        """List VIFs attached to a given node.

        :param node_ident: The UUID or Name of the node.
        """
        path = "%s/vifs" % node_ident

        return self._list(self._path(path), "vifs")

    def vif_attach(self, node_ident, vif_id, **kwargs):
        """Attach VIF to a given node.

        :param node_ident: The UUID or Name of the node.
        :param vif_id: The UUID or Name of the VIF to attach.
        :param kwargs: A dictionary containing the attributes of the resource
                       that will be created.
        """
        path = "%s/vifs" % node_ident
        data = {"id": vif_id}
        if 'id' in kwargs:
            raise exc.InvalidAttribute("The attribute 'id' can't be "
                                       "specified in vif-info")
        data.update(kwargs)
        # TODO(vdrok): cleanup places doing custom path and http_method
        self.update(path, data, http_method="POST")

    def vif_detach(self, node_ident, vif_id):
        """Detach VIF from a given node.

        :param node_ident: The UUID or Name of the node.
        :param vif_id: The UUID or Name of the VIF to detach.
        """
        path = "%s/vifs/%s" % (node_ident, vif_id)
        self.delete(path)

    def set_maintenance(self, node_id, state, maint_reason=None):
        """Set the maintenance mode for the node.

        :param node_id: The UUID of the node.
        :param state: the maintenance mode; either a Boolean or a string
                      representation of a Boolean (eg, 'true', 'on', 'false',
                      'off'). True to put the node in maintenance mode; False
                      to take the node out of maintenance mode.
        :param maint_reason: Optional string. Reason for putting node
                             into maintenance mode.
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
            return self.update(path, reason, http_method='PUT')
        else:
            return self.delete(path)

    def set_power_state(self, node_id, state, soft=False, timeout=None):
        """Sets power state for a node.

        :param node_id: Node identifier
        :param state: One of target power state, 'on', 'off', or 'reboot'
        :param soft: The flag for graceful power 'off' or 'reboot'
        :param timeout: The timeout (in seconds) positive integer value (> 0)
        :raises: ValueError if 'soft' or 'timeout' option is invalid
        :returns: The status of the request
        """
        if state == 'on' and soft:
            raise ValueError(
                _("'soft' option is invalid for the power-state 'on'"))

        path = "%s/states/power" % node_id

        requested_state = 'soft ' + state if soft else state
        target = _power_states.get(requested_state, state)

        body = {'target': target}
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

        return self.update(path, body, http_method='PUT')

    def set_target_raid_config(self, node_ident, target_raid_config):
        """Sets target_raid_config for a node.

        :param node_ident: Node identifier
        :param target_raid_config: A dictionary with the target RAID
            configuration; may be empty.
        :returns: status of the request
        """
        path = "%s/states/raid" % node_ident
        return self.update(path, target_raid_config, http_method='PUT')

    def validate(self, node_uuid):
        path = "%s/validate" % node_uuid
        return self.get(path)

    def set_provision_state(self, node_uuid, state, configdrive=None,
                            cleansteps=None):
        """Set the provision state for the node.

        :param node_uuid: The UUID or name of the node.
        :param state: The desired provision state. One of 'active', 'deleted',
             'rebuild', 'inspect', 'provide', 'manage', 'clean', 'abort'.
        :param configdrive: A gzipped, base64-encoded configuration drive
            string OR the path to the configuration drive file OR the path to
            a directory containing the config drive files. In case it's a
            directory, a config drive will be generated from it. This is only
            valid when setting state to 'active'.
        :param cleansteps: The clean steps as a list of clean-step
            dictionaries; each dictionary should have keys 'interface' and
            'step', and optional key 'args'. This must be specified (and is
            only valid) when setting provision-state to 'clean'.
        :raises: InvalidAttribute if there was an error with the clean steps
        :returns: The status of the request
        """

        path = "%s/states/provision" % node_uuid
        body = {'target': state}
        if configdrive:
            if os.path.isfile(configdrive):
                with open(configdrive, 'rb') as f:
                    configdrive = f.read()
            if os.path.isdir(configdrive):
                configdrive = utils.make_configdrive(configdrive)

            body['configdrive'] = configdrive
        elif cleansteps:
            body['clean_steps'] = cleansteps

        return self.update(path, body, http_method='PUT')

    def states(self, node_uuid):
        path = "%s/states" % node_uuid
        return self.get(path)

    def get_console(self, node_uuid):
        path = "%s/states/console" % node_uuid
        return self._get_as_dict(path)

    def set_console_mode(self, node_uuid, enabled):
        """Set the console mode for the node.

        :param node_uuid: The UUID of the node.
        :param enabled: Either a Boolean or a string representation of a
                        Boolean. True to enable the console; False to disable.

        """
        path = "%s/states/console" % node_uuid
        target = {'enabled': enabled}
        return self.update(path, target, http_method='PUT')

    def set_boot_device(self, node_uuid, boot_device, persistent=False):
        path = "%s/management/boot_device" % node_uuid
        target = {'boot_device': boot_device, 'persistent': persistent}
        return self.update(path, target, http_method='PUT')

    def get_boot_device(self, node_uuid):
        path = "%s/management/boot_device" % node_uuid
        return self._get_as_dict(path)

    def inject_nmi(self, node_uuid):
        path = "%s/management/inject_nmi" % node_uuid
        return self.update(path, {}, http_method='PUT')

    def get_supported_boot_devices(self, node_uuid):
        path = "%s/management/boot_device/supported" % node_uuid
        return self._get_as_dict(path)

    def get_vendor_passthru_methods(self, node_ident):
        path = "%s/vendor_passthru/methods" % node_ident
        return self._get_as_dict(path)

    def wait_for_provision_state(self, node_ident, expected_state,
                                 timeout=0,
                                 poll_interval=_DEFAULT_POLL_INTERVAL,
                                 poll_delay_function=None,
                                 fail_on_unexpected_state=True):
        """Helper function to wait for a node to reach a given state.

        Polls Ironic API in a loop until node gets to a requested state.

        Fails in the following cases:
        * Timeout (if provided) is reached
        * Node's last_error gets set to a non-empty value
        * Unexpected stable state is reached and fail_on_unexpected_state is on
        * Error state is reached (if it's not equal to expected_state)

        :param node_ident: node UUID or name
        :param expected_state: expected final provision state
        :param timeout: timeout in seconds, no timeout if 0
        :param poll_interval: interval in seconds between 2 poll
        :param poll_delay_function: function to use to wait between polls
            (defaults to time.sleep). Should take one argument - delay time
            in seconds. Any exceptions raised inside it will abort the wait.
        :param fail_on_unexpected_state: whether to fail if the nodes
            reaches a different stable state.
        :raises: StateTransitionFailed if node reached an error state
        :raises: StateTransitionTimeout on timeout
        """
        if not isinstance(timeout, (int, float)) or timeout < 0:
            raise ValueError(_('Timeout must be a non-negative number'))

        threshold = time.time() + timeout
        expected_state = expected_state.lower()
        poll_delay_function = (time.sleep if poll_delay_function is None
                               else poll_delay_function)
        if not callable(poll_delay_function):
            raise TypeError(_('poll_delay_function must be callable'))

        # TODO(dtantsur): use version negotiation to request API 1.8 and use
        # the "fields" argument to reduce amount of data sent.
        while not timeout or time.time() < threshold:
            node = self.get(node_ident)
            if node.provision_state == expected_state:
                LOG.debug('Node %(node)s reached provision state %(state)s',
                          {'node': node_ident, 'state': expected_state})
                return

            # Note that if expected_state == 'error' we still succeed
            if (node.last_error or node.provision_state == 'error' or
                    node.provision_state.endswith(' failed')):
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
            poll_delay_function(poll_interval)

        raise exc.StateTransitionTimeout(
            _('Node %(node)s failed to reach state %(state)s in '
              '%(timeout)s seconds') % {'node': node_ident,
                                        'state': expected_state,
                                        'timeout': timeout})
