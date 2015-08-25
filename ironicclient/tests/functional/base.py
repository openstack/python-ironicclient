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

import os

import six
import six.moves.configparser as config_parser
from tempest_lib.cli import base


DEFAULT_CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'test.conf')


class FunctionalTestBase(base.ClientTestBase):
    """Ironic base class, calls to ironicclient."""
    def setUp(self):
        super(FunctionalTestBase, self).setUp()
        self.client = self._get_clients()

    def _get_clients(self):
        # NOTE(aarefiev): {toxinidir} is a current working directory, so
        # the tox env path is {toxinidir}/.tox
        cli_dir = os.path.join(os.path.abspath('.'), '.tox/functional/bin')

        config = self._get_config()
        if config.get('os_auth_url'):
            client = base.CLIClient(cli_dir=cli_dir,
                                    username=config['os_username'],
                                    password=config['os_password'],
                                    tenant_name=config['os_tenant_name'],
                                    uri=config['os_auth_url'])
        else:
            self.ironic_url = config['ironic_url']
            self.os_auth_token = config['os_auth_token']
            client = base.CLIClient(cli_dir=cli_dir,
                                    ironic_url=self.ironic_url,
                                    os_auth_token=self.os_auth_token)
        return client

    def _get_config(self):
        config_file = os.environ.get('IRONICCLIENT_TEST_CONFIG',
                                     DEFAULT_CONFIG_FILE)
        config = config_parser.SafeConfigParser()
        if not config.read(config_file):
            self.skipTest('Skipping, no test config found @ %s' % config_file)
        try:
            auth_strategy = config.get('functional', 'auth_strategy')
        except config_parser.NoOptionError:
            auth_strategy = 'keystone'
        if auth_strategy not in ['keystone', 'noauth']:
            raise self.fail(
                'Invalid auth type specified: %s in functional must be '
                'one of: [keystone, noauth]' % auth_strategy)

        conf_settings = []
        if auth_strategy == 'keystone':
            conf_settings += ['os_auth_url', 'os_username',
                              'os_password', 'os_tenant_name']
        else:
            conf_settings += ['os_auth_token', 'ironic_url']

        cli_flags = {}
        missing = []
        for c in conf_settings:
            try:
                cli_flags[c] = config.get('functional', c)
            except config_parser.NoOptionError:
                missing.append(c)
        if missing:
            self.fail('Missing required setting in test.conf (%(conf)s) for '
                      'auth_strategy=%(auth)s: %(missing)s' %
                      {'conf': config_file,
                       'auth': auth_strategy,
                       'missing': ','.join(missing)})
        return cli_flags

    def _cmd_no_auth(self, cmd, action, flags='', params=''):
        """Executes given command with noauth attributes.

        :param cmd: command to be executed
        :type cmd: string
        :param action: command on cli to run
        :type action: string
        :param flags: optional cli flags to use
        :type flags: string
        :param params: optional positional args to use
        :type params: string
        """
        flags = ('--os_auth_token %(token)s --ironic_url %(url)s %(flags)s'
                 %
                 {'token': self.os_auth_token,
                  'url': self.ironic_url,
                  'flags': flags})
        return base.execute(cmd, action, flags, params,
                            cli_dir=self.client.cli_dir)

    def ironic(self, action, flags='', params=''):
        """Executes ironic command for the given action.

        :param action: the cli command to run using Ironic
        :type action: string
        :param flags: any optional cli flags to use
        :type flags: string
        :param params: any optional positional args to use
        :type params: string
        """
        flags += ' --os-endpoint-type publicURL'
        if hasattr(self, 'os_auth_token'):
            return self._cmd_no_auth('ironic', action, flags, params)
        else:
            return self.client.cmd_with_auth('ironic', action, flags, params)

    def _try_delete_node(self, node_id):
        if node_id in self.ironic('node-list'):
            self.ironic('node-delete', params=node_id)

    def get_dict_from_output(self, output):
        """Create a dictionary from an output

        :param output: the output of the cmd
        """
        obj = {}
        items = self.parser.listing(output)
        for item in items:
            obj[item['Property']] = six.text_type(item['Value'])
        return obj

    def create_node(self, params=''):
        if not any(dr in params for dr in ('--driver', '-d')):
            params += '--driver fake'
        node = self.ironic('node-create', params=params)
        node = self.get_dict_from_output(node)
        self.addCleanup(self._try_delete_node, node['uuid'])
        return node

    def assertTableHeaders(self, field_names, output_lines):
        """Verify that output table has headers item listed in field_names.

        :param field_names: field names from the output table of the cmd
        :param output_lines: output table from cmd
        """
        table = self.parser.table(output_lines)
        headers = table['headers']
        for field in field_names:
            self.assertIn(field, headers)

    def assertNodeDeleted(self, node_id):
        """Verify that there isn't node with given id.

        :param node_id: node id to verify
        """
        self.assertNotIn(node_id, self.ironic('node-list'))
