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

import re
import sys

import fixtures
from keystoneauth1 import exceptions as keystone_exc
from keystoneauth1 import fixture as ks_fixture
import mock
from oslo_utils import uuidutils
import requests_mock
import six
import testtools
from testtools import matchers

from ironicclient import client
from ironicclient.common.apiclient import exceptions
from ironicclient.common import http
from ironicclient import exc
from ironicclient import shell as ironic_shell
from ironicclient.tests.unit import utils

BASE_URL = 'http://no.where:5000'
V2_URL = BASE_URL + '/v2.0'
V3_URL = BASE_URL + '/v3'

FAKE_ENV = {'OS_USERNAME': 'username',
            'OS_PASSWORD': 'password',
            'OS_PROJECT_NAME': 'project_name',
            'OS_AUTH_URL': V2_URL}

FAKE_ENV_KEYSTONE_V2 = {
    'OS_USERNAME': 'username',
    'OS_PASSWORD': 'password',
    'OS_PROJECT_NAME': 'project_name',
    'OS_AUTH_URL': V2_URL
}

FAKE_ENV_KEYSTONE_V3 = {
    'OS_USERNAME': 'username',
    'OS_PASSWORD': 'password',
    'OS_PROJECT_NAME': 'project_name',
    'OS_AUTH_URL': V3_URL,
    'OS_USER_DOMAIN_ID': 'default',
    'OS_PROJECT_DOMAIN_ID': 'default',
}

FAKE_ENV_KEYSTONE_V2_TOKEN = {
    'OS_AUTH_TOKEN': 'admin_token',
    'OS_PROJECT_NAME': 'project_name',
    'OS_AUTH_URL': V2_URL
}


