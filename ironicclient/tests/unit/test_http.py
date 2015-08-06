# Copyright 2012 OpenStack LLC.
# All Rights Reserved.
#
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

import json
import time

import mock
import six

from ironicclient.common import filecache
from ironicclient.common import http
from ironicclient import exc
from ironicclient.tests.unit import utils


HTTP_CLASS = six.moves.http_client.HTTPConnection
HTTPS_CLASS = http.VerifiedHTTPSConnection
DEFAULT_TIMEOUT = 600

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = '1234'


def _get_error_body(faultstring=None, debuginfo=None):
    error_body = {
        'faultstring': faultstring,
        'debuginfo': debuginfo
    }
    raw_error_body = json.dumps(error_body)
    body = {'error_message': raw_error_body}
    raw_body = json.dumps(body)
    return raw_body


def _session_client(**kwargs):
    return http.SessionClient(os_ironic_api_version='1.6',
                              api_version_select_state='default',
                              max_retries=5,
                              retry_interval=2,
                              auth=None,
                              interface=None,
                              service_type='publicURL',
                              region_name='',
                              endpoint='http://%s:%s' % (DEFAULT_HOST,
                                                         DEFAULT_PORT),
                              **kwargs)


class VersionNegotiationMixinTest(utils.BaseTestCase):

    def setUp(self):
        super(VersionNegotiationMixinTest, self).setUp()
        self.test_object = http.VersionNegotiationMixin()
        self.test_object.os_ironic_api_version = '1.6'
        self.test_object.api_version_select_state = 'default'
        self.test_object.endpoint = "http://localhost:1234"
        self.mock_mcu = mock.MagicMock()
        self.test_object._make_connection_url = self.mock_mcu
        self.response = utils.FakeResponse({}, status=406)
        self.test_object.get_server = mock.MagicMock(
            return_value=('localhost', '1234'))

    def test__generic_parse_version_headers_has_headers(self):
        response = {'X-OpenStack-Ironic-API-Minimum-Version': '1.1',
                    'X-OpenStack-Ironic-API-Maximum-Version': '1.6',
                    }
        expected = ('1.1', '1.6')
        result = self.test_object._generic_parse_version_headers(response.get)
        self.assertEqual(expected, result)

    def test__generic_parse_version_headers_missing_headers(self):
        response = {}
        expected = (None, None)
        result = self.test_object._generic_parse_version_headers(response.get)
        self.assertEqual(expected, result)

    @mock.patch.object(filecache, 'save_data', autospec=True)
    def test_negotiate_version_bad_state(self, mock_save_data):
        # Test if bad api_version_select_state value
        self.test_object.api_version_select_state = 'word of the day: augur'
        self.assertRaises(
            RuntimeError,
            self.test_object.negotiate_version,
            None, None)
        self.assertEqual(0, mock_save_data.call_count)

    @mock.patch.object(filecache, 'save_data', autospec=True)
    @mock.patch.object(http.VersionNegotiationMixin, '_parse_version_headers',
                       autospec=True)
    def test_negotiate_version_server_older(self, mock_pvh, mock_save_data):
        # Test newer client and older server
        latest_ver = '1.5'
        mock_pvh.return_value = ('1.1', latest_ver)
        mock_conn = mock.MagicMock()
        result = self.test_object.negotiate_version(mock_conn, self.response)
        self.assertEqual(latest_ver, result)
        self.assertEqual(1, mock_pvh.call_count)
        host, port = http.get_server(self.test_object.endpoint)
        mock_save_data.assert_called_once_with(host=host, port=port,
                                               data=latest_ver)

    @mock.patch.object(filecache, 'save_data', autospec=True)
    @mock.patch.object(http.VersionNegotiationMixin, '_parse_version_headers',
                       autospec=True)
    def test_negotiate_version_server_newer(self, mock_pvh, mock_save_data):
        # Test newer server and older client
        mock_pvh.return_value = ('1.1', '1.10')
        mock_conn = mock.MagicMock()
        result = self.test_object.negotiate_version(mock_conn, self.response)
        self.assertEqual('1.6', result)
        self.assertEqual(1, mock_pvh.call_count)
        mock_save_data.assert_called_once_with(host=DEFAULT_HOST,
                                               port=DEFAULT_PORT,
                                               data='1.6')

    @mock.patch.object(filecache, 'save_data', autospec=True)
    @mock.patch.object(http.VersionNegotiationMixin, '_make_simple_request',
                       autospec=True)
    @mock.patch.object(http.VersionNegotiationMixin, '_parse_version_headers',
                       autospec=True)
    def test_negotiate_version_server_no_version_on_error(
            self, mock_pvh, mock_msr, mock_save_data):
        # Test older Ironic version which errored with no version number and
        # have to retry with simple get
        mock_pvh.side_effect = iter([(None, None), ('1.1', '1.2')])
        mock_conn = mock.MagicMock()
        result = self.test_object.negotiate_version(mock_conn, self.response)
        self.assertEqual('1.2', result)
        self.assertTrue(mock_msr.called)
        self.assertEqual(2, mock_pvh.call_count)
        self.assertEqual(1, mock_save_data.call_count)

    @mock.patch.object(filecache, 'save_data', autospec=True)
    @mock.patch.object(http.VersionNegotiationMixin, '_parse_version_headers',
                       autospec=True)
    def test_negotiate_version_server_explicit_too_high(self, mock_pvh,
                                                        mock_save_data):
        # requested version is not supported because it is too large
        mock_pvh.return_value = ('1.1', '1.6')
        mock_conn = mock.MagicMock()
        self.test_object.api_version_select_state = 'user'
        self.test_object.os_ironic_api_version = '99.99'
        self.assertRaises(
            exc.UnsupportedVersion,
            self.test_object.negotiate_version,
            mock_conn, self.response)
        self.assertEqual(1, mock_pvh.call_count)
        self.assertEqual(0, mock_save_data.call_count)

    @mock.patch.object(filecache, 'save_data', autospec=True)
    @mock.patch.object(http.VersionNegotiationMixin, '_parse_version_headers',
                       autospec=True)
    def test_negotiate_version_server_explicit_not_supported(self, mock_pvh,
                                                             mock_save_data):
        # requested version is supported by the server but the server returned
        # 406 because the requested operation is not supported with the
        # requested version
        mock_pvh.return_value = ('1.1', '1.6')
        mock_conn = mock.MagicMock()
        self.test_object.api_version_select_state = 'negotiated'
        self.test_object.os_ironic_api_version = '1.5'
        self.assertRaises(
            exc.UnsupportedVersion,
            self.test_object.negotiate_version,
            mock_conn, self.response)
        self.assertEqual(1, mock_pvh.call_count)
        self.assertEqual(0, mock_save_data.call_count)

    def test_get_server(self):
        host = 'ironic-host'
        port = '6385'
        endpoint = 'http://%s:%s/ironic/v1/' % (host, port)
        self.assertEqual((host, port), http.get_server(endpoint))


