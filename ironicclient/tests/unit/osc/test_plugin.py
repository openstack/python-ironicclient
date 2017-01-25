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

import mock
import testtools

from ironicclient.osc import plugin
from ironicclient.tests.unit.osc import fakes
from ironicclient.v1 import client


class MakeClientTest(testtools.TestCase):

    @mock.patch.object(client, 'Client', autospec=True)
    def test_make_client(self, mock_client):
        instance = fakes.FakeClientManager()
        instance.get_endpoint_for_service_type = mock.Mock(
            return_value='endpoint')
        plugin.make_client(instance)
        mock_client.assert_called_once_with(os_ironic_api_version='1.6',
                                            session=instance.session,
                                            region_name=instance._region_name,
                                            endpoint='endpoint')
        instance.get_endpoint_for_service_type.assert_called_once_with(
            'baremetal', region_name=instance._region_name,
            interface=instance.interface)
