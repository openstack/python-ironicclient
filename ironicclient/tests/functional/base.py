# Copyright (c) 2016 Mirantis, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import configparser
import os

from tempest.lib.cli import base
from tempest.lib.common.utils import data_utils
from tempest.lib import exceptions

import ironicclient.tests.functional.utils as utils

DEFAULT_CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'test.conf')


class FunctionalTestBase(base.ClientTestBase):
    """Ironic base class, calls to ironicclient."""

    def setUp(self):
        super(FunctionalTestBase, self).setUp()
        self.client = self._get_clients()
        # NOTE(kromanenko) set ironic api version for portgroups
        self.pg_api_ver = '--ironic-api-version 1.25'

    def _get_clients(self):
        # NOTE(aarefiev): {toxinidir} is a current working directory, so
        # the tox env path is {toxinidir}/.tox
        venv_name = os.environ.get('OS_TESTENV_NAME', 'functional')
        cli_dir = os.path.join(os.path.abspath('.'), '.tox/%s/bin' % venv_name)

        config = self._get_config()
        if config.get('os_auth_url'):
            client = base.CLIClient(cli_dir=cli_dir,
                                    username=config['os_username'],
                                    password=config['os_password'],
                                    tenant_name=config['os_project_name'],
                                    uri=config['os_auth_url'])
            for keystone_object in 'user', 'project':
                domain_attr = 'os_%s_domain_id' % keystone_object
                if config.get(domain_attr):
                    setattr(self, domain_attr, config[domain_attr])
        else:
            self.ironic_url = config['ironic_url']
            client = base.CLIClient(cli_dir=cli_dir,
                                    ironic_url=self.ironic_url)
        return client

    def _get_config(self):
        config_file = os.environ.get('IRONICCLIENT_TEST_CONFIG',
                                     DEFAULT_CONFIG_FILE)
        config = configparser.ConfigParser()
        if not config.read(config_file):
            self.skipTest('Skipping, no test config found @ %s' % config_file)
        try:
            auth_strategy = config.get('functional', 'auth_strategy')
        except configparser.NoOptionError:
            auth_strategy = 'keystone'
        if auth_strategy not in ['keystone', 'noauth']:
            raise self.fail(
                'Invalid auth type specified: %s in functional must be '
                'one of: [keystone, noauth]' % auth_strategy)

        conf_settings = []
        keystone_v3_conf_settings = []
        if auth_strategy == 'keystone':
            conf_settings += ['os_auth_url', 'os_username',
                              'os_password', 'os_project_name']
            keystone_v3_conf_settings += ['os_user_domain_id',
                                          'os_project_domain_id',
                                          'os_identity_api_version']
        else:
            conf_settings += ['ironic_url']

        cli_flags = {}
        missing = []
        for c in conf_settings + keystone_v3_conf_settings:
            try:
                cli_flags[c] = config.get('functional', c)
            except configparser.NoOptionError:
                # NOTE(vdrok): Here we ignore the absence of KS v3 options as
                # v2 may be used. Keystone client will do the actual check of
                # the parameters' correctness.
                if c not in keystone_v3_conf_settings:
                    missing.append(c)
        if missing:
            self.fail('Missing required setting in test.conf (%(conf)s) for '
                      'auth_strategy=%(auth)s: %(missing)s' %
                      {'conf': config_file,
                       'auth': auth_strategy,
                       'missing': ','.join(missing)})
        return cli_flags

    def _cmd_no_auth(self, cmd, action, flags='', params=''):
        """Execute given command with noauth attributes.

        :param cmd: command to be executed
        :type cmd: string
        :param action: command on cli to run
        :type action: string
        :param flags: optional cli flags to use
        :type flags: string
        :param params: optional positional args to use
        :type params: string
        """
        flags = ('--os-endpoint %(url)s %(flags)s'
                 %
                 {'url': self.ironic_url,
                  'flags': flags})
        return base.execute(cmd, action, flags, params,
                            cli_dir=self.client.cli_dir)

    def _ironic(self, action, cmd='ironic', flags='', params='',
                merge_stderr=False):
        """Execute ironic command for the given action.

        :param action: the cli command to run using Ironic
        :type action: string
        :param cmd: the base of cli command to run
        :type action: string
        :param flags: any optional cli flags to use
        :type flags: string
        :param params: any optional positional args to use
        :type params: string
        :param merge_stderr: whether to merge stderr into the result
        :type merge_stderr: bool
        """
        if cmd == 'openstack':
            config = self._get_config()
            id_api_version = config.get('os_identity_api_version')
            if id_api_version:
                flags += ' --os-identity-api-version {}'.format(id_api_version)
        else:
            flags += ' --os-endpoint-type publicURL'

        if hasattr(self, 'ironic_url'):
            if cmd == 'openstack':
                flags += ' --os-auth-type none'
            return self._cmd_no_auth(cmd, action, flags, params)
        else:
            for keystone_object in 'user', 'project':
                domain_attr = 'os_%s_domain_id' % keystone_object
                if hasattr(self, domain_attr):
                    flags += ' --os-%(ks_obj)s-domain-id %(value)s' % {
                        'ks_obj': keystone_object,
                        'value': getattr(self, domain_attr)
                    }
            return self.client.cmd_with_auth(
                cmd, action, flags, params, merge_stderr=merge_stderr)

    def ironic(self, action, flags='', params='', parse=True):
        """Return parsed list of dicts with basic item info.

        :param action: the cli command to run using Ironic
        :type action: string
        :param flags: any optional cli flags to use
        :type flags: string
        :param params: any optional positional args to use
        :type params: string
        :param parse: return parsed list or raw output
        :type parse: bool
        """
        output = self._ironic(action=action, flags=flags, params=params)
        return self.parser.listing(output) if parse else output

    def get_table_headers(self, action, flags='', params=''):
        output = self._ironic(action=action, flags=flags, params=params)
        table = self.parser.table(output)
        return table['headers']

    def assertTableHeaders(self, field_names, table_headers):
        """Assert that field_names and table_headers are equal.

        :param field_names: field names from the output table of the cmd
        :param table_headers: table headers output from cmd
        """
        self.assertEqual(sorted(field_names), sorted(table_headers))

    def assertNodeStates(self, node_show, node_show_states):
        """Assert that node_show_states output corresponds to node_show output.

        :param node_show: output from node-show cmd
        :param node_show_states: output from node-show-states cmd
        """
        for key in node_show_states.keys():
            self.assertEqual(node_show_states[key], node_show[key])

    def assertNodeValidate(self, node_validate):
        """Assert that all interfaces present are valid.

        :param node_validate: output from node-validate cmd
        """
        self.assertNotIn('False', [x['Result'] for x in node_validate])

    def delete_node(self, node_id):
        """Delete node method works only with fake driver.

        :param node_id: node uuid
        :raises: CommandFailed exception when command fails to delete a node
        """
        node_list = self.list_nodes()

        if utils.get_object(node_list, node_id):
            node_show = self.show_node(node_id)
            if node_show['provision_state'] not in ('available',
                                                    'manageable',
                                                    'enroll'):
                self.ironic('node-set-provision-state',
                            params='{0} deleted'.format(node_id))
            if node_show['power_state'] not in ('None', 'off'):
                self.ironic('node-set-power-state',
                            params='{0} off'.format(node_id))
            self.ironic('node-delete', params=node_id)

            node_list_uuid = self.get_nodes_uuids_from_node_list()
            if node_id in node_list_uuid:
                self.fail('Ironic node {0} has not been deleted!'
                          .format(node_id))

    def create_node(self, driver='fake-hardware', params=''):
        node = self.ironic('node-create',
                           params='--driver {0} {1}'.format(driver, params))

        if not node:
            self.fail('Ironic node has not been created!')

        node = utils.get_dict_from_output(node)
        self.addCleanup(self.delete_node, node['uuid'])
        return node

    def show_node(self, node_id, params=''):
        node_show = self.ironic('node-show',
                                params='{0} {1}'.format(node_id, params))
        return utils.get_dict_from_output(node_show)

    def list_nodes(self, params=''):
        return self.ironic('node-list', params=params)

    def update_node(self, node_id, params):
        updated_node = self.ironic('node-update',
                                   params='{0} {1}'.format(node_id, params))
        return utils.get_dict_from_output(updated_node)

    def get_nodes_uuids_from_node_list(self):
        node_list = self.list_nodes()
        return [x['UUID'] for x in node_list]

    def show_node_states(self, node_id):
        show_node_states = self.ironic('node-show-states', params=node_id)
        return utils.get_dict_from_output(show_node_states)

    def set_node_maintenance(self, node_id, maintenance_mode, params=''):
        self.ironic(
            'node-set-maintenance',
            params='{0} {1} {2}'.format(node_id, maintenance_mode, params))

    def set_node_power_state(self, node_id, power_state, params=''):
        self.ironic('node-set-power-state',
                    params='{0} {1} {2}'
                    .format(node_id, power_state, params))

    def set_node_provision_state(self, node_id, provision_state, params=''):
        self.ironic('node-set-provision-state',
                    params='{0} {1} {2}'
                    .format(node_id, provision_state, params))

    def validate_node(self, node_id):
        return self.ironic('node-validate', params=node_id)

    def list_node_chassis(self, chassis_uuid, params=''):
        return self.ironic('chassis-node-list',
                           params='{0} {1}'.format(chassis_uuid, params))

    def get_nodes_uuids_from_chassis_node_list(self, chassis_uuid):
        chassis_node_list = self.list_node_chassis(chassis_uuid)
        return [x['UUID'] for x in chassis_node_list]

    def list_driver(self, params=''):
        return self.ironic('driver-list', params=params)

    def show_driver(self, driver_name):
        driver_show = self.ironic('driver-show', params=driver_name)
        return utils.get_dict_from_output(driver_show)

    def properties_driver(self, driver_name):
        return self.ironic('driver-properties', params=driver_name)

    def get_drivers_names(self):
        driver_list = self.list_driver()
        return [x['Supported driver(s)'] for x in driver_list]

    def delete_chassis(self, chassis_id, ignore_exceptions=False):
        try:
            self.ironic('chassis-delete', params=chassis_id)
        except exceptions.CommandFailed:
            if not ignore_exceptions:
                raise

    def get_chassis_uuids_from_chassis_list(self):
        chassis_list = self.list_chassis()
        return [x['UUID'] for x in chassis_list]

    def create_chassis(self, params=''):
        chassis = self.ironic('chassis-create', params=params)

        if not chassis:
            self.fail('Ironic chassis has not been created!')

        chassis = utils.get_dict_from_output(chassis)
        self.addCleanup(self.delete_chassis,
                        chassis['uuid'],
                        ignore_exceptions=True)
        return chassis

    def list_chassis(self, params=''):
        return self.ironic('chassis-list', params=params)

    def show_chassis(self, chassis_id, params=''):
        chassis_show = self.ironic('chassis-show',
                                   params='{0} {1}'.format(chassis_id, params))
        return utils.get_dict_from_output(chassis_show)

    def update_chassis(self, chassis_id, operation, params=''):
        updated_chassis = self.ironic(
            'chassis-update',
            params='{0} {1} {2}'.format(chassis_id, operation, params))
        return utils.get_dict_from_output(updated_chassis)

    def delete_port(self, port_id, ignore_exceptions=False):
        try:
            self.ironic('port-delete', params=port_id)
        except exceptions.CommandFailed:
            if not ignore_exceptions:
                raise

    def create_port(self,
                    node_id,
                    mac_address=None,
                    flags='',
                    params=''):

        if mac_address is None:
            mac_address = data_utils.rand_mac_address()

        port = self.ironic('port-create',
                           flags=flags,
                           params='--address {0} --node {1} {2}'
                           .format(mac_address, node_id, params))
        if not port:
            self.fail('Ironic port has not been created!')

        return utils.get_dict_from_output(port)

    def list_ports(self, params=''):
        return self.ironic('port-list', params=params)

    def show_port(self, port_id, params=''):
        port_show = self.ironic('port-show', params='{0} {1}'
                                .format(port_id, params))
        return utils.get_dict_from_output(port_show)

    def get_uuids_from_port_list(self):
        port_list = self.list_ports()
        return [x['UUID'] for x in port_list]

    def update_port(self, port_id, operation, flags='', params=''):
        updated_port = self.ironic('port-update',
                                   flags=flags,
                                   params='{0} {1} {2}'
                                   .format(port_id, operation, params))
        return utils.get_dict_from_output(updated_port)

    def create_portgroup(self, node_id, params=''):
        """Create a new portgroup."""
        portgroup = self.ironic('portgroup-create',
                                flags=self.pg_api_ver,
                                params='--node {0} {1}'
                                .format(node_id, params))
        if not portgroup:
            self.fail('Ironic portgroup failed to create!')
        portgroup = utils.get_dict_from_output(portgroup)
        self.addCleanup(self.delete_portgroup, portgroup['uuid'],
                        ignore_exceptions=True)
        return portgroup

    def delete_portgroup(self, portgroup_id, ignore_exceptions=False):
        """Delete a port group."""
        try:
            self.ironic('portgroup-delete',
                        flags=self.pg_api_ver,
                        params=portgroup_id)
        except exceptions.CommandFailed:
            if not ignore_exceptions:
                raise

    def list_portgroups(self, params=''):
        """List the port groups."""
        return self.ironic('portgroup-list',
                           flags=self.pg_api_ver,
                           params=params)

    def show_portgroup(self, portgroup_id, params=''):
        """Show detailed information about a port group."""
        portgroup_show = self.ironic('portgroup-show',
                                     flags=self.pg_api_ver,
                                     params='{0} {1}'
                                     .format(portgroup_id, params))
        return utils.get_dict_from_output(portgroup_show)

    def update_portgroup(self, portgroup_id, op, params=''):
        """Update information about a port group."""
        updated_portgroup = self.ironic('portgroup-update',
                                        flags=self.pg_api_ver,
                                        params='{0} {1} {2}'
                                        .format(portgroup_id, op, params))
        return utils.get_dict_from_output(updated_portgroup)

    def get_portgroup_uuids_from_portgroup_list(self):
        """Get UUIDs from list of port groups."""
        portgroup_list = self.list_portgroups()
        return [x['UUID'] for x in portgroup_list]

    def portgroup_port_list(self, portgroup_id, params=''):
        """List the ports associated with a port group."""
        return self.ironic('portgroup-port-list', flags=self.pg_api_ver,
                           params='{0} {1}'.format(portgroup_id, params))
