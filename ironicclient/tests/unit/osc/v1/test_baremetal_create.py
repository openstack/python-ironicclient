#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import copy
import mock

from ironicclient import exc
from ironicclient.osc.v1 import baremetal_create
from ironicclient.tests.unit.osc.v1 import fakes as baremetal_fakes
from ironicclient.v1 import create_resources


class TestBaremetalCreate(baremetal_fakes.TestBaremetal):
    def setUp(self):
        super(TestBaremetalCreate, self).setUp()
        self.cmd = baremetal_create.CreateBaremetal(self.app, None)

    def test_baremetal_create_with_driver(self):
        self.baremetal_mock = self.app.client_manager.baremetal
        self.baremetal_mock.reset_mock()
        self.baremetal_mock.node.create.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.BAREMETAL),
                loaded=True,
            ))

        arglist = ['--driver', 'fake_driver']
        verifylist = [('driver', 'fake_driver')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(('chassis_uuid',
                          'instance_uuid',
                          'maintenance',
                          'name',
                          'power_state',
                          'provision_state',
                          'uuid'), columns)
        self.assertEqual(
            (baremetal_fakes.baremetal_chassis_uuid_empty,
             baremetal_fakes.baremetal_instance_uuid,
             baremetal_fakes.baremetal_maintenance,
             baremetal_fakes.baremetal_name,
             baremetal_fakes.baremetal_power_state,
             baremetal_fakes.baremetal_provision_state,
             baremetal_fakes.baremetal_uuid), tuple(data))

        self.baremetal_mock.node.create.assert_called_once_with(
            driver='fake_driver')

    def test_baremetal_create_no_args(self):
        parsed_args = self.check_parser(self.cmd, [], [])
        self.assertRaises(exc.ValidationError,
                          self.cmd.take_action, parsed_args)

    @mock.patch.object(create_resources, 'create_resources', autospec=True)
    def test_baremetal_create_resource_files(self, mock_create):
        arglist = ['file.yaml', 'file.json']
        verifylist = [('resource_files', ['file.yaml', 'file.json'])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.assertEqual((tuple(), tuple()), self.cmd.take_action(parsed_args))
        mock_create.assert_called_once_with(self.app.client_manager.baremetal,
                                            ['file.yaml', 'file.json'])
