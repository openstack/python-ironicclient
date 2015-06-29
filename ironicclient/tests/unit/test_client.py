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

import fixtures
import mock

import ironicclient
from ironicclient.client import get_client
from ironicclient.common import filecache
from ironicclient import exc
from ironicclient.tests.unit import utils
from ironicclient.v1 import client as v1


def fake_get_ksclient(**kwargs):
    return utils.FakeKeystone('KSCLIENT_AUTH_TOKEN')


class ClientTest(utils.BaseTestCase):

    def test_get_client_with_auth_token_ironic_url(self):
        self.useFixture(fixtures.MonkeyPatch(
            'ironicclient.client._get_ksclient', fake_get_ksclient))
        kwargs = {
            'ironic_url': 'http://ironic.example.org:6385/',
            'os_auth_token': 'USER_AUTH_TOKEN',
        }
        client = get_client('1', **kwargs)

        self.assertEqual('USER_AUTH_TOKEN', client.http_client.auth_token)
        self.assertEqual('http://ironic.example.org:6385/',
                         client.http_client.endpoint)

    def test_get_client_no_auth_token(self):
        self.useFixture(fixtures.MonkeyPatch(
            'ironicclient.client._get_ksclient', fake_get_ksclient))
        kwargs = {
            'os_tenant_name': 'TENANT_NAME',
            'os_username': 'USERNAME',
            'os_password': 'PASSWORD',
            'os_auth_url': 'http://localhost:35357/v2.0',
            'os_auth_token': '',
        }
        client = get_client('1', **kwargs)

        self.assertEqual('KSCLIENT_AUTH_TOKEN', client.http_client.auth_token)
        self.assertEqual('http://localhost:6385/v1/f14b41234',
                         client.http_client.endpoint)
        self.assertEqual(fake_get_ksclient().auth_ref,
                         client.http_client.auth_ref)

    def test_get_client_with_region_no_auth_token(self):
        self.useFixture(fixtures.MonkeyPatch(
            'ironicclient.client._get_ksclient', fake_get_ksclient))
        kwargs = {
            'os_tenant_name': 'TENANT_NAME',
            'os_username': 'USERNAME',
            'os_password': 'PASSWORD',
            'os_region_name': 'REGIONONE',
            'os_auth_url': 'http://localhost:35357/v2.0',
            'os_auth_token': '',
        }
        client = get_client('1', **kwargs)

        self.assertEqual('KSCLIENT_AUTH_TOKEN', client.http_client.auth_token)
        self.assertEqual('http://regionhost:6385/v1/f14b41234',
                         client.http_client.endpoint)
        self.assertEqual(fake_get_ksclient().auth_ref,
                         client.http_client.auth_ref)

    def test_get_client_with_auth_token(self):
        self.useFixture(fixtures.MonkeyPatch(
            'ironicclient.client._get_ksclient', fake_get_ksclient))
        kwargs = {
            'os_tenant_name': 'TENANT_NAME',
            'os_username': 'USERNAME',
            'os_password': 'PASSWORD',
            'os_auth_url': 'http://localhost:35357/v2.0',
            'os_auth_token': 'USER_AUTH_TOKEN',
        }
        client = get_client('1', **kwargs)

        self.assertEqual('USER_AUTH_TOKEN', client.http_client.auth_token)
        self.assertEqual('http://localhost:6385/v1/f14b41234',
                         client.http_client.endpoint)
        self.assertEqual(fake_get_ksclient().auth_ref,
                         client.http_client.auth_ref)

    def test_get_client_with_region_name_auth_token(self):
        self.useFixture(fixtures.MonkeyPatch(
            'ironicclient.client._get_ksclient', fake_get_ksclient))
        kwargs = {
            'os_tenant_name': 'TENANT_NAME',
            'os_username': 'USERNAME',
            'os_password': 'PASSWORD',
            'os_auth_url': 'http://localhost:35357/v2.0',
            'os_region_name': 'REGIONONE',
            'os_auth_token': 'USER_AUTH_TOKEN',
        }
        client = get_client('1', **kwargs)

        self.assertEqual('USER_AUTH_TOKEN', client.http_client.auth_token)
        self.assertEqual('http://regionhost:6385/v1/f14b41234',
                         client.http_client.endpoint)
        self.assertEqual(fake_get_ksclient().auth_ref,
                         client.http_client.auth_ref)

    def test_get_client_no_url_and_no_token(self):
        self.useFixture(fixtures.MonkeyPatch(
            'ironicclient.client._get_ksclient', fake_get_ksclient))
        kwargs = {
            'os_tenant_name': 'TENANT_NAME',
            'os_username': 'USERNAME',
            'os_password': 'PASSWORD',
            'os_auth_url': '',
            'os_auth_token': '',
        }
        self.assertRaises(exc.AmbiguousAuthSystem, get_client, '1', **kwargs)
        # test the alias as well to ensure backwards compatibility
        self.assertRaises(exc.AmbigiousAuthSystem, get_client, '1', **kwargs)

    def test_ensure_auth_ref_propagated(self):
        ksclient = fake_get_ksclient
        self.useFixture(fixtures.MonkeyPatch(
            'ironicclient.client._get_ksclient', ksclient))
        kwargs = {
            'os_tenant_name': 'TENANT_NAME',
            'os_username': 'USERNAME',
            'os_password': 'PASSWORD',
            'os_auth_url': 'http://localhost:35357/v2.0',
            'os_auth_token': '',
        }
        client = get_client('1', **kwargs)

        self.assertEqual(ksclient().auth_ref, client.http_client.auth_ref)

    @mock.patch.object(filecache, 'retrieve_data', autospec=True)
    @mock.patch.object(ironicclient.client, '_get_ksclient', autospec=True)
    def _get_client_with_api_version(self, version, mock_ksclient,
                                     mock_retrieve_data):
        mock_ksclient.return_value = fake_get_ksclient()
        kwargs = {
            'os_tenant_name': 'TENANT_NAME',
            'os_username': 'USERNAME',
            'os_password': 'PASSWORD',
            'os_auth_url': 'http://localhost:35357/v2.0',
            'os_auth_token': '',
            'os_ironic_api_version': version,
        }
        client = get_client('1', **kwargs)
        self.assertEqual(0, mock_retrieve_data.call_count)
        self.assertEqual(version, client.http_client.os_ironic_api_version)
        self.assertEqual('user', client.http_client.api_version_select_state)

    def test_get_client_with_api_version_latest(self):
        self._get_client_with_api_version("latest")

    def test_get_client_with_api_version_numeric(self):
        self._get_client_with_api_version("1.4")

    @mock.patch.object(filecache, 'retrieve_data', autospec=True)
    @mock.patch.object(ironicclient.client, '_get_ksclient', autospec=True)
    def test_get_client_default_version_set_no_cache(self, mock_ksclient,
                                                     mock_retrieve_data):
        mock_ksclient.return_value = fake_get_ksclient()
        mock_retrieve_data.return_value = None
        kwargs = {
            'os_tenant_name': 'TENANT_NAME',
            'os_username': 'USERNAME',
            'os_password': 'PASSWORD',
            'os_auth_url': 'http://localhost:35357/v2.0',
            'os_auth_token': '',
        }
        client = get_client('1', **kwargs)
        mock_retrieve_data.assert_called_once_with(
            host=utils.DEFAULT_TEST_HOST,
            port=utils.DEFAULT_TEST_PORT)
        self.assertEqual(v1.DEFAULT_VER,
                         client.http_client.os_ironic_api_version)
        self.assertEqual('default',
                         client.http_client.api_version_select_state)

    @mock.patch.object(filecache, 'retrieve_data', autospec=True)
    @mock.patch.object(ironicclient.client, '_get_ksclient', autospec=True)
    def test_get_client_default_version_set_cached(self, mock_ksclient,
                                                   mock_retrieve_data):
        version = '1.3'
        # Make sure we don't coincidentally succeed
        self.assertNotEqual(v1.DEFAULT_VER, version)
        mock_ksclient.return_value = fake_get_ksclient()
        mock_retrieve_data.return_value = version
        kwargs = {
            'os_tenant_name': 'TENANT_NAME',
            'os_username': 'USERNAME',
            'os_password': 'PASSWORD',
            'os_auth_url': 'http://localhost:35357/v2.0',
            'os_auth_token': '',
        }
        client = get_client('1', **kwargs)
        mock_retrieve_data.assert_called_once_with(host=mock.ANY,
                                                   port=mock.ANY)
        self.assertEqual(version, client.http_client.os_ironic_api_version)
        self.assertEqual('cached', client.http_client.api_version_select_state)