class ShellTest(utils.BaseTestCase):
    re_options = re.DOTALL | re.MULTILINE

    # Patch os.environ to avoid required auth info.
    def make_env(self, exclude=None, environ_dict=FAKE_ENV):
        env = dict((k, v) for k, v in environ_dict.items() if k != exclude)
        self.useFixture(fixtures.MonkeyPatch('os.environ', env))

    def setUp(self):
        super(ShellTest, self).setUp()

    def shell(self, argstr):
        with mock.patch.object(sys, 'stdout', six.StringIO()):
            with mock.patch.object(sys, 'stderr', six.StringIO()):
                try:
                    _shell = ironic_shell.IronicShell()
                    _shell.main(argstr.split())
                except SystemExit:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    self.assertEqual(0, exc_value.code)
                finally:
                    out = sys.stdout.getvalue()
                    err = sys.stderr.getvalue()
                return out, err

    def test_help_unknown_command(self):
        self.assertRaises(exc.CommandError, self.shell, 'help foofoo')

    def test_help(self):
        required = [
            '.*?^usage: ironic',
            '.*?^ +bash-completion',
            '.*?^See "ironic help COMMAND" '
            'for help on a specific command',
        ]
        for argstr in ['--help', 'help']:
            help_text = self.shell(argstr)[0]
            for r in required:
                self.assertThat(help_text,
                                matchers.MatchesRegex(r,
                                                      self.re_options))

    def test_help_on_subcommand(self):
        required = [
            ".*?^usage: ironic chassis-show",
            ".*?^Show detailed information about a chassis",
        ]
        argstrings = [
            'help chassis-show',
        ]
        for argstr in argstrings:
            help_text = self.shell(argstr)[0]
            for r in required:
                self.assertThat(help_text,
                                matchers.MatchesRegex(r, self.re_options))

    def test_required_args_on_node_create_help(self):
        required = [
            ".*?^usage: ironic node-create",
            ".*?^Register a new node with the Ironic service",
            ".*?^Required arguments:",
        ]
        argstrings = [
            'help node-create',
        ]
        for argstr in argstrings:
            help_text = self.shell(argstr)[0]
            for r in required:
                self.assertThat(help_text,
                                matchers.MatchesRegex(r, self.re_options))

    def test_required_args_on_port_create_help(self):
        required = [
            ".*?^usage: ironic port-create",
            ".*?^Create a new port",
            ".*?^Required arguments:",
        ]
        argstrings = [
            'help port-create',
        ]
        for argstr in argstrings:
            help_text = self.shell(argstr)[0]
            for r in required:
                self.assertThat(help_text,
                                matchers.MatchesRegex(r, self.re_options))

    def test_auth_param(self):
        self.make_env(exclude='OS_USERNAME')
        self.test_help()

    @mock.patch.object(client, 'get_client', autospec=True,
                       side_effect=keystone_exc.ConnectFailure)
    @mock.patch('sys.stdin', side_effect=mock.MagicMock, autospec=True)
    @mock.patch('getpass.getpass', return_value='password', autospec=True)
    def test_password_prompted(self, mock_getpass, mock_stdin, mock_client):
        self.make_env(exclude='OS_PASSWORD')
        # We will get a ConnectFailure because there is no keystone.
        self.assertRaises(keystone_exc.ConnectFailure,
                          self.shell, 'node-list')
        expected_kwargs = {
            'ironic_url': '', 'os_auth_url': FAKE_ENV['OS_AUTH_URL'],
            'os_tenant_id': '', 'os_tenant_name': '',
            'os_username': FAKE_ENV['OS_USERNAME'], 'os_user_domain_id': '',
            'os_user_domain_name': '', 'os_password': FAKE_ENV['OS_PASSWORD'],
            'os_auth_token': '', 'os_project_id': '',
            'os_project_name': FAKE_ENV['OS_PROJECT_NAME'],
            'os_project_domain_id': '',
            'os_project_domain_name': '', 'os_region_name': '',
            'os_service_type': '', 'os_endpoint_type': '', 'os_cacert': None,
            'os_cert': None, 'os_key': None,
            'max_retries': http.DEFAULT_MAX_RETRIES,
            'retry_interval': http.DEFAULT_RETRY_INTERVAL,
            'os_ironic_api_version': None, 'timeout': 600, 'insecure': False
        }
        mock_client.assert_called_once_with(1, **expected_kwargs)
        # Make sure we are actually prompted.
        mock_getpass.assert_called_with('OpenStack Password: ')

    @mock.patch.object(client, 'get_client', autospec=True,
                       side_effect=keystone_exc.ConnectFailure)
    @mock.patch('getpass.getpass', return_value='password', autospec=True)
    def test_token_auth(self, mock_getpass, mock_client):
        self.make_env(environ_dict=FAKE_ENV_KEYSTONE_V2_TOKEN)
        # We will get a ConnectFailure because there is no keystone.
        self.assertRaises(keystone_exc.ConnectFailure,
                          self.shell, 'node-list')
        expected_kwargs = {
            'ironic_url': '',
            'os_auth_url': FAKE_ENV_KEYSTONE_V2_TOKEN['OS_AUTH_URL'],
            'os_tenant_id': '',
            'os_tenant_name': '',
            'os_username': '', 'os_user_domain_id': '',
            'os_user_domain_name': '', 'os_password': '',
            'os_auth_token': FAKE_ENV_KEYSTONE_V2_TOKEN['OS_AUTH_TOKEN'],
            'os_project_id': '',
            'os_project_name': FAKE_ENV_KEYSTONE_V2_TOKEN['OS_PROJECT_NAME'],
            'os_project_domain_id': '', 'os_project_domain_name': '',
            'os_region_name': '', 'os_service_type': '',
            'os_endpoint_type': '', 'os_cacert': None, 'os_cert': None,
            'os_key': None, 'max_retries': http.DEFAULT_MAX_RETRIES,
            'retry_interval': http.DEFAULT_RETRY_INTERVAL,
            'os_ironic_api_version': None, 'timeout': 600, 'insecure': False
        }
        mock_client.assert_called_once_with(1, **expected_kwargs)
        self.assertFalse(mock_getpass.called)

    @mock.patch('sys.stdin', side_effect=mock.MagicMock, autospec=True)
    @mock.patch('getpass.getpass', side_effect=EOFError, autospec=True)
    def test_password_prompted_ctrlD(self, mock_getpass, mock_stdin):
        self.make_env(exclude='OS_PASSWORD')
        # We should get Command Error because we mock Ctl-D.
        self.assertRaises(exc.CommandError,
                          self.shell, 'node-list')
        # Make sure we are actually prompted.
        mock_getpass.assert_called_with('OpenStack Password: ')

    @mock.patch('sys.stdin', autospec=True)
    def test_no_password_no_tty(self, mock_stdin):
        # delete the isatty attribute so that we do not get
        # prompted when manually running the tests
        del mock_stdin.isatty
        required = ('You must provide a password'
                    ' via either --os-password, env[OS_PASSWORD],'
                    ' or prompted response',)
        self.make_env(exclude='OS_PASSWORD')
        try:
            self.shell('node-list')
        except exc.CommandError as message:
            self.assertEqual(required, message.args)
        else:
            self.fail('CommandError not raised')

    def test_bash_completion(self):
        stdout = self.shell('bash-completion')[0]
        # just check we have some output
        required = [
            '.*--driver_info',
            '.*--chassis_uuid',
            '.*help',
            '.*node-create',
            '.*chassis-create']
        for r in required:
            self.assertThat(stdout,
                            matchers.MatchesRegex(r, self.re_options))

    def test_ironic_api_version(self):
        err = self.shell('--ironic-api-version 1.2 help')[1]
        self.assertFalse(err)

        err = self.shell('--ironic-api-version latest help')[1]
        self.assertFalse(err)

        self.assertRaises(exc.CommandError,
                          self.shell, '--ironic-api-version 1.2.1 help')

    def test_invalid_ironic_api_version(self):
        self.assertRaises(exceptions.UnsupportedVersion,
                          self.shell, '--ironic-api-version 0.8 help')

    def test_warning_on_no_version(self):
        err = self.shell('help')[1]
        self.assertIn('You are using the default API version', err)


