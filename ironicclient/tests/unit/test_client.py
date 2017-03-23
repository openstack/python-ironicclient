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

from keystoneauth1 import loading as kaloading

from ironicclient import client as iroclient
from ironicclient.common import filecache
from ironicclient.common import http
from ironicclient import exc
from ironicclient.tests.unit import utils
from ironicclient.v1 import client as v1


class ClientTest(utils.BaseTestCase):

    def test_get_client_with_auth_token_ironic_url(self):
        kwargs = {
            'ironic_url': 'http://ironic.example.org:6385/',
            'os_auth_token': 'USER_AUTH_TOKEN',
        }
        client = iroclient.get_client('1', **kwargs)

        self.assertEqual('USER_AUTH_TOKEN', client.http_client.auth_token)
        self.assertEqual('http://ironic.example.org:6385/',
                         client.http_client.endpoint)

    @mock.patch.object(filecache, 'retrieve_data', autospec=True)
    @mock.patch.object(kaloading.session, 'Session', autospec=True)
    @mock.patch.object(kaloading, 'get_plugin_loader', autospec=True)
    def _test_get_client(self, mock_ks_loader, mock_ks_session,
                         mock_retrieve_data, version=None,
                         auth='password', **kwargs):
        session = mock_ks_session.return_value.load_from_options.return_value
        session.get_endpoint.return_value = 'http://localhost:6385/v1/f14b4123'
        mock_ks_loader.return_value.load_from_options.return_value = 'auth'
        mock_retrieve_data.return_value = version

        client = iroclient.get_client('1', **kwargs)

        mock_ks_loader.assert_called_once_with(auth)
        mock_ks_session.return_value.load_from_options.assert_called_once_with(
            auth='auth', timeout=kwargs.get('timeout'),
            insecure=kwargs.get('insecure'), cert=kwargs.get('cert'),
            cacert=kwargs.get('cacert'), key=kwargs.get('key'))
        session.get_endpoint.assert_called_once_with(
            service_type=kwargs.get('os_service_type') or 'baremetal',
            interface=kwargs.get('os_endpoint_type') or 'publicURL',
            region_name=kwargs.get('os_region_name'))
        if 'os_ironic_api_version' in kwargs:
            self.assertEqual(0, mock_retrieve_data.call_count)
        else:
            mock_retrieve_data.assert_called_once_with(
                host='localhost',
                port='6385')
            self.assertEqual(version or v1.DEFAULT_VER,
                             client.http_client.os_ironic_api_version)

    def test_get_client_no_auth_token(self):
        kwargs = {
            'os_project_name': 'PROJECT_NAME',
            'os_username': 'USERNAME',
            'os_password': 'PASSWORD',
            'os_auth_url': 'http://localhost:35357/v2.0',
            'os_auth_token': '',
        }
        self._test_get_client(**kwargs)

    def test_get_client_service_and_endpoint_type_defaults(self):
        kwargs = {
            'os_project_name': 'PROJECT_NAME',
            'os_username': 'USERNAME',
            'os_password': 'PASSWORD',
            'os_auth_url': 'http://localhost:35357/v2.0',
            'os_auth_token': '',
            'os_service_type': '',
            'os_endpoint_type': ''
        }
        self._test_get_client(**kwargs)

    def test_get_client_with_region_no_auth_token(self):
        kwargs = {
            'os_project_name': 'PROJECT_NAME',
            'os_username': 'USERNAME',
            'os_password': 'PASSWORD',
            'os_region_name': 'REGIONONE',
            'os_auth_url': 'http://localhost:35357/v2.0',
            'os_auth_token': '',
        }
        self._test_get_client(**kwargs)

    def test_get_client_no_url(self):
        kwargs = {
            'os_project_name': 'PROJECT_NAME',
            'os_username': 'USERNAME',
            'os_password': 'PASSWORD',
            'os_auth_url': '',
        }
        self.assertRaises(exc.AmbiguousAuthSystem, iroclient.get_client,
                          '1', **kwargs)
        # test the alias as well to ensure backwards compatibility
        self.assertRaises(exc.AmbigiousAuthSystem, iroclient.get_client,
                          '1', **kwargs)

    def test_get_client_incorrect_auth_params(self):
        kwargs = {
            'os_project_name': 'PROJECT_NAME',
            'os_username': 'USERNAME',
            'os_auth_url': 'http://localhost:35357/v2.0',
        }
        self.assertRaises(exc.AmbiguousAuthSystem, iroclient.get_client,
                          '1', **kwargs)

    def test_get_client_with_api_version_latest(self):
        kwargs = {
            'os_project_name': 'PROJECT_NAME',
            'os_username': 'USERNAME',
            'os_password': 'PASSWORD',
            'os_auth_url': 'http://localhost:35357/v2.0',
            'os_auth_token': '',
            'os_ironic_api_version': "latest",
        }
        self._test_get_client(**kwargs)

    def test_get_client_with_api_version_numeric(self):
        kwargs = {
            'os_project_name': 'PROJECT_NAME',
            'os_username': 'USERNAME',
            'os_password': 'PASSWORD',
            'os_auth_url': 'http://localhost:35357/v2.0',
            'os_auth_token': '',
            'os_ironic_api_version': "1.4",
        }
        self._test_get_client(**kwargs)

    def test_get_client_default_version_set_cached(self):
        version = '1.3'
        # Make sure we don't coincidentally succeed
        self.assertNotEqual(v1.DEFAULT_VER, version)
        kwargs = {
            'os_project_name': 'PROJECT_NAME',
            'os_username': 'USERNAME',
            'os_password': 'PASSWORD',
            'os_auth_url': 'http://localhost:35357/v2.0',
            'os_auth_token': '',
        }
        self._test_get_client(version=version, **kwargs)

    def test_get_client_with_auth_token(self):
        kwargs = {
            'os_auth_url': 'http://localhost:35357/v2.0',
            'os_auth_token': 'USER_AUTH_TOKEN',
        }
        self._test_get_client(auth='token', **kwargs)

    def test_get_client_with_region_name_auth_token(self):
        kwargs = {
            'os_auth_url': 'http://localhost:35357/v2.0',
            'os_region_name': 'REGIONONE',
            'os_auth_token': 'USER_AUTH_TOKEN',
        }
        self._test_get_client(auth='token', **kwargs)

    def test_get_client_only_session_passed(self):
        session = mock.Mock()
        session.get_endpoint.return_value = 'http://localhost:35357/v2.0'
        kwargs = {
            'session': session,
        }
        iroclient.get_client('1', **kwargs)
        session.get_endpoint.assert_called_once_with(service_type='baremetal',
                                                     interface='publicURL',
                                                     region_name=None)

    def test_get_client_incorrect_session_passed(self):
        session = mock.Mock()
        session.get_endpoint.side_effect = Exception('boo')
        kwargs = {
            'session': session,
        }
        self.assertRaises(exc.AmbiguousAuthSystem, iroclient.get_client,
                          '1', **kwargs)

    @mock.patch.object(kaloading.session, 'Session', autospec=True)
    @mock.patch.object(kaloading, 'get_plugin_loader', autospec=True)
    def _test_loader_arguments_passed_correctly(
            self, mock_ks_loader, mock_ks_session,
            passed_kwargs, expected_kwargs):
        session = mock_ks_session.return_value.load_from_options.return_value
        session.get_endpoint.return_value = 'http://localhost:6385/v1/f14b4123'
        mock_ks_loader.return_value.load_from_options.return_value = 'auth'

        iroclient.get_client('1', **passed_kwargs)

        mock_ks_loader.return_value.load_from_options.assert_called_once_with(
            **expected_kwargs)
        mock_ks_session.return_value.load_from_options.assert_called_once_with(
            auth='auth', timeout=passed_kwargs.get('timeout'),
            insecure=passed_kwargs.get('insecure'),
            cert=passed_kwargs.get('cert'),
            cacert=passed_kwargs.get('cacert'), key=passed_kwargs.get('key'))
        session.get_endpoint.assert_called_once_with(
            service_type=passed_kwargs.get('os_service_type') or 'baremetal',
            interface=passed_kwargs.get('os_endpoint_type') or 'publicURL',
            region_name=passed_kwargs.get('os_region_name'))

    def test_loader_arguments_token(self):
        passed_kwargs = {
            'os_auth_url': 'http://localhost:35357/v3',
            'os_region_name': 'REGIONONE',
            'os_auth_token': 'USER_AUTH_TOKEN',
        }
        expected_kwargs = {
            'auth_url': 'http://localhost:35357/v3',
            'project_id': None,
            'project_name': None,
            'user_domain_id': None,
            'user_domain_name': None,
            'project_domain_id': None,
            'project_domain_name': None,
            'token': 'USER_AUTH_TOKEN'
        }
        self._test_loader_arguments_passed_correctly(
            passed_kwargs=passed_kwargs, expected_kwargs=expected_kwargs)

    def test_loader_arguments_password_tenant_name(self):
        passed_kwargs = {
            'os_auth_url': 'http://localhost:35357/v3',
            'os_region_name': 'REGIONONE',
            'os_project_name': 'PROJECT',
            'os_username': 'user',
            'os_password': '1234',
            'os_project_domain_id': 'DEFAULT',
            'os_user_domain_id': 'DEFAULT'
        }
        expected_kwargs = {
            'auth_url': 'http://localhost:35357/v3',
            'project_id': None,
            'project_name': 'PROJECT',
            'user_domain_id': 'DEFAULT',
            'user_domain_name': None,
            'project_domain_id': 'DEFAULT',
            'project_domain_name': None,
            'username': 'user',
            'password': '1234'
        }
        self._test_loader_arguments_passed_correctly(
            passed_kwargs=passed_kwargs, expected_kwargs=expected_kwargs)

    def test_loader_arguments_password_project_id(self):
        passed_kwargs = {
            'os_auth_url': 'http://localhost:35357/v3',
            'os_region_name': 'REGIONONE',
            'os_project_id': '1000',
            'os_username': 'user',
            'os_password': '1234',
            'os_project_domain_name': 'domain1',
            'os_user_domain_name': 'domain1'
        }
        expected_kwargs = {
            'auth_url': 'http://localhost:35357/v3',
            'project_id': '1000',
            'project_name': None,
            'user_domain_id': None,
            'user_domain_name': 'domain1',
            'project_domain_id': None,
            'project_domain_name': 'domain1',
            'username': 'user',
            'password': '1234'
        }
        self._test_loader_arguments_passed_correctly(
            passed_kwargs=passed_kwargs, expected_kwargs=expected_kwargs)

    @mock.patch.object(iroclient, 'Client', autospec=True)
    @mock.patch.object(kaloading.session, 'Session', autospec=True)
    def test_correct_arguments_passed_to_client_constructor_noauth_mode(
            self, mock_ks_session, mock_client):
        kwargs = {
            'ironic_url': 'http://ironic.example.org:6385/',
            'os_auth_token': 'USER_AUTH_TOKEN',
            'os_ironic_api_version': 'latest',
            'insecure': True,
            'max_retries': 10,
            'retry_interval': 10,
            'os_cacert': 'data'
        }
        iroclient.get_client('1', **kwargs)
        mock_client.assert_called_once_with(
            '1', 'http://ironic.example.org:6385/',
            **{
                'os_ironic_api_version': 'latest',
                'max_retries': 10,
                'retry_interval': 10,
                'token': 'USER_AUTH_TOKEN',
                'insecure': True,
                'ca_file': 'data',
                'cert_file': None,
                'key_file': None,
                'timeout': None,
                'session': None
            }
        )
        self.assertFalse(mock_ks_session.called)

    @mock.patch.object(iroclient, 'Client', autospec=True)
    @mock.patch.object(kaloading.session, 'Session', autospec=True)
    def test_correct_arguments_passed_to_client_constructor_session_created(
            self, mock_ks_session, mock_client):
        session = mock_ks_session.return_value.load_from_options.return_value
        kwargs = {
            'os_auth_url': 'http://localhost:35357/v3',
            'os_region_name': 'REGIONONE',
            'os_project_id': '1000',
            'os_username': 'user',
            'os_password': '1234',
            'os_project_domain_name': 'domain1',
            'os_user_domain_name': 'domain1'
        }
        iroclient.get_client('1', **kwargs)
        mock_client.assert_called_once_with(
            '1', session.get_endpoint.return_value,
            **{
                'os_ironic_api_version': None,
                'max_retries': None,
                'retry_interval': None,
                'session': session,
            }
        )

    @mock.patch.object(iroclient, 'Client', autospec=True)
    @mock.patch.object(kaloading.session, 'Session', autospec=True)
    def test_correct_arguments_passed_to_client_constructor_session_passed(
            self, mock_ks_session, mock_client):
        session = mock.Mock()
        kwargs = {
            'session': session,
        }
        iroclient.get_client('1', **kwargs)
        mock_client.assert_called_once_with(
            '1', session.get_endpoint.return_value,
            **{
                'os_ironic_api_version': None,
                'max_retries': None,
                'retry_interval': None,
                'session': session,
            }
        )
        self.assertFalse(mock_ks_session.called)

    def test_safe_header_with_auth_token(self):
        (name, value) = ('X-Auth-Token', u'3b640e2e64d946ac8f55615aff221dc1')
        expected_header = (u'X-Auth-Token',
                           '{SHA1}6de9fb3b0b89099030a54abfeb468e7b1b1f0f2b')
        client = http.HTTPClient('http://localhost/')
        header_redact = client._process_header(name, value)
        self.assertEqual(expected_header, header_redact)

    def test_safe_header_with_no_auth_token(self):
        name, value = ('Accept', 'application/json')
        header = ('Accept', 'application/json')
        client = http.HTTPClient('http://localhost/')
        header_redact = client._process_header(name, value)
        self.assertEqual(header, header_redact)
