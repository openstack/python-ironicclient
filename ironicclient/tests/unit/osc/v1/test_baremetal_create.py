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

import mock

from osc_lib.tests import utils as oscutils

from ironicclient.osc.v1 import baremetal_create
from ironicclient.tests.unit.osc.v1 import fakes as baremetal_fakes
from ironicclient.v1 import create_resources


class TestBaremetalCreate(baremetal_fakes.TestBaremetal):
    def setUp(self):
        super(TestBaremetalCreate, self).setUp()
        self.cmd = baremetal_create.CreateBaremetal(self.app, None)

    def test_baremetal_create_no_args(self):
        arglist = []
        verifylist = []
        self.assertRaises(oscutils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    @mock.patch.object(create_resources, 'create_resources', autospec=True)
    def test_baremetal_create_resource_files(self, mock_create):
        arglist = ['file.yaml', 'file.json']
        verifylist = [('resource_files', ['file.yaml', 'file.json'])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        mock_create.assert_called_once_with(self.app.client_manager.baremetal,
                                            ['file.yaml', 'file.json'])
