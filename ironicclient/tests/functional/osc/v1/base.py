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

    driver_name = 'fake-hardware'

    def openstack(self, *args, **kwargs):
        return self._ironic(cmd='openstack', *args, **kwargs)

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

    @staticmethod
    def construct_cmd(*parts):
        return ' '.join(str(x) for x in parts)

    @staticmethod
    def generate_params(argument, params):
        """Generate parameters string.

        :param argument: argument
        :param params: values passed with argument
        """
        parts = []
        for key, value in params.items():
            parts.append('{} {}={}'.format(argument, key, value))
        return ' '.join(parts)

    def assert_dict_is_subset(self, expected, actual):
        """Check if expected keys/values exist in actual response body.

        Check if the expected keys and values are in the actual response body.

        :param expected: dict of key-value pairs that are expected to be in
                         'actual' dict.
        :param actual: dict of key-value pairs.
        """
        for key, value in expected.items():
            self.assertEqual(value, actual[key])

    def node_create(self, driver=driver_name, name=None, params=''):
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

    def port_create(self, node_id, mac_address=None, params=''):
        """Create baremetal port and add cleanup.

        :param String node_id: baremetal node UUID
        :param String mac_address: MAC address for port
        :param String params: Additional args and kwargs
        :return: JSON object of created port
        """
        if not mac_address:
            mac_address = data_utils.rand_mac_address()

        opts = self.get_opts()
        port = self.openstack('baremetal port create {0} '
                              '--node {1} {2} {3}'
                              .format(opts, node_id, mac_address, params))
        port = json.loads(port)
        if not port:
            self.fail('Baremetal port has not been created!')
        self.addCleanup(self.port_delete, port['uuid'], True)
        return port

    def port_list(self, fields=None, params=''):
        """List baremetal ports.

        :param List fields: List of fields to show
        :param String params: Additional kwargs
        :return: list of JSON port objects
        """
        opts = self.get_opts(fields=fields)
        output = self.openstack('baremetal port list {0} {1}'
                                .format(opts, params))
        return json.loads(output)

    def port_show(self, uuid, fields=None, params=''):
        """Show specified baremetal port.

        :param String uuid: UUID of the port
        :param List fields: List of fields to show
        :param List params: Additional kwargs
        :return: JSON object of port
        """
        opts = self.get_opts(fields)
        output = self.openstack('baremetal port show {0} {1} {2}'
                                .format(opts, uuid, params))
        return json.loads(output)

    def port_delete(self, uuid, ignore_exceptions=False):
        """Try to delete baremetal port by UUID.

        :param String uuid: UUID of the port
        :param Bool ignore_exceptions: Ignore exception (needed for cleanUp)
        :return: raw values output
        :raise: CommandFailed exception when command fails to delete a port
        """
        try:
            return self.openstack('baremetal port delete {0}'
                                  .format(uuid))
        except exceptions.CommandFailed:
            if not ignore_exceptions:
                raise

    def port_group_list(self, fields=None, params=''):
        """List baremetal port groups.

        :param List fields: List of fields to show
        :param String params: Additional kwargs
        :return: JSON object of port group list
        """
        opts = self.get_opts(fields=fields)
        output = self.openstack('baremetal port group list {0} {1}'
                                .format(opts, params))
        return json.loads(output)

    def port_group_create(self, node_id, name=None, params=''):
        """Create baremetal port group.

        :param String node_id: baremetal node UUID
        :param String name: port group name
        :param String params: Additional args and kwargs
        :return: JSON object of created port group
        """
        if not name:
            name = data_utils.rand_name('port_group')

        opts = self.get_opts()
        output = self.openstack(
            'baremetal port group create {0} --node {1} --name {2} {3}'
            .format(opts, node_id, name, params))

        port_group = json.loads(output)
        if not port_group:
            self.fail('Baremetal port group has not been created!')

        self.addCleanup(self.port_group_delete, port_group['uuid'],
                        params=params, ignore_exceptions=True)
        return port_group

    def port_group_delete(self, identifier, params='',
                          ignore_exceptions=False):
        """Try to delete baremetal port group by Name or UUID.

        :param String identifier: Name or UUID of the port group
        :param String params: temporary arg to pass api version.
        :param Bool ignore_exceptions: Ignore exception (needed for cleanUp)
        :return: raw values output
        :raise: CommandFailed exception if not ignore_exceptions
        """
        try:
            return self.openstack('baremetal port group delete {0} {1}'
                                  .format(identifier, params))
        except exceptions.CommandFailed:
            if not ignore_exceptions:
                raise

    def port_group_show(self, identifier, fields=None, params=''):
        """Show specified baremetal port group.

        :param String identifier: Name or UUID of the port group
        :param List fields: List of fields to show
        :param List params: Additional kwargs
        :return: JSON object of port group
        """
        opts = self.get_opts(fields)
        output = self.openstack('baremetal port group show {0} {1} {2}'
                                .format(identifier, opts, params))
        return json.loads(output)

    def chassis_create(self, params=''):
        """Create baremetal chassis and add cleanup.

        :param String params: Additional args and kwargs
        :return: JSON object of created chassis
        """
        opts = self.get_opts()
        chassis = self.openstack('baremetal chassis create {0} {1}'
                                 .format(opts, params))

        chassis = json.loads(chassis)
        if not chassis:
            self.fail('Baremetal chassis has not been created!')
        self.addCleanup(self.chassis_delete, chassis['uuid'], True)

        return chassis

    def chassis_delete(self, uuid, ignore_exceptions=False):
        """Try to delete baremetal chassis by UUID.

        :param String uuid: UUID of the chassis
        :param Bool ignore_exceptions: Ignore exception (needed for cleanUp)
        :return: raw values output
        :raise: CommandFailed exception when command fails to delete a chassis
        """
        try:
            return self.openstack('baremetal chassis delete {0}'
                                  .format(uuid))
        except exceptions.CommandFailed:
            if not ignore_exceptions:
                raise

    def chassis_list(self, fields=None, params=''):
        """List baremetal chassis.

        :param List fields: List of fields to show
        :param String params: Additional kwargs
        :return: list of JSON chassis objects
        """
        opts = self.get_opts(fields=fields)
        output = self.openstack('baremetal chassis list {0} {1}'
                                .format(opts, params))
        return json.loads(output)

    def chassis_show(self, uuid, fields=None, params=''):
        """Show specified baremetal chassis.

        :param String uuid: UUID of the chassis
        :param List fields: List of fields to show
        :param List params: Additional kwargs
        :return: JSON object of chassis
        """
        opts = self.get_opts(fields)
        chassis = self.openstack('baremetal chassis show {0} {1} {2}'
                                 .format(opts, uuid, params))
        return json.loads(chassis)

    def driver_show(self, driver_name, fields=None, params=''):
        """Show specified baremetal driver.

        :param String driver_name: Name of the driver
        :param List fields: List of fields to show
        :param List params: Additional kwargs
        :return: JSON object of driver
        """
        opts = self.get_opts(fields=fields)
        driver = self.openstack('baremetal driver show {0} {1} {2}'
                                .format(opts, driver_name, params))
        return json.loads(driver)

    def driver_list(self, fields=None, params=''):
        """List baremetal drivers.

        :param List fields: List of fields to show
        :param String params: Additional kwargs
        :return: list of JSON driver objects
        """
        opts = self.get_opts(fields=fields)
        output = self.openstack('baremetal driver list {0} {1}'
                                .format(opts, params))
        return json.loads(output)

    def conductor_show(self, hostname, fields=None, params=''):
        """Show specified baremetal conductors.

        :param String hostname: hostname of the conductor
        :param List fields: List of fields to show
        :param List params: Additional kwargs
        :return: JSON object of driver
        """
        opts = self.get_opts(fields=fields)
        output = self.openstack('baremetal conductor show {0} {1} {2}'
                                .format(opts, hostname, params))
        return json.loads(output)

    def conductor_list(self, fields=None, params=''):
        """List baremetal conductors.

        :param List fields: List of fields to show
        :param String params: Additional kwargs
        :return: list of JSON driver objects
        """
        opts = self.get_opts(fields=fields)
        output = self.openstack('baremetal conductor list {0} {1}'
                                .format(opts, params))
        return json.loads(output)

    def allocation_create(self, resource_class='allocation-test', params=''):
        opts = self.get_opts()
        output = self.openstack('baremetal allocation create {0} '
                                '--resource-class {1} {2}'
                                .format(opts, resource_class, params))
        allocation = json.loads(output)
        self.addCleanup(self.allocation_delete, allocation['uuid'], True)
        if not output:
            self.fail('Baremetal allocation has not been created!')

        return allocation

    def allocation_list(self, fields=None, params=''):
        """List baremetal allocations.

        :param List fields: List of fields to show
        :param String params: Additional kwargs
        :return: list of JSON allocation objects
        """
        opts = self.get_opts(fields=fields)
        output = self.openstack('baremetal allocation list {0} {1}'
                                .format(opts, params))
        return json.loads(output)

    def allocation_show(self, identifier, fields=None, params=''):
        """Show specified baremetal allocation.

        :param String identifier: Name or UUID of the allocation
        :param List fields: List of fields to show
        :param List params: Additional kwargs
        :return: JSON object of allocation
        """
        opts = self.get_opts(fields)
        output = self.openstack('baremetal allocation show {0} {1} {2}'
                                .format(opts, identifier, params))
        return json.loads(output)

    def allocation_delete(self, identifier, ignore_exceptions=False):
        """Try to delete baremetal allocation by name or UUID.

        :param String identifier: Name or UUID of the allocation
        :param Bool ignore_exceptions: Ignore exception (needed for cleanUp)
        :return: raw values output
        :raise: CommandFailed exception when command fails to delete
            an allocation
        """
        try:
            return self.openstack('baremetal allocation delete {0}'
                                  .format(identifier))
        except exceptions.CommandFailed:
            if not ignore_exceptions:
                raise

    def deploy_template_create(self, name, params=''):
        """Create baremetal deploy template and add cleanup.

        :param String name: deploy template name
        :param String params: additional parameters
        :return: JSON object of created deploy template
        """
        opts = self.get_opts()
        template = self.openstack('baremetal deploy template create {0} {1} '
                                  '{2}'.format(opts, name, params))
        template = json.loads(template)
        if not template:
            self.fail('Baremetal deploy template has not been created!')
        self.addCleanup(self.deploy_template_delete, template['uuid'], True)
        return template

    def deploy_template_list(self, fields=None, params=''):
        """List baremetal deploy templates.

        :param List fields: List of fields to show
        :param String params: Additional kwargs
        :return: list of JSON deploy template objects
        """
        opts = self.get_opts(fields=fields)
        output = self.openstack('baremetal deploy template list {0} {1}'
                                .format(opts, params))
        return json.loads(output)

    def deploy_template_show(self, identifier, fields=None, params=''):
        """Show specified baremetal deploy template.

        :param String identifier: Name or UUID of the deploy template
        :param List fields: List of fields to show
        :param List params: Additional kwargs
        :return: JSON object of deploy template
        """
        opts = self.get_opts(fields)
        output = self.openstack('baremetal deploy template show {0} {1} {2}'
                                .format(opts, identifier, params))
        return json.loads(output)

    def deploy_template_delete(self, identifier, ignore_exceptions=False):
        """Try to delete baremetal deploy template by UUID.

        :param String identifier: Name or UUID of the deploy template
        :param Bool ignore_exceptions: Ignore exception (needed for cleanUp)
        :return: raw values output
        :raise: CommandFailed exception when command fails to delete a deploy
            template
        """
        try:
            return self.openstack('baremetal deploy template delete {0}'
                                  .format(identifier))
        except exceptions.CommandFailed:
            if not ignore_exceptions:
                raise
