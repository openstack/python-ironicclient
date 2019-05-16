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

from keystoneauth1 import identity
from keystoneauth1 import loading as kaloading
from keystoneauth1 import token_endpoint

from ironicclient import client as iroclient
from ironicclient.common import filecache
from ironicclient.common import http
from ironicclient import exc
from ironicclient.tests.unit import utils
from ironicclient.v1 import client as v1


class ClientTest(utils.BaseTestCase):

    @mock.patch.object(iroclient.LOG, 'warning', autospec=True)
    @mock.patch.object(filecache, 'retrieve_data', autospec=True)
    @mock.patch.object(kaloading.session, 'Session', autospec=True)
    @mock.patch.object(kaloading, 'get_plugin_loader', autospec=True)
    def _test_get_client(self, mock_ks_loader, mock_ks_session,
                         mock_retrieve_data, warn_mock, version=None,
                         auth='password', warn_mock_call_count=0,
                         expected_interface=None, **kwargs):
        session = mock_ks_session.return_value.load_from_options.return_value
        session.get_endpoint.return_value = 'http://localhost:6385/v1/f14b4123'

        class Opt(object):
            def __init__(self, name):
                self.dest = name

        session_loader_options = [
            Opt('insecure'), Opt('cafile'), Opt('certfile'), Opt('keyfile'),
            Opt('timeout')]
        mock_ks_session.return_value.get_conf_options.return_value = (
            session_loader_options)
        mock_ks_loader.return_value.load_from_options.return_value = 'auth'
        mock_retrieve_data.return_value = version

        client = iroclient.get_client('1', **kwargs)
        self.assertEqual(warn_mock_call_count, warn_mock.call_count)
        iroclient.convert_keystoneauth_opts(kwargs)

        mock_ks_loader.assert_called_once_with(auth)
        session_opts = {k: v for (k, v) in kwargs.items() if k in
                        [o.dest for o in session_loader_options]}
        mock_ks_session.return_value.load_from_options.assert_called_once_with(
            auth='auth', **session_opts)
        if not {'endpoint', 'ironic_url'}.intersection(kwargs):
            session.get_endpoint.assert_called_once_with(
                service_type=kwargs.get('service_type') or 'baremetal',
                interface=expected_interface,
                region_name=kwargs.get('region_name'))
        if 'os_ironic_api_version' in kwargs:
            # NOTE(TheJulia): This does not test the negotiation logic
            # as a request must be triggered in order for any version
            # negotiation actions to occur.
            self.assertEqual(0, mock_retrieve_data.call_count)
            self.assertEqual(kwargs['os_ironic_api_version'],
                             client.current_api_version)
            self.assertFalse(client.is_api_version_negotiated)
        else:
            mock_retrieve_data.assert_called_once_with(
                host='localhost',
                port='6385')
            self.assertEqual(version or v1.DEFAULT_VER,
                             client.http_client.os_ironic_api_version)

        # make sure the interface is conveyed to the client
        if expected_interface is not None:
            self.assertEqual(expected_interface,
                             client.http_client.interface)
        if kwargs.get('os_endpoint_type'):
            self.assertEqual(kwargs['os_endpoint_type'],
                             client.http_client.interface)

        return client

    def test_get_client_only_ironic_url(self):
        kwargs = {'ironic_url': 'http://localhost:6385/v1'}
        client = self._test_get_client(auth='none',
                                       warn_mock_call_count=1, **kwargs)
        self.assertIsInstance(client.http_client, http.SessionClient)
        self.assertEqual('http://localhost:6385',
                         client.http_client.endpoint_override)

    def test_get_client_only_endpoint(self):
        kwargs = {'endpoint': 'http://localhost:6385/v1'}
        client = self._test_get_client(auth='none', **kwargs)
        self.assertIsInstance(client.http_client, http.SessionClient)
        self.assertEqual('http://localhost:6385',
                         client.http_client.endpoint_override)

    def test_get_client_with_auth_token_ironic_url(self):
        kwargs = {
            'ironic_url': 'http://localhost:6385/v1',
            'os_auth_token': 'USER_AUTH_TOKEN',
        }

        client = self._test_get_client(auth='admin_token',
                                       warn_mock_call_count=2, **kwargs)

        self.assertIsInstance(client.http_client, http.SessionClient)
        self.assertEqual('http://localhost:6385',
                         client.http_client.endpoint_override)

    def test_get_client_no_auth_token(self):
        kwargs = {
            'os_project_name': 'PROJECT_NAME',
            'os_username': 'USERNAME',
            'os_password': 'PASSWORD',
            'os_auth_url': 'http://localhost:35357/v2.0',
            'os_auth_token': '',
        }
        self._test_get_client(warn_mock_call_count=4, **kwargs)

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
        self._test_get_client(warn_mock_call_count=4, **kwargs)

    def test_get_client_and_endpoint_type(self):
        kwargs = {
            'os_project_name': 'PROJECT_NAME',
            'os_username': 'USERNAME',
            'os_password': 'PASSWORD',
            'os_auth_url': 'http://localhost:35357/v2.0',
            'os_auth_token': '',
            'os_service_type': '',
            'os_endpoint_type': 'adminURL'
        }
        self._test_get_client(warn_mock_call_count=5,
                              expected_interface='adminURL', **kwargs)

    def test_get_client_and_interface(self):
        kwargs = {
            'os_project_name': 'PROJECT_NAME',
            'os_username': 'USERNAME',
            'os_password': 'PASSWORD',
            'os_auth_url': 'http://localhost:35357/v2.0',
            'os_auth_token': '',
            'os_service_type': '',
            'interface': 'internal'
        }
        self._test_get_client(warn_mock_call_count=4,
                              expected_interface='internal', **kwargs)

    def test_get_client_and_valid_interfaces(self):
        kwargs = {
            'os_project_name': 'PROJECT_NAME',
            'os_username': 'USERNAME',
            'os_password': 'PASSWORD',
            'os_auth_url': 'http://localhost:35357/v2.0',
            'os_auth_token': '',
            'os_service_type': '',
            'valid_interfaces': ['internal', 'public']
        }
        self._test_get_client(warn_mock_call_count=4,
                              expected_interface=['internal', 'public'],
                              **kwargs)

    def test_get_client_and_interface_and_valid_interfaces(self):
        """Ensure 'valid_interfaces' takes precedence over 'interface'."""
        kwargs = {
            'os_project_name': 'PROJECT_NAME',
            'os_username': 'USERNAME',
            'os_password': 'PASSWORD',
            'os_auth_url': 'http://localhost:35357/v2.0',
            'os_auth_token': '',
            'os_service_type': '',
            'interface': ['ignored'],
            'valid_interfaces': ['internal', 'public']
        }
        self._test_get_client(warn_mock_call_count=4,
                              expected_interface=['internal', 'public'],
                              **kwargs)

    def test_get_client_with_region_no_auth_token(self):
        kwargs = {
            'os_project_name': 'PROJECT_NAME',
            'os_username': 'USERNAME',
            'os_password': 'PASSWORD',
            'os_region_name': 'REGIONONE',
            'os_auth_url': 'http://localhost:35357/v2.0',
            'os_auth_token': '',
        }
        self._test_get_client(warn_mock_call_count=5, **kwargs)

    def test_get_client_incorrect_auth_params(self):
        kwargs = {
            'os_project_name': 'PROJECT_NAME',
            'os_username': 'USERNAME',
            'os_auth_url': 'http://localhost:35357/v2.0',
        }
        self.assertRaises(exc.AmbiguousAuthSystem, iroclient.get_client,
                          '1', warn_mock_call_count=3, **kwargs)

    def test_get_client_with_api_version_latest(self):
        kwargs = {
            'project_name': 'PROJECT_NAME',
            'username': 'USERNAME',
            'password': 'PASSWORD',
            'auth_url': 'http://localhost:35357/v2.0',
            'os_ironic_api_version': "latest",
        }
        self._test_get_client(**kwargs)

    def test_get_client_with_api_version_list(self):
        kwargs = {
            'project_name': 'PROJECT_NAME',
            'username': 'USERNAME',
            'password': 'PASSWORD',
            'auth_url': 'http://localhost:35357/v2.0',
            'auth_token': '',
            'os_ironic_api_version': ['1.1', '1.99'],
        }
        self._test_get_client(**kwargs)

    def test_get_client_with_api_version_numeric(self):
        kwargs = {
            'project_name': 'PROJECT_NAME',
            'username': 'USERNAME',
            'password': 'PASSWORD',
            'auth_url': 'http://localhost:35357/v2.0',
            'os_ironic_api_version': "1.4",
        }
        self._test_get_client(**kwargs)

    def test_get_client_default_version_set_cached(self):
        version = '1.3'
        # Make sure we don't coincidentally succeed
        self.assertNotEqual(v1.DEFAULT_VER, version)
        kwargs = {
            'project_name': 'PROJECT_NAME',
            'username': 'USERNAME',
            'password': 'PASSWORD',
            'auth_url': 'http://localhost:35357/v2.0',
        }
        self._test_get_client(version=version, **kwargs)

    def test_get_client_with_auth_token(self):
        kwargs = {
            'auth_url': 'http://localhost:35357/v2.0',
            'token': 'USER_AUTH_TOKEN',
        }
        self._test_get_client(auth='token', **kwargs)

    def test_get_client_with_region_name_auth_token(self):
        kwargs = {
            'auth_url': 'http://localhost:35357/v2.0',
            'region_name': 'REGIONONE',
            'token': 'USER_AUTH_TOKEN',
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
                                                     interface=None,
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
    def _test_loader_arguments_passed_correctly(
            self, mock_ks_session, passed_kwargs, expected_kwargs,
            loader_class, expected_interface=None):
        session = mock_ks_session.return_value.load_from_options.return_value
        session.get_endpoint.return_value = 'http://localhost:6385/v1/f14b4123'

        with mock.patch.object(loader_class, '__init__',
                               autospec=True) as init_mock:
            init_mock.return_value = None
            iroclient.get_client('1', **passed_kwargs)
            iroclient.convert_keystoneauth_opts(passed_kwargs)

        init_mock.assert_called_once_with(mock.ANY, **expected_kwargs)
        session_opts = {k: v for (k, v) in passed_kwargs.items() if k in
                        ['insecure', 'cacert', 'cert', 'key', 'timeout']}
        mock_ks_session.return_value.load_from_options.assert_called_once_with(
            auth=mock.ANY, **session_opts)
        if 'ironic_url' not in passed_kwargs:
            service_type = passed_kwargs.get('service_type') or 'baremetal'
            session.get_endpoint.assert_called_once_with(
                service_type=service_type, interface=expected_interface,
                region_name=passed_kwargs.get('region_name'))

    def test_loader_arguments_admin_token(self):
        passed_kwargs = {
            'ironic_url': 'http://localhost:6385/v1',
            'os_auth_token': 'USER_AUTH_TOKEN',
        }
        expected_kwargs = {
            'endpoint': 'http://localhost:6385/v1',
            'token': 'USER_AUTH_TOKEN'
        }
        self._test_loader_arguments_passed_correctly(
            passed_kwargs=passed_kwargs, expected_kwargs=expected_kwargs,
            loader_class=token_endpoint.Token
        )

    def test_loader_arguments_token(self):
        passed_kwargs = {
            'os_auth_url': 'http://localhost:35357/v3',
            'os_region_name': 'REGIONONE',
            'os_auth_token': 'USER_AUTH_TOKEN',
            'os_project_name': 'admin'
        }
        expected_kwargs = {
            'auth_url': 'http://localhost:35357/v3',
            'project_name': 'admin',
            'token': 'USER_AUTH_TOKEN'
        }
        self._test_loader_arguments_passed_correctly(
            passed_kwargs=passed_kwargs, expected_kwargs=expected_kwargs,
            loader_class=identity.Token
        )

    def test_loader_arguments_interface(self):
        passed_kwargs = {
            'os_auth_url': 'http://localhost:35357/v3',
            'os_region_name': 'REGIONONE',
            'os_auth_token': 'USER_AUTH_TOKEN',
            'os_project_name': 'admin',
            'interface': 'internal'
        }
        expected_kwargs = {
            'auth_url': 'http://localhost:35357/v3',
            'project_name': 'admin',
            'token': 'USER_AUTH_TOKEN'
        }
        self._test_loader_arguments_passed_correctly(
            passed_kwargs=passed_kwargs, expected_kwargs=expected_kwargs,
            loader_class=identity.Token, expected_interface='internal'
        )

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
            'project_name': 'PROJECT',
            'user_domain_id': 'DEFAULT',
            'project_domain_id': 'DEFAULT',
            'username': 'user',
            'password': '1234'
        }
        self._test_loader_arguments_passed_correctly(
            passed_kwargs=passed_kwargs, expected_kwargs=expected_kwargs,
            loader_class=identity.Password
        )

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
            'user_domain_name': 'domain1',
            'project_domain_name': 'domain1',
            'username': 'user',
            'password': '1234'
        }
        self._test_loader_arguments_passed_correctly(
            passed_kwargs=passed_kwargs, expected_kwargs=expected_kwargs,
            loader_class=identity.Password
        )

    @mock.patch.object(iroclient, 'Client', autospec=True)
    @mock.patch.object(kaloading.session, 'Session', autospec=True)
    def test_correct_arguments_passed_to_client_constructor_noauth_mode(
            self, mock_ks_session, mock_client):
        session = mock_ks_session.return_value.load_from_options.return_value
        kwargs = {
            'ironic_url': 'http://ironic.example.org:6385/',
            'os_auth_token': 'USER_AUTH_TOKEN',
            'os_ironic_api_version': 'latest',
        }
        iroclient.get_client('1', **kwargs)
        mock_client.assert_called_once_with(
            '1', **{'os_ironic_api_version': 'latest',
                    'max_retries': None,
                    'retry_interval': None,
                    'session': session,
                    'endpoint_override': 'http://ironic.example.org:6385/',
                    'interface': None}
        )
        self.assertFalse(session.get_endpoint.called)

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
            '1', **{'os_ironic_api_version': None,
                    'max_retries': None,
                    'retry_interval': None,
                    'session': session,
                    'endpoint_override': session.get_endpoint.return_value,
                    'interface': None}
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
            '1', **{'os_ironic_api_version': None,
                    'max_retries': None,
                    'retry_interval': None,
                    'session': session,
                    'endpoint_override': session.get_endpoint.return_value,
                    'interface': None}
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