class HttpClientTest(utils.BaseTestCase):

    def test_url_generation_trailing_slash_in_base(self):
        client = http.HTTPClient('http://localhost/')
        url = client._make_connection_url('/v1/resources')
        self.assertEqual('/v1/resources', url)

    def test_url_generation_without_trailing_slash_in_base(self):
        client = http.HTTPClient('http://localhost')
        url = client._make_connection_url('/v1/resources')
        self.assertEqual('/v1/resources', url)

    def test_url_generation_prefix_slash_in_path(self):
        client = http.HTTPClient('http://localhost/')
        url = client._make_connection_url('/v1/resources')
        self.assertEqual('/v1/resources', url)

    def test_url_generation_without_prefix_slash_in_path(self):
        client = http.HTTPClient('http://localhost')
        url = client._make_connection_url('v1/resources')
        self.assertEqual('/v1/resources', url)

    def test_server_exception_empty_body(self):
        error_body = _get_error_body()
        fake_resp = utils.FakeResponse({'content-type': 'application/json'},
                                       six.StringIO(error_body),
                                       version=1,
                                       status=500)
        client = http.HTTPClient('http://localhost/')
        client.get_connection = (
            lambda *a, **kw: utils.FakeConnection(fake_resp))

        error = self.assertRaises(exc.InternalServerError,
                                  client.json_request,
                                  'GET', '/v1/resources')
        self.assertEqual('Internal Server Error (HTTP 500)', str(error))

    def test_server_exception_msg_only(self):
        error_msg = 'test error msg'
        error_body = _get_error_body(error_msg)
        fake_resp = utils.FakeResponse({'content-type': 'application/json'},
                                       six.StringIO(error_body),
                                       version=1,
                                       status=500)
        client = http.HTTPClient('http://localhost/')
        client.get_connection = (
            lambda *a, **kw: utils.FakeConnection(fake_resp))

        error = self.assertRaises(exc.InternalServerError,
                                  client.json_request,
                                  'GET', '/v1/resources')
        self.assertEqual(error_msg + ' (HTTP 500)', str(error))

    def test_server_exception_msg_and_traceback(self):
        error_msg = 'another test error'
        error_trace = ("\"Traceback (most recent call last):\\n\\n  "
                       "File \\\"/usr/local/lib/python2.7/...")
        error_body = _get_error_body(error_msg, error_trace)
        fake_resp = utils.FakeResponse({'content-type': 'application/json'},
                                       six.StringIO(error_body),
                                       version=1,
                                       status=500)
        client = http.HTTPClient('http://localhost/')
        client.get_connection = (
            lambda *a, **kw: utils.FakeConnection(fake_resp))

        error = self.assertRaises(exc.InternalServerError,
                                  client.json_request,
                                  'GET', '/v1/resources')

        self.assertEqual(
            '%(error)s (HTTP 500)\n%(trace)s' % {'error': error_msg,
                                                 'trace': error_trace},
            "%(error)s\n%(details)s" % {'error': str(error),
                                        'details': str(error.details)})

    def test_get_connection_params(self):
        endpoint = 'http://ironic-host:6385'
        expected = (HTTP_CLASS,
                    ('ironic-host', 6385, ''),
                    {'timeout': DEFAULT_TIMEOUT})
        params = http.HTTPClient.get_connection_params(endpoint)
        self.assertEqual(expected, params)

    def test_get_connection_params_with_trailing_slash(self):
        endpoint = 'http://ironic-host:6385/'
        expected = (HTTP_CLASS,
                    ('ironic-host', 6385, ''),
                    {'timeout': DEFAULT_TIMEOUT})
        params = http.HTTPClient.get_connection_params(endpoint)
        self.assertEqual(expected, params)

    def test_get_connection_params_with_ssl(self):
        endpoint = 'https://ironic-host:6385'
        expected = (HTTPS_CLASS,
                    ('ironic-host', 6385, ''),
                    {
                        'timeout': DEFAULT_TIMEOUT,
                        'ca_file': None,
                        'cert_file': None,
                        'key_file': None,
                        'insecure': False,
                    })
        params = http.HTTPClient.get_connection_params(endpoint)
        self.assertEqual(expected, params)

    def test_get_connection_params_with_ssl_params(self):
        endpoint = 'https://ironic-host:6385'
        ssl_args = {
            'ca_file': '/path/to/ca_file',
            'cert_file': '/path/to/cert_file',
            'key_file': '/path/to/key_file',
            'insecure': True,
        }

        expected_kwargs = {'timeout': DEFAULT_TIMEOUT}
        expected_kwargs.update(ssl_args)
        expected = (HTTPS_CLASS,
                    ('ironic-host', 6385, ''),
                    expected_kwargs)
        params = http.HTTPClient.get_connection_params(endpoint, **ssl_args)
        self.assertEqual(expected, params)

    def test_get_connection_params_with_timeout(self):
        endpoint = 'http://ironic-host:6385'
        expected = (HTTP_CLASS,
                    ('ironic-host', 6385, ''),
                    {'timeout': 300.0})
        params = http.HTTPClient.get_connection_params(endpoint, timeout=300)
        self.assertEqual(expected, params)

    def test_get_connection_params_with_version(self):
        endpoint = 'http://ironic-host:6385/v1'
        expected = (HTTP_CLASS,
                    ('ironic-host', 6385, ''),
                    {'timeout': DEFAULT_TIMEOUT})
        params = http.HTTPClient.get_connection_params(endpoint)
        self.assertEqual(expected, params)

    def test_get_connection_params_with_version_trailing_slash(self):
        endpoint = 'http://ironic-host:6385/v1/'
        expected = (HTTP_CLASS,
                    ('ironic-host', 6385, ''),
                    {'timeout': DEFAULT_TIMEOUT})
        params = http.HTTPClient.get_connection_params(endpoint)
        self.assertEqual(expected, params)

    def test_get_connection_params_with_subpath(self):
        endpoint = 'http://ironic-host:6385/ironic'
        expected = (HTTP_CLASS,
                    ('ironic-host', 6385, '/ironic'),
                    {'timeout': DEFAULT_TIMEOUT})
        params = http.HTTPClient.get_connection_params(endpoint)
        self.assertEqual(expected, params)

    def test_get_connection_params_with_subpath_trailing_slash(self):
        endpoint = 'http://ironic-host:6385/ironic/'
        expected = (HTTP_CLASS,
                    ('ironic-host', 6385, '/ironic'),
                    {'timeout': DEFAULT_TIMEOUT})
        params = http.HTTPClient.get_connection_params(endpoint)
        self.assertEqual(expected, params)

    def test_get_connection_params_with_subpath_version(self):
        endpoint = 'http://ironic-host:6385/ironic/v1'
        expected = (HTTP_CLASS,
                    ('ironic-host', 6385, '/ironic'),
                    {'timeout': DEFAULT_TIMEOUT})
        params = http.HTTPClient.get_connection_params(endpoint)
        self.assertEqual(expected, params)

    def test_get_connection_params_with_subpath_version_trailing_slash(self):
        endpoint = 'http://ironic-host:6385/ironic/v1/'
        expected = (HTTP_CLASS,
                    ('ironic-host', 6385, '/ironic'),
                    {'timeout': DEFAULT_TIMEOUT})
        params = http.HTTPClient.get_connection_params(endpoint)
        self.assertEqual(expected, params)

    def test_401_unauthorized_exception(self):
        error_body = _get_error_body()
        fake_resp = utils.FakeResponse({'content-type': 'text/plain'},
                                       six.StringIO(error_body),
                                       version=1,
                                       status=401)
        client = http.HTTPClient('http://localhost/')
        client.get_connection = (
            lambda *a, **kw: utils.FakeConnection(fake_resp))

        self.assertRaises(exc.Unauthorized, client.json_request,
                          'GET', '/v1/resources')

    def test__parse_version_headers(self):
        # Test parsing of version headers from HTTPClient
        error_body = _get_error_body()
        fake_resp = utils.FakeResponse(
            {'X-OpenStack-Ironic-API-Minimum-Version': '1.1',
             'X-OpenStack-Ironic-API-Maximum-Version': '1.6',
             'content-type': 'text/plain',
             },
            six.StringIO(error_body),
            version=1,
            status=406)
        expected_result = ('1.1', '1.6')
        client = http.HTTPClient('http://localhost/')
        result = client._parse_version_headers(fake_resp)
        self.assertEqual(expected_result, result)

    @mock.patch.object(filecache, 'save_data', autospec=True)
    @mock.patch.object(http.HTTPClient, 'get_connection', autospec=True)
    def test__http_request_client_fallback_fail(self, mock_getcon,
                                                mock_save_data):
        # Test when fallback to a supported version fails
        host, port, latest_ver = 'localhost', '1234', '1.6'
        error_body = _get_error_body()
        fake_resp = utils.FakeResponse(
            {'X-OpenStack-Ironic-API-Minimum-Version': '1.1',
             'X-OpenStack-Ironic-API-Maximum-Version': latest_ver,
             'content-type': 'text/plain',
             },
            six.StringIO(error_body),
            version=1,
            status=406)
        client = http.HTTPClient('http://%s:%s/' % (host, port))
        mock_getcon.return_value = utils.FakeConnection(fake_resp)
        self.assertRaises(
            exc.UnsupportedVersion,
            client._http_request,
            '/v1/resources',
            'GET')
        mock_save_data.assert_called_once_with(host=host, data=latest_ver,
                                               port=port)

    @mock.patch.object(http.VersionNegotiationMixin, 'negotiate_version',
                       autospec=False)
    @mock.patch.object(http.HTTPClient, 'get_connection', autospec=True)
    def test__http_request_client_fallback_success(
            self, mock_getcon, mock_negotiate):
        # Test when fallback to a supported version succeeds
        mock_negotiate.return_value = '1.6'
        error_body = _get_error_body()
        bad_resp = utils.FakeResponse(
            {'X-OpenStack-Ironic-API-Minimum-Version': '1.1',
             'X-OpenStack-Ironic-API-Maximum-Version': '1.6',
             'content-type': 'text/plain',
             },
            six.StringIO(error_body),
            version=1,
            status=406)
        good_resp = utils.FakeResponse(
            {'X-OpenStack-Ironic-API-Minimum-Version': '1.1',
             'X-OpenStack-Ironic-API-Maximum-Version': '1.6',
             'content-type': 'text/plain',
             },
            six.StringIO("We got some text"),
            version=1,
            status=200)
        client = http.HTTPClient('http://localhost/')
        mock_getcon.side_effect = iter([utils.FakeConnection(bad_resp),
                                        utils.FakeConnection(good_resp)])
        response, body_iter = client._http_request('/v1/resources', 'GET')
        self.assertEqual(200, response.status)
        self.assertEqual(1, mock_negotiate.call_count)


