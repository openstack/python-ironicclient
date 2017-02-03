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

import json

from tempest.lib.common.utils import data_utils
from tempest.lib import exceptions

from ironicclient.tests.functional import base


class TestCase(base.FunctionalTestBase):

    def openstack(self, *args, **kwargs):
        return self._ironic_osc(*args, **kwargs)

    def get_opts(self, fields=None, output_format='json'):
        """Get options for OSC output fields format.

        :param List fields: List of fields to get
        :param String output_format: Select output format
        :return: String of formatted options
        """
        if not fields:
            return ' -f {0}'.format(output_format)
        return ' -f {0} {1}'.format(output_format,
                                    ' '.join(['-c ' + it for it in fields]))

    def node_create(self, driver='fake', name=None, params=''):
        """Create baremetal node and add cleanup.

        :param String driver: Driver for a new node
        :param String name: Name for a new node
        :param String params: Additional args and kwargs
        :return: JSON object of created node
        """
        if not name:
            name = data_utils.rand_name('baremetal')

        opts = self.get_opts()
        output = self.openstack('baremetal node create {0} '
                                '--driver {1} --name {2} {3}'
                                .format(opts, driver, name, params))
        node = json.loads(output)
        self.addCleanup(self.node_delete, node['uuid'], True)
        if not output:
            self.fail('Baremetal node has not been created!')

        return node

    def node_list(self, fields=None, params=''):
        """List baremetal nodes.

        :param List fields: List of fields to show
        :param String params: Additional kwargs
        :return: list of JSON node objects
        """
        opts = self.get_opts(fields=fields)
        output = self.openstack('baremetal node list {0} {1}'
                                .format(opts, params))
        return json.loads(output)

    def node_show(self, identifier, fields=None, params=''):
        """Show specified baremetal node.

        :param String identifier: Name or UUID of the node
        :param List fields: List of fields to show
        :param List params: Additional kwargs
        :return: JSON object of node
        """
        opts = self.get_opts(fields)
        output = self.openstack('baremetal node show {0} {1} {2}'
                                .format(opts, identifier, params))
        return json.loads(output)

    def node_delete(self, identifier, ignore_exceptions=False):
        """Try to delete baremetal node by name or UUID.

        :param String identifier: Name or UUID of the node
        :param Bool ignore_exceptions: Ignore exception (needed for cleanUp)
        :return: raw values output
        :raise: CommandFailed exception when command fails to delete a node
        """
        try:
            return self.openstack('baremetal node delete {0}'
                                  .format(identifier))
        except exceptions.CommandFailed:
            if not ignore_exceptions:
                raise
