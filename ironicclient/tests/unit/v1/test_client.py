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
from ironicclient.tests.unit import utils
from ironicclient.v1 import client


@mock.patch.object(http, '_construct_http_client', autospec=True)
class ClientTest(utils.BaseTestCase):

    session = mock.sentinel.session

    def test_client_user_api_version(self, http_client_mock):
        endpoint = 'http://ironic:6385'
        os_ironic_api_version = '1.15'

        client.Client(endpoint, session=self.session,
                      os_ironic_api_version=os_ironic_api_version)

        http_client_mock.assert_called_once_with(
            endpoint_override=endpoint, session=self.session,
            os_ironic_api_version=os_ironic_api_version,
            api_version_select_state='user')

    def test_client_user_api_version_with_downgrade(self, http_client_mock):
        endpoint = 'http://ironic:6385'
        os_ironic_api_version = '1.15'

        client.Client(endpoint, session=self.session,
                      os_ironic_api_version=os_ironic_api_version,
                      allow_api_version_downgrade=True)

        http_client_mock.assert_called_once_with(
            endpoint_override=endpoint, session=self.session,
            os_ironic_api_version=os_ironic_api_version,
            api_version_select_state='default')

    def test_client_user_api_version_latest_with_downgrade(self,
                                                           http_client_mock):
        endpoint = 'http://ironic:6385'
        os_ironic_api_version = 'latest'

        self.assertRaises(ValueError, client.Client, endpoint,
                          session=self.session,
                          allow_api_version_downgrade=True,
                          os_ironic_api_version=os_ironic_api_version)

    @mock.patch.object(filecache, 'retrieve_data', autospec=True)
    def test_client_cache_api_version(self, cache_mock, http_client_mock):
        endpoint = 'http://ironic:6385'
        os_ironic_api_version = '1.15'
        cache_mock.return_value = os_ironic_api_version

        client.Client(endpoint, session=self.session)

        cache_mock.assert_called_once_with(host='ironic', port='6385')
        http_client_mock.assert_called_once_with(
            endpoint_override=endpoint, session=self.session,
            os_ironic_api_version=os_ironic_api_version,
            api_version_select_state='cached')

    @mock.patch.object(filecache, 'retrieve_data', autospec=True)
    def test_client_default_api_version(self, cache_mock, http_client_mock):
        endpoint = 'http://ironic:6385'
        cache_mock.return_value = None

        client.Client(endpoint, session=self.session)

        cache_mock.assert_called_once_with(host='ironic', port='6385')
        http_client_mock.assert_called_once_with(
            endpoint_override=endpoint, session=self.session,
            os_ironic_api_version=client.DEFAULT_VER,
            api_version_select_state='default')

    def test_client_cache_version_no_endpoint_as_arg(self, http_client_mock):
        client.Client(session='fake_session', insecure=True)
        http_client_mock.assert_called_once_with(
            session='fake_session', insecure=True,
            os_ironic_api_version=client.DEFAULT_VER,
            api_version_select_state='default')

    def test_client_initialized_managers(self, http_client_mock):
        cl = client.Client('http://ironic:6385', session=self.session,
                           os_ironic_api_version='1.15')

        self.assertIsInstance(cl.node, client.node.NodeManager)
        self.assertIsInstance(cl.port, client.port.PortManager)
        self.assertIsInstance(cl.driver, client.driver.DriverManager)
        self.assertIsInstance(cl.chassis, client.chassis.ChassisManager)

    def test_negotiate_api_version(self, http_client_mock):
        endpoint = 'http://ironic:6385'
        os_ironic_api_version = 'latest'
        cl = client.Client(endpoint, session=self.session,
                           os_ironic_api_version=os_ironic_api_version)

        cl.negotiate_api_version()
        http_client_mock.assert_called_once_with(
            api_version_select_state='user', endpoint_override=endpoint,
            os_ironic_api_version='latest', session=self.session)
        # TODO(TheJulia): We should verify that negotiate_version
        # is being called in the client and returns a version,
        # although mocking might need to be restrutured to
        # properly achieve that.