class SessionClientTest(utils.BaseTestCase):

    def test_server_exception_msg_and_traceback(self):
        error_msg = 'another test error'
        error_trace = ("\"Traceback (most recent call last):\\n\\n  "
                       "File \\\"/usr/local/lib/python2.7/...")
        error_body = _get_error_body(error_msg, error_trace)

        fake_session = utils.FakeSession({'Content-Type': 'application/json'},
                                         error_body,
                                         500)

        client = _session_client(session=fake_session)

        error = self.assertRaises(exc.InternalServerError,
                                  client.json_request,
                                  'GET', '/v1/resources')

        self.assertEqual(
            '%(error)s (HTTP 500)\n%(trace)s' % {'error': error_msg,
                                                 'trace': error_trace},
            "%(error)s\n%(details)s" % {'error': str(error),
                                        'details': str(error.details)})

    def test_server_exception_empty_body(self):
        error_body = _get_error_body()

        fake_session = utils.FakeSession({'Content-Type': 'application/json'},
                                         error_body,
                                         500)

        client = _session_client(session=fake_session)

        error = self.assertRaises(exc.InternalServerError,
                                  client.json_request,
                                  'GET', '/v1/resources')

        self.assertEqual('Internal Server Error (HTTP 500)', str(error))

    def test__parse_version_headers(self):
        # Test parsing of version headers from SessionClient
        fake_session = utils.FakeSession(
            {'X-OpenStack-Ironic-API-Minimum-Version': '1.1',
             'X-OpenStack-Ironic-API-Maximum-Version': '1.6',
             'content-type': 'text/plain',
             },
            None,
            506)
        expected_result = ('1.1', '1.6')
        client = _session_client(session=fake_session)
        result = client._parse_version_headers(fake_session)
        self.assertEqual(expected_result, result)


