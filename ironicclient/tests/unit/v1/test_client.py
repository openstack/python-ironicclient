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

import mock

from ironicclient.common import filecache
from ironicclient.common import http
from ironicclient import exc
from ironicclient.tests.unit import utils
from ironicclient.v1 import client


@mock.patch.object(http, '_construct_http_client', autospec=True)
class ClientTest(utils.BaseTestCase):

    def test_client_user_api_version(self, http_client_mock):
        endpoint = 'http://ironic:6385'
        token = 'safe_token'
        os_ironic_api_version = '1.15'

        client.Client(endpoint, token=token,
                      os_ironic_api_version=os_ironic_api_version)

        http_client_mock.assert_called_once_with(
            endpoint, token=token,
            os_ironic_api_version=os_ironic_api_version,
            api_version_select_state='user')

    @mock.patch.object(filecache, 'retrieve_data', autospec=True)
    def test_client_cache_api_version(self, cache_mock, http_client_mock):
        endpoint = 'http://ironic:6385'
        token = 'safe_token'
        os_ironic_api_version = '1.15'
        cache_mock.return_value = os_ironic_api_version

        client.Client(endpoint, token=token)

        cache_mock.assert_called_once_with(host='ironic', port='6385')
        http_client_mock.assert_called_once_with(
            endpoint, token=token,
            os_ironic_api_version=os_ironic_api_version,
            api_version_select_state='cached')

    @mock.patch.object(filecache, 'retrieve_data', autospec=True)
    def test_client_default_api_version(self, cache_mock, http_client_mock):
        endpoint = 'http://ironic:6385'
        token = 'safe_token'
        cache_mock.return_value = None

        client.Client(endpoint, token=token)

        cache_mock.assert_called_once_with(host='ironic', port='6385')
        http_client_mock.assert_called_once_with(
            endpoint, token=token,
            os_ironic_api_version=client.DEFAULT_VER,
            api_version_select_state='default')

    def test_client_cache_version_no_endpoint_as_arg(self, http_client_mock):
        self.assertRaises(exc.EndpointException,
                          client.Client,
                          session='fake_session',
                          insecure=True,
                          endpoint_override='http://ironic:6385')

    def test_client_initialized_managers(self, http_client_mock):
        cl = client.Client('http://ironic:6385', token='safe_token',
                           os_ironic_api_version='1.15')

        self.assertIsInstance(cl.node, client.node.NodeManager)
        self.assertIsInstance(cl.port, client.port.PortManager)
        self.assertIsInstance(cl.driver, client.driver.DriverManager)
        self.assertIsInstance(cl.chassis, client.chassis.ChassisManager)