class TestCase(testtools.TestCase):

    def set_fake_env(self, fake_env):
        client_env = ('OS_USERNAME', 'OS_PASSWORD', 'OS_PROJECT_ID',
                      'OS_PROJECT_NAME', 'OS_AUTH_URL', 'OS_REGION_NAME',
                      'OS_AUTH_TOKEN', 'OS_NO_CLIENT_AUTH', 'OS_SERVICE_TYPE',
                      'OS_ENDPOINT_TYPE', 'OS_CACERT', 'OS_CERT', 'OS_KEY')

        for key in client_env:
            self.useFixture(
                fixtures.EnvironmentVariable(key, fake_env.get(key)))

    # required for testing with Python 2.6
    def assertRegexpMatches(self, text, expected_regexp, msg=None):
        """Fail the test unless the text matches the regular expression."""
        if isinstance(expected_regexp, six.string_types):
            expected_regexp = re.compile(expected_regexp)
        if not expected_regexp.search(text):
            msg = msg or "Regexp didn't match"
            msg = '%s: %r not found in %r' % (
                msg, expected_regexp.pattern, text)
            raise self.failureException(msg)

    def register_keystone_v2_token_fixture(self, request_mocker):
        v2_token = ks_fixture.V2Token()
        service = v2_token.add_service('baremetal')
        service.add_endpoint('http://ironic.example.com', region='RegionOne')
        request_mocker.post('%s/tokens' % V2_URL,
                            json=v2_token)

    def register_keystone_v3_token_fixture(self, request_mocker):
        v3_token = ks_fixture.V3Token()
        service = v3_token.add_service('baremetal')
        service.add_standard_endpoints(public='http://ironic.example.com')
        request_mocker.post(
            '%s/auth/tokens' % V3_URL,
            json=v3_token,
            headers={'X-Subject-Token': uuidutils.generate_uuid()})

    def register_keystone_auth_fixture(self, request_mocker):
        self.register_keystone_v2_token_fixture(request_mocker)
        self.register_keystone_v3_token_fixture(request_mocker)

        request_mocker.get(V2_URL, json=ks_fixture.V2Discovery(V2_URL))
        request_mocker.get(V3_URL, json=ks_fixture.V3Discovery(V3_URL))
        request_mocker.get(BASE_URL, json=ks_fixture.DiscoveryList(BASE_URL))


class ShellTestNoMox(TestCase):
    def setUp(self):
        super(ShellTestNoMox, self).setUp()
        self.set_fake_env(FAKE_ENV_KEYSTONE_V2)

    def shell(self, argstr):
        orig = sys.stdout
        try:
            sys.stdout = six.StringIO()
            _shell = ironic_shell.IronicShell()
            _shell.main(argstr.split())
            self.subcommands = _shell.subcommands.keys()
        except SystemExit:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.assertEqual(0, exc_value.code)
        finally:
            out = sys.stdout.getvalue()
            sys.stdout.close()
            sys.stdout = orig

        return out

    @requests_mock.mock()
    def test_node_list(self, request_mocker):
        self.register_keystone_auth_fixture(request_mocker)
        resp_dict = {"nodes": [
                     {"instance_uuid": "null",
                      "uuid": "351a82d6-9f04-4c36-b79a-a38b9e98ff71",
                      "links": [{"href": "http://ironic.example.com:6385/"
                                 "v1/nodes/foo",
                                 "rel": "self"},
                                {"href": "http://ironic.example.com:6385/"
                                 "nodes/foo",
                                 "rel": "bookmark"}],
                      "maintenance": "false",
                      "provision_state": "null",
                      "power_state": "power off"},
                     {"instance_uuid": "null",
                      "uuid": "66fbba13-29e8-4b8a-9e80-c655096a40d3",
                      "links": [{"href": "http://ironic.example.com:6385/"
                                 "v1/nodes/foo2",
                                 "rel": "self"},
                                {"href": "http://ironic.example.com:6385/"
                                 "nodes/foo2",
                                 "rel": "bookmark"}],
                      "maintenance": "false",
                      "provision_state": "null",
                      "power_state": "power off"}]}
        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        request_mocker.get('http://ironic.example.com/v1/nodes',
                           headers=headers,
                           json=resp_dict)

        event_list_text = self.shell('node-list')

        required = [
            '351a82d6-9f04-4c36-b79a-a38b9e98ff71',
            '66fbba13-29e8-4b8a-9e80-c655096a40d3',
        ]

        for r in required:
            self.assertRegexpMatches(event_list_text, r)


class ShellTestNoMoxV3(ShellTestNoMox):

    def _set_fake_env(self):
        self.set_fake_env(FAKE_ENV_KEYSTONE_V3)


class ShellParserTest(TestCase):
    def test_deprecated_defaults(self):
        cert_env = {}
        cert_env['OS_CACERT'] = '/fake/cacert.pem'
        cert_env['OS_CERT'] = '/fake/cert.pem'
        cert_env['OS_KEY'] = '/fake/key.pem'
        self.set_fake_env(cert_env)
        parser = ironic_shell.IronicShell().get_base_parser()
        options, _ = parser.parse_known_args([])
        self.assertEqual(cert_env['OS_CACERT'], options.os_cacert)
        self.assertEqual(cert_env['OS_CERT'], options.os_cert)
        self.assertEqual(cert_env['OS_KEY'], options.os_key)
