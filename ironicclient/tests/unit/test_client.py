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

from unittest import mock

from openstack import config

from ironicclient import client as iroclient
from ironicclient.common import filecache
from ironicclient.common import http
from ironicclient import exc
from ironicclient.tests.unit import utils
from ironicclient.v1 import client as v1


class ClientTest(utils.BaseTestCase):

    @mock.patch.object(filecache, 'retrieve_data', autospec=True)
    @mock.patch.object(config, 'get_cloud_region', autospec=True)
    def _test_get_client(self, mock_cloud_region, mock_retrieve_data,
                         version=None, auth='password',
                         expected_interface=None, additional_headers=None,
                         global_request_id=None, **kwargs):
        session = mock_cloud_region.return_value.get_session.return_value
        session.get_endpoint.return_value = 'http://localhost:6385/v1/f14b4123'
        mock_retrieve_data.return_value = version

        client = iroclient.get_client(
            '1', additional_headers=additional_headers,
            global_request_id=global_request_id, **kwargs)

        expected_version = kwargs.pop('os_ironic_api_version', None)
        kwargs.pop('interface', None)
        kwargs.pop('valid_interfaces', None)

        get_endpoint_call = mock.call(
            service_type=kwargs.pop('service_type', None) or 'baremetal',
            interface=expected_interface,
            region_name=kwargs.pop('region_name', None))
        mock_cloud_region.assert_called_once_with(load_yaml_config=False,
                                                  load_envvars=False,
                                                  auth_type=auth, **kwargs)
        if 'endpoint' not in kwargs:
            self.assertEqual([get_endpoint_call],
                             session.get_endpoint.call_args_list)
        else:
            # we use adapter.get_endpoint instead of session.get_endpoint
            self.assertFalse(session.get_endpoint.called)
        if expected_version is not None:
            # NOTE(TheJulia): This does not test the negotiation logic
            # as a request must be triggered in order for any version
            # negotiation actions to occur.
            self.assertEqual(0, mock_retrieve_data.call_count)
            self.assertEqual(expected_version, client.current_api_version)
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

        return client

    def test_get_client_only_endpoint(self):
        kwargs = {'endpoint': 'http://localhost:6385/v1'}
        client = self._test_get_client(auth='none', **kwargs)
        self.assertIsInstance(client.http_client, http.SessionClient)
        self.assertEqual('http://localhost:6385',
                         client.http_client.endpoint_override)

    def test_get_client_additional_headers_and_global_request(self):
        req_id = 'req-7b081d28-8272-45f4-9cf6-89649c1c7a1a'
        kwargs = {
            'endpoint': 'http://localhost:6385/v1',
            'additional_headers': {'foo': 'bar'},
            'global_request_id': req_id
        }
        client = self._test_get_client(auth='none', **kwargs)
        self.assertIsInstance(client.http_client, http.SessionClient)
        self.assertEqual('http://localhost:6385',
                         client.http_client.endpoint_override)
        self.assertEqual(req_id, client.http_client.global_request_id)
        self.assertEqual({'foo': 'bar'}, client.http_client.additional_headers)

    def test_get_client_with_auth_token_endpoint(self):
        kwargs = {
            'endpoint': 'http://localhost:6385/v1',
            'token': 'USER_AUTH_TOKEN',
        }

        client = self._test_get_client(auth='admin_token', **kwargs)

        self.assertIsInstance(client.http_client, http.SessionClient)
        self.assertEqual('http://localhost:6385',
                         client.http_client.endpoint_override)

    def test_get_client_no_auth_token(self):
        kwargs = {
            'project_name': 'PROJECT_NAME',
            'username': 'USERNAME',
            'password': 'PASSWORD',
            'auth_url': 'http://localhost:35357/v2.0',
        }
        self._test_get_client(**kwargs)

    def test_get_client_service_and_interface_defaults(self):
        kwargs = {
            'project_name': 'PROJECT_NAME',
            'username': 'USERNAME',
            'password': 'PASSWORD',
            'auth_url': 'http://localhost:35357/v2.0',
            'service_type': '',
        }
        self._test_get_client(**kwargs)

    def test_get_client_and_interface_adminurl(self):
        kwargs = {
            'project_name': 'PROJECT_NAME',
            'username': 'USERNAME',
            'password': 'PASSWORD',
            'auth_url': 'http://localhost:35357/v2.0',
            'service_type': '',
            'interface': 'adminURL'
        }
        self._test_get_client(expected_interface='adminURL', **kwargs)

    def test_get_client_and_interface_internal(self):
        kwargs = {
            'project_name': 'PROJECT_NAME',
            'username': 'USERNAME',
            'password': 'PASSWORD',
            'auth_url': 'http://localhost:35357/v2.0',
            'service_type': '',
            'interface': 'internal'
        }
        self._test_get_client(expected_interface='internal', **kwargs)

    def test_get_client_and_valid_interfaces(self):
        kwargs = {
            'project_name': 'PROJECT_NAME',
            'username': 'USERNAME',
            'password': 'PASSWORD',
            'auth_url': 'http://localhost:35357/v2.0',
            'service_type': '',
            'valid_interfaces': ['internal', 'public']
        }
        self._test_get_client(expected_interface=['internal', 'public'],
                              **kwargs)

    def test_get_client_and_interface_and_valid_interfaces(self):
        """Ensure 'valid_interfaces' takes precedence over 'interface'."""
        kwargs = {
            'project_name': 'PROJECT_NAME',
            'username': 'USERNAME',
            'password': 'PASSWORD',
            'auth_url': 'http://localhost:35357/v2.0',
            'service_type': '',
            'interface': ['ignored'],
            'valid_interfaces': ['internal', 'public']
        }
        self._test_get_client(expected_interface=['internal', 'public'],
                              **kwargs)

    def test_get_client_with_region_no_auth_token(self):
        kwargs = {
            'project_name': 'PROJECT_NAME',
            'username': 'USERNAME',
            'os_password': 'PASSWORD',
            'os_region_name': 'REGIONONE',
            'auth_url': 'http://localhost:35357/v2.0',
        }
        self._test_get_client(**kwargs)

    def test_get_client_incorrect_auth_params(self):
        kwargs = {
            'project_name': 'PROJECT_NAME',
            'username': 'USERNAME',
            'auth_url': 'http://localhost:35357/v2.0',
        }
        self.assertRaises(exc.AmbiguousAuthSystem, iroclient.get_client,
                          '1', **kwargs)

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

    def test_client_no_session(self):
        # get_client can create a session, all other calls require it
        self.assertRaisesRegex(TypeError,
                               "session is required",
                               iroclient.Client,
                               1, "http://example.com")

    def test_client_session_via_posargs(self):
        session = mock.Mock()
        session.get_endpoint.return_value = 'http://localhost:35357/v2.0'
        iroclient.Client('1', "http://example.com", session)

    def test_client_session_via_kwargs(self):
        session = mock.Mock()
        session.get_endpoint.return_value = 'http://localhost:35357/v2.0'
        iroclient.Client('1', session=session,
                         endpoint_override="http://example.com")