@mock.patch.object(time, 'sleep', lambda *_: None)
class RetriesTestCase(utils.BaseTestCase):

    @mock.patch.object(http.HTTPClient, 'get_connection', autospec=True)
    def test_http_no_retry(self, mock_getcon):
        error_body = _get_error_body()
        bad_resp = utils.FakeResponse(
            {'content-type': 'text/plain'},
            six.StringIO(error_body),
            version=1,
            status=409)
        client = http.HTTPClient('http://localhost/', max_retries=0)
        mock_getcon.return_value = utils.FakeConnection(bad_resp)
        self.assertRaises(exc.Conflict, client._http_request,
                          '/v1/resources', 'GET')
        self.assertEqual(1, mock_getcon.call_count)

    @mock.patch.object(http.HTTPClient, 'get_connection', autospec=True)
    def test_http_retry(self, mock_getcon):
        error_body = _get_error_body()
        bad_resp = utils.FakeResponse(
            {'content-type': 'text/plain'},
            six.StringIO(error_body),
            version=1,
            status=409)
        good_resp = utils.FakeResponse(
            {'content-type': 'text/plain'},
            six.StringIO("meow"),
            version=1,
            status=200)
        client = http.HTTPClient('http://localhost/')
        mock_getcon.side_effect = iter((utils.FakeConnection(bad_resp),
                                        utils.FakeConnection(good_resp)))
        response, body_iter = client._http_request('/v1/resources', 'GET')
        self.assertEqual(200, response.status)
        self.assertEqual(2, mock_getcon.call_count)

    @mock.patch.object(http.HTTPClient, 'get_connection', autospec=True)
    def test_http_retry_503(self, mock_getcon):
        error_body = _get_error_body()
        bad_resp = utils.FakeResponse(
            {'content-type': 'text/plain'},
            six.StringIO(error_body),
            version=1,
            status=503)
        good_resp = utils.FakeResponse(
            {'content-type': 'text/plain'},
            six.StringIO("meow"),
            version=1,
            status=200)
        client = http.HTTPClient('http://localhost/')
        mock_getcon.side_effect = iter((utils.FakeConnection(bad_resp),
                                        utils.FakeConnection(good_resp)))
        response, body_iter = client._http_request('/v1/resources', 'GET')
        self.assertEqual(200, response.status)
        self.assertEqual(2, mock_getcon.call_count)

    @mock.patch.object(http.HTTPClient, 'get_connection', autospec=True)
    def test_http_retry_connection_refused(self, mock_getcon):
        good_resp = utils.FakeResponse(
            {'content-type': 'text/plain'},
            six.StringIO("meow"),
            version=1,
            status=200)
        client = http.HTTPClient('http://localhost/')
        mock_getcon.side_effect = iter((exc.ConnectionRefused(),
                                        utils.FakeConnection(good_resp)))
        response, body_iter = client._http_request('/v1/resources', 'GET')
        self.assertEqual(200, response.status)
        self.assertEqual(2, mock_getcon.call_count)

    @mock.patch.object(http.HTTPClient, 'get_connection', autospec=True)
    def test_http_failed_retry(self, mock_getcon):
        error_body = _get_error_body()
        bad_resp = utils.FakeResponse(
            {'content-type': 'text/plain'},
            six.StringIO(error_body),
            version=1,
            status=409)
        client = http.HTTPClient('http://localhost/')
        mock_getcon.return_value = utils.FakeConnection(bad_resp)
        self.assertRaises(exc.Conflict, client._http_request,
                          '/v1/resources', 'GET')
        self.assertEqual(http.DEFAULT_MAX_RETRIES + 1, mock_getcon.call_count)

    @mock.patch.object(http.HTTPClient, 'get_connection', autospec=True)
    def test_http_max_retries_none(self, mock_getcon):
        error_body = _get_error_body()
        bad_resp = utils.FakeResponse(
            {'content-type': 'text/plain'},
            six.StringIO(error_body),
            version=1,
            status=409)
        client = http.HTTPClient('http://localhost/', max_retries=None)
        mock_getcon.return_value = utils.FakeConnection(bad_resp)
        self.assertRaises(exc.Conflict, client._http_request,
                          '/v1/resources', 'GET')
        self.assertEqual(http.DEFAULT_MAX_RETRIES + 1, mock_getcon.call_count)

    @mock.patch.object(http.HTTPClient, 'get_connection', autospec=True)
    def test_http_change_max_retries(self, mock_getcon):
        error_body = _get_error_body()
        bad_resp = utils.FakeResponse(
            {'content-type': 'text/plain'},
            six.StringIO(error_body),
            version=1,
            status=409)
        client = http.HTTPClient('http://localhost/',
                                 max_retries=http.DEFAULT_MAX_RETRIES + 1)
        mock_getcon.return_value = utils.FakeConnection(bad_resp)
        self.assertRaises(exc.Conflict, client._http_request,
                          '/v1/resources', 'GET')
        self.assertEqual(http.DEFAULT_MAX_RETRIES + 2, mock_getcon.call_count)

    def test_session_retry(self):
        error_body = _get_error_body()

        fake_resp = utils.FakeSessionResponse(
            {'Content-Type': 'application/json'},
            error_body,
            409)
        ok_resp = utils.FakeSessionResponse(
            {'Content-Type': 'application/json'},
            b"OK",
            200)
        fake_session = mock.Mock(spec=utils.FakeSession)
        fake_session.request.side_effect = iter((fake_resp, ok_resp))

        client = _session_client(session=fake_session)
        client.json_request('GET', '/v1/resources')
        self.assertEqual(2, fake_session.request.call_count)

    def test_session_retry_503(self):
        error_body = _get_error_body()

        fake_resp = utils.FakeSessionResponse(
            {'Content-Type': 'application/json'},
            error_body,
            503)
        ok_resp = utils.FakeSessionResponse(
            {'Content-Type': 'application/json'},
            b"OK",
            200)
        fake_session = mock.Mock(spec=utils.FakeSession)
        fake_session.request.side_effect = iter((fake_resp, ok_resp))

        client = _session_client(session=fake_session)
        client.json_request('GET', '/v1/resources')
        self.assertEqual(2, fake_session.request.call_count)

    def test_session_retry_connection_refused(self):
        ok_resp = utils.FakeSessionResponse(
            {'Content-Type': 'application/json'},
            b"OK",
            200)
        fake_session = mock.Mock(spec=utils.FakeSession)
        fake_session.request.side_effect = iter((exc.ConnectionRefused(),
                                                 ok_resp))

        client = _session_client(session=fake_session)
        client.json_request('GET', '/v1/resources')
        self.assertEqual(2, fake_session.request.call_count)

    def test_session_retry_fail(self):
        error_body = _get_error_body()

        fake_resp = utils.FakeSessionResponse(
            {'Content-Type': 'application/json'},
            error_body,
            409)
        fake_session = mock.Mock(spec=utils.FakeSession)
        fake_session.request.return_value = fake_resp

        client = _session_client(session=fake_session)

        self.assertRaises(exc.Conflict, client.json_request,
                          'GET', '/v1/resources')
        self.assertEqual(http.DEFAULT_MAX_RETRIES + 1,
                         fake_session.request.call_count)

    def test_session_max_retries_none(self):
        error_body = _get_error_body()

        fake_resp = utils.FakeSessionResponse(
            {'Content-Type': 'application/json'},
            error_body,
            409)
        fake_session = mock.Mock(spec=utils.FakeSession)
        fake_session.request.return_value = fake_resp

        client = _session_client(session=fake_session)
        client.conflict_max_retries = None

        self.assertRaises(exc.Conflict, client.json_request,
                          'GET', '/v1/resources')
        self.assertEqual(http.DEFAULT_MAX_RETRIES + 1,
                         fake_session.request.call_count)

    def test_session_change_max_retries(self):
        error_body = _get_error_body()

        fake_resp = utils.FakeSessionResponse(
            {'Content-Type': 'application/json'},
            error_body,
            409)
        fake_session = mock.Mock(spec=utils.FakeSession)
        fake_session.request.return_value = fake_resp

        client = _session_client(session=fake_session)
        client.conflict_max_retries = http.DEFAULT_MAX_RETRIES + 1

        self.assertRaises(exc.Conflict, client.json_request,
                          'GET', '/v1/resources')
        self.assertEqual(http.DEFAULT_MAX_RETRIES + 2,
                         fake_session.request.call_count)
