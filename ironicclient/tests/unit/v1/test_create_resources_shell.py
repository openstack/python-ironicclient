#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import mock

from ironicclient.tests.unit import utils
from ironicclient.v1 import create_resources
from ironicclient.v1 import create_resources_shell


class TestCreateResourcesShell(utils.BaseTestCase):
    def setUp(self):
        super(TestCreateResourcesShell, self).setUp()
        self.client = mock.MagicMock(autospec=True)

    @mock.patch.object(create_resources, 'create_resources', autospec=True)
    def test_create_shell(self, mock_create_resources):
        args = mock.MagicMock()
        files = ['file1', 'file2', 'file3']
        args.resource_files = files
        create_resources_shell.do_create(self.client, args)
        mock_create_resources.assert_called_once_with(self.client, files)
