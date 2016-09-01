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

import time

import mock
from oslo_serialization import jsonutils
import requests
import six
from six.moves import http_client

from keystoneauth1 import exceptions as kexc

from ironicclient.common import filecache
from ironicclient.common import http
from ironicclient import exc
from ironicclient.tests.unit import utils


DEFAULT_TIMEOUT = 600

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = '1234'


def _get_error_body(faultstring=None, debuginfo=None, description=None):
    if description:
        error_body = {'description': description}
    else:
        error_body = {
            'faultstring': faultstring,
            'debuginfo': debuginfo
        }
    raw_error_body = jsonutils.dump_as_bytes(error_body)
    body = {'error_message': raw_error_body}
    return jsonutils.dumps(body)


def _session_client(**kwargs):
    return http.SessionClient(os_ironic_api_version='1.6',
                              api_version_select_state='default',
                              max_retries=5,
                              retry_interval=2,
                              auth=None,
                              interface='publicURL',
                              service_type='baremetal',
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
        self.response = utils.FakeResponse(
            {}, status=http_client.NOT_ACCEPTABLE)
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
        self.assertEqual('http://localhost/v1/resources', url)

    def test_url_generation_without_trailing_slash_in_base(self):
        client = http.HTTPClient('http://localhost')
        url = client._make_connection_url('/v1/resources')
        self.assertEqual('http://localhost/v1/resources', url)

    def test_url_generation_without_prefix_slash_in_path(self):
        client = http.HTTPClient('http://localhost')
        url = client._make_connection_url('v1/resources')
        self.assertEqual('http://localhost/v1/resources', url)

    def test_server_https_request_with_application_octet_stream(self):
        client = http.HTTPClient('https://localhost/')
        client.session = utils.mockSession(
            {'Content-Type': 'application/octet-stream'},
            "Body",
            version=1,
            status_code=http_client.OK)

        response, body = client.json_request('GET', '/v1/resources')
        self.assertEqual(client.session.request.return_value, response)
        self.assertIsNone(body)

    def test_server_exception_empty_body(self):
        error_body = _get_error_body()
        client = http.HTTPClient('http://localhost/')
        client.session = utils.mockSession(
            {'Content-Type': 'application/json'},
            error_body,
            version=1,
            status_code=http_client.INTERNAL_SERVER_ERROR)

        self.assertRaises(exc.InternalServerError,
                          client.json_request,
                          'GET', '/v1/resources')

    def test_server_exception_msg_only(self):
        error_msg = 'test error msg'
        error_body = _get_error_body(error_msg)
        client = http.HTTPClient('http://localhost/')
        client.session = utils.mockSession(
            {'Content-Type': 'application/json'},
            error_body,
            version=1,
            status_code=http_client.INTERNAL_SERVER_ERROR)

        self.assertRaises(exc.InternalServerError,
                          client.json_request,
                          'GET', '/v1/resources')

    def test_server_exception_description_only(self):
        error_msg = 'test error msg'
        error_body = _get_error_body(description=error_msg)
        client = http.HTTPClient('http://localhost/')
        client.session = utils.mockSession(
            {'Content-Type': 'application/json'},
            error_body,
            version=1,
            status_code=http_client.BAD_REQUEST)

        self.assertRaisesRegex(exc.BadRequest, 'test error msg',
                               client.json_request,
                               'GET', '/v1/resources')

    def test_server_https_request_ok(self):
        client = http.HTTPClient('https://localhost/')
        client.session = utils.mockSession(
            {'Content-Type': 'application/json'},
            "Body",
            version=1,
            status_code=http_client.OK)

        client.json_request('GET', '/v1/resources')

    def test_server_https_empty_body(self):
        error_body = _get_error_body()

        client = http.HTTPClient('https://localhost/')
        client.session = utils.mockSession(
            {'Content-Type': 'application/json'},
            error_body,
            version=1,
            status_code=http_client.INTERNAL_SERVER_ERROR)

        self.assertRaises(exc.InternalServerError,
                          client.json_request,
                          'GET', '/v1/resources')

    def test_401_unauthorized_exception(self):
        error_body = _get_error_body()
        client = http.HTTPClient('http://localhost/')
        client.session = utils.mockSession(
            {'Content-Type': 'text/plain'},
            error_body,
            version=1,
            status_code=http_client.UNAUTHORIZED)

        self.assertRaises(exc.Unauthorized, client.json_request,
                          'GET', '/v1/resources')

    def test_http_request_not_valid_request(self):
        client = http.HTTPClient('http://localhost/')
        client.session.request = mock.Mock(
            side_effect=http.requests.exceptions.InvalidSchema)

        self.assertRaises(exc.ValidationError, client._http_request,
                          'http://localhost/', 'GET')

    def test__parse_version_headers(self):
        # Test parsing of version headers from HTTPClient
        error_body = _get_error_body()
        expected_result = ('1.1', '1.6')

        client = http.HTTPClient('http://localhost/')
        fake_resp = utils.mockSessionResponse(
            {'X-OpenStack-Ironic-API-Minimum-Version': '1.1',
             'X-OpenStack-Ironic-API-Maximum-Version': '1.6',
             'Content-Type': 'text/plain',
             },
            error_body,
            version=1,
            status_code=http_client.NOT_ACCEPTABLE)
        result = client._parse_version_headers(fake_resp)
        self.assertEqual(expected_result, result)

    @mock.patch.object(filecache, 'save_data', autospec=True)
    def test__http_request_client_fallback_fail(self, mock_save_data):
        # Test when fallback to a supported version fails
        host, port, latest_ver = 'localhost', '1234', '1.6'
        error_body = _get_error_body()

        client = http.HTTPClient('http://%s:%s/' % (host, port))
        client.session = utils.mockSession(
            {'X-OpenStack-Ironic-API-Minimum-Version': '1.1',
             'X-OpenStack-Ironic-API-Maximum-Version': latest_ver,
             'content-type': 'text/plain',
             },
            error_body,
            version=1,
            status_code=http_client.NOT_ACCEPTABLE)
        self.assertRaises(
            exc.UnsupportedVersion,
            client._http_request,
            '/v1/resources',
            'GET')
        mock_save_data.assert_called_once_with(host=host, data=latest_ver,
                                               port=port)

    @mock.patch.object(http.VersionNegotiationMixin, 'negotiate_version',
                       autospec=False)
    def test__http_request_client_fallback_success(self, mock_negotiate):
        # Test when fallback to a supported version succeeds
        mock_negotiate.return_value = '1.6'
        error_body = _get_error_body()
        bad_resp = utils.mockSessionResponse(
            {'X-OpenStack-Ironic-API-Minimum-Version': '1.1',
             'X-OpenStack-Ironic-API-Maximum-Version': '1.6',
             'content-type': 'text/plain',
             },
            error_body,
            version=1,
            status_code=http_client.NOT_ACCEPTABLE)
        good_resp = utils.mockSessionResponse(
            {'X-OpenStack-Ironic-API-Minimum-Version': '1.1',
             'X-OpenStack-Ironic-API-Maximum-Version': '1.6',
             'content-type': 'text/plain',
             },
            "We got some text",
            version=1,
            status_code=http_client.OK)
        client = http.HTTPClient('http://localhost/')

        with mock.patch.object(client, 'session',
                               autospec=True) as mock_session:

            mock_session.request.side_effect = iter([bad_resp, good_resp])
            response, body_iter = client._http_request('/v1/resources', 'GET')

        self.assertEqual(http_client.OK, response.status_code)
        self.assertEqual(1, mock_negotiate.call_count)

    @mock.patch.object(http.LOG, 'debug', autospec=True)
    def test_log_curl_request_mask_password(self, mock_log):
        client = http.HTTPClient('http://localhost/')
        kwargs = {'headers': {'foo-header': 'bar-header'},
                  'body': '{"password": "foo"}'}
        client.log_curl_request('foo', 'http://127.0.0.1', kwargs)
        expected_log = ("curl -i -X foo -H 'foo-header: bar-header' "
                        "-d '{\"password\": \"***\"}' http://127.0.0.1")
        mock_log.assert_called_once_with(expected_log)

    @mock.patch.object(http.LOG, 'debug', autospec=True)
    def test_log_http_response_mask_password(self, mock_log):
        client = http.HTTPClient('http://localhost/')
        fake_response = utils.FakeResponse({}, version=1, reason='foo',
                                           status=200)
        body = '{"password": "foo"}'
        client.log_http_response(fake_response, body=body)
        expected_log = ("\nHTTP/0.1 200 foo\n\n{\"password\": \"***\"}\n")
        mock_log.assert_called_once_with(expected_log)

    def test__https_init_ssl_args_insecure(self):
        client = http.HTTPClient('https://localhost/', insecure=True)

        self.assertEqual(False, client.session.verify)

    def test__https_init_ssl_args_secure(self):
        client = http.HTTPClient('https://localhost/', ca_file='test_ca',
                                 key_file='test_key', cert_file='test_cert')

        self.assertEqual('test_ca', client.session.verify)
        self.assertEqual(('test_cert', 'test_key'), client.session.cert)

    @mock.patch.object(http.LOG, 'debug', autospec=True)
    def test_log_curl_request_with_body_and_header(self, mock_log):
        client = http.HTTPClient('http://test')
        headers = {'header1': 'value1'}
        body = 'example body'

        client.log_curl_request('GET', '/v1/nodes',
                                {'headers': headers, 'body': body})

        self.assertTrue(mock_log.called)
        self.assertTrue(mock_log.call_args[0])
        self.assertEqual("curl -i -X GET -H 'header1: value1'"
                         " -d 'example body' http://test/v1/nodes",
                         mock_log.call_args[0][0])

    @mock.patch.object(http.LOG, 'debug', autospec=True)
    def test_log_curl_request_with_certs(self, mock_log):
        headers = {'header1': 'value1'}
        client = http.HTTPClient('https://test', key_file='key',
                                 cert_file='cert', cacert='cacert',
                                 token='fake-token')

        client.log_curl_request('GET', '/v1/test', {'headers': headers})

        self.assertTrue(mock_log.called)
        self.assertTrue(mock_log.call_args[0])

        self.assertEqual("curl -i -X GET -H 'header1: value1' "
                         "--cert cert --key key https://test/v1/test",
                         mock_log.call_args[0][0])

    @mock.patch.object(http.LOG, 'debug', autospec=True)
    def test_log_curl_request_with_insecure_param(self, mock_log):
        headers = {'header1': 'value1'}
        http_client_object = http.HTTPClient('https://test', insecure=True,
                                             token='fake-token')

        http_client_object.log_curl_request('GET', '/v1/test',
                                            {'headers': headers})

        self.assertTrue(mock_log.called)
        self.assertTrue(mock_log.call_args[0])
        self.assertEqual("curl -i -X GET -H 'header1: value1' -k "
                         "--cert None --key None https://test/v1/test",
                         mock_log.call_args[0][0])


class SessionClientTest(utils.BaseTestCase):

    def test_server_exception_empty_body(self):
        error_body = _get_error_body()

        fake_session = utils.mockSession({'Content-Type': 'application/json'},
                                         error_body,
                                         http_client.INTERNAL_SERVER_ERROR)

        client = _session_client(session=fake_session)

        self.assertRaises(exc.InternalServerError,
                          client.json_request,
                          'GET', '/v1/resources')

    def test_server_exception_description_only(self):
        error_msg = 'test error msg'
        error_body = _get_error_body(description=error_msg)
        fake_session = utils.mockSession(
            {'Content-Type': 'application/json'},
            error_body, status_code=http_client.BAD_REQUEST)
        client = _session_client(session=fake_session)

        self.assertRaisesRegex(exc.BadRequest, 'test error msg',
                               client.json_request,
                               'GET', '/v1/resources')

    def test__parse_version_headers(self):
        # Test parsing of version headers from SessionClient
        fake_session = utils.mockSession(
            {'X-OpenStack-Ironic-API-Minimum-Version': '1.1',
             'X-OpenStack-Ironic-API-Maximum-Version': '1.6',
             'content-type': 'text/plain',
             },
            None,
            http_client.HTTP_VERSION_NOT_SUPPORTED)
        expected_result = ('1.1', '1.6')
        client = _session_client(session=fake_session)
        result = client._parse_version_headers(fake_session.request())
        self.assertEqual(expected_result, result)

    def _test_endpoint_override(self, endpoint):
        fake_session = utils.mockSession({'content-type': 'application/json'},
                                         status_code=http_client.NO_CONTENT)
        request_mock = mock.Mock()
        fake_session.request = request_mock
        request_mock.return_value = utils.mockSessionResponse(
            headers={'content-type': 'application/json'},
            status_code=http_client.NO_CONTENT)
        client = _session_client(session=fake_session,
                                 endpoint_override=endpoint)
        client.json_request('DELETE', '/v1/nodes/aa/maintenance')
        expected_args_dict = {
            'headers': {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-OpenStack-Ironic-API-Version': '1.6'
            },
            'auth': None, 'user_agent': 'python-ironicclient',
            'endpoint_filter': {
                'interface': 'publicURL',
                'service_type': 'baremetal',
                'region_name': ''
            }
        }
        if isinstance(endpoint, six.string_types):
            trimmed = http._trim_endpoint_api_version(endpoint)
            expected_args_dict['endpoint_override'] = trimmed
        request_mock.assert_called_once_with(
            '/v1/nodes/aa/maintenance', 'DELETE', raise_exc=False,
            **expected_args_dict
        )

    def test_endpoint_override(self):
        self._test_endpoint_override('http://1.0.0.1:6385')

    def test_endpoint_override_with_version(self):
        self._test_endpoint_override('http://1.0.0.1:6385/v1')

    def test_endpoint_override_not_valid(self):
        self._test_endpoint_override(True)


@mock.patch.object(time, 'sleep', lambda *_: None)
class RetriesTestCase(utils.BaseTestCase):

    def test_http_no_retry(self):
        error_body = _get_error_body()
        bad_resp = utils.mockSessionResponse(
            {'Content-Type': 'text/plain'},
            error_body,
            version=1,
            status_code=http_client.CONFLICT)
        client = http.HTTPClient('http://localhost/', max_retries=0)

        with mock.patch.object(client.session, 'request', autospec=True,
                               return_value=bad_resp) as mock_request:

            self.assertRaises(exc.Conflict, client._http_request,
                              '/v1/resources', 'GET')
            self.assertEqual(1, mock_request.call_count)

    def test_http_retry(self):
        error_body = _get_error_body()
        bad_resp = utils.mockSessionResponse(
            {'Content-Type': 'text/plain'},
            error_body,
            version=1,
            status_code=http_client.CONFLICT)
        good_resp = utils.mockSessionResponse(
            {'Content-Type': 'text/plain'},
            "meow",
            version=1,
            status_code=http_client.OK)
        client = http.HTTPClient('http://localhost/')

        with mock.patch.object(client, 'session',
                               autospec=True) as mock_session:

            mock_session.request.side_effect = iter([bad_resp, good_resp])
            response, body_iter = client._http_request('/v1/resources', 'GET')

        self.assertEqual(http_client.OK, response.status_code)
        self.assertEqual(2, mock_session.request.call_count)

    def test_http_retry_503(self):
        error_body = _get_error_body()
        bad_resp = utils.mockSessionResponse(
            {'Content-Type': 'text/plain'},
            error_body,
            version=1,
            status_code=http_client.SERVICE_UNAVAILABLE)
        good_resp = utils.mockSessionResponse(
            {'Content-Type': 'text/plain'},
            "meow",
            version=1,
            status_code=http_client.OK)
        client = http.HTTPClient('http://localhost/')

        with mock.patch.object(client, 'session',
                               autospec=True) as mock_session:
            mock_session.request.side_effect = iter([bad_resp, good_resp])
            response, body_iter = client._http_request('/v1/resources', 'GET')

        self.assertEqual(http_client.OK, response.status_code)
        self.assertEqual(2, mock_session.request.call_count)

    def test_http_retry_connection_refused(self):
        good_resp = utils.mockSessionResponse(
            {'content-type': 'text/plain'},
            "meow",
            version=1,
            status_code=http_client.OK)
        client = http.HTTPClient('http://localhost/')

        with mock.patch.object(client, 'session',
                               autospec=True) as mock_session:
            mock_session.request.side_effect = iter([exc.ConnectionRefused(),
                                                     good_resp])
            response, body_iter = client._http_request('/v1/resources', 'GET')

        self.assertEqual(http_client.OK, response.status_code)
        self.assertEqual(2, mock_session.request.call_count)

    def test_http_failed_retry(self):
        error_body = _get_error_body()
        bad_resp = utils.mockSessionResponse(
            {'content-type': 'text/plain'},
            error_body,
            version=1,
            status_code=http_client.CONFLICT)
        client = http.HTTPClient('http://localhost/')

        with mock.patch.object(client, 'session',
                               autospec=True) as mock_session:
            mock_session.request.return_value = bad_resp
            self.assertRaises(exc.Conflict, client._http_request,
                              '/v1/resources', 'GET')
            self.assertEqual(http.DEFAULT_MAX_RETRIES + 1,
                             mock_session.request.call_count)

    def test_http_max_retries_none(self):
        error_body = _get_error_body()
        bad_resp = utils.mockSessionResponse(
            {'content-type': 'text/plain'},
            error_body,
            version=1,
            status_code=http_client.CONFLICT)
        client = http.HTTPClient('http://localhost/', max_retries=None)

        with mock.patch.object(client, 'session',
                               autospec=True) as mock_session:
            mock_session.request.return_value = bad_resp
            self.assertRaises(exc.Conflict, client._http_request,
                              '/v1/resources', 'GET')
            self.assertEqual(http.DEFAULT_MAX_RETRIES + 1,
                             mock_session.request.call_count)

    def test_http_change_max_retries(self):
        error_body = _get_error_body()
        bad_resp = utils.mockSessionResponse(
            {'content-type': 'text/plain'},
            error_body,
            version=1,
            status_code=http_client.CONFLICT)
        client = http.HTTPClient('http://localhost/',
                                 max_retries=http.DEFAULT_MAX_RETRIES + 1)

        with mock.patch.object(client, 'session',
                               autospec=True) as mock_session:
            mock_session.request.return_value = bad_resp
            self.assertRaises(exc.Conflict, client._http_request,
                              '/v1/resources', 'GET')
            self.assertEqual(http.DEFAULT_MAX_RETRIES + 2,
                             mock_session.request.call_count)

    def test_session_retry(self):
        error_body = _get_error_body()

        fake_resp = utils.mockSessionResponse(
            {'Content-Type': 'application/json'},
            error_body,
            http_client.CONFLICT)
        ok_resp = utils.mockSessionResponse(
            {'Content-Type': 'application/json'},
            b"OK",
            http_client.OK)
        fake_session = mock.Mock(spec=requests.Session)
        fake_session.request.side_effect = iter((fake_resp, ok_resp))

        client = _session_client(session=fake_session)
        client.json_request('GET', '/v1/resources')
        self.assertEqual(2, fake_session.request.call_count)

    def test_session_retry_503(self):
        error_body = _get_error_body()

        fake_resp = utils.mockSessionResponse(
            {'Content-Type': 'application/json'},
            error_body,
            http_client.SERVICE_UNAVAILABLE)
        ok_resp = utils.mockSessionResponse(
            {'Content-Type': 'application/json'},
            b"OK",
            http_client.OK)
        fake_session = mock.Mock(spec=requests.Session)
        fake_session.request.side_effect = iter((fake_resp, ok_resp))

        client = _session_client(session=fake_session)
        client.json_request('GET', '/v1/resources')
        self.assertEqual(2, fake_session.request.call_count)

    def test_session_retry_connection_refused(self):
        ok_resp = utils.mockSessionResponse(
            {'Content-Type': 'application/json'},
            b"OK",
            http_client.OK)
        fake_session = mock.Mock(spec=requests.Session)
        fake_session.request.side_effect = iter((exc.ConnectionRefused(),
                                                 ok_resp))

        client = _session_client(session=fake_session)
        client.json_request('GET', '/v1/resources')
        self.assertEqual(2, fake_session.request.call_count)

    def test_session_retry_retriable_connection_failure(self):
        ok_resp = utils.mockSessionResponse(
            {'Content-Type': 'application/json'},
            b"OK",
            http_client.OK)
        fake_session = mock.Mock(spec=requests.Session)
        fake_session.request.side_effect = iter(
            (kexc.RetriableConnectionFailure(), ok_resp))

        client = _session_client(session=fake_session)
        client.json_request('GET', '/v1/resources')
        self.assertEqual(2, fake_session.request.call_count)

    def test_session_retry_fail(self):
        error_body = _get_error_body()

        fake_resp = utils.mockSessionResponse(
            {'Content-Type': 'application/json'},
            error_body,
            http_client.CONFLICT)
        fake_session = mock.Mock(spec=requests.Session)
        fake_session.request.return_value = fake_resp

        client = _session_client(session=fake_session)

        self.assertRaises(exc.Conflict, client.json_request,
                          'GET', '/v1/resources')
        self.assertEqual(http.DEFAULT_MAX_RETRIES + 1,
                         fake_session.request.call_count)

    def test_session_max_retries_none(self):
        error_body = _get_error_body()

        fake_resp = utils.mockSessionResponse(
            {'Content-Type': 'application/json'},
            error_body,
            http_client.CONFLICT)
        fake_session = mock.Mock(spec=requests.Session)
        fake_session.request.return_value = fake_resp

        client = _session_client(session=fake_session)
        client.conflict_max_retries = None

        self.assertRaises(exc.Conflict, client.json_request,
                          'GET', '/v1/resources')
        self.assertEqual(http.DEFAULT_MAX_RETRIES + 1,
                         fake_session.request.call_count)

    def test_session_change_max_retries(self):
        error_body = _get_error_body()

        fake_resp = utils.mockSessionResponse(
            {'Content-Type': 'application/json'},
            error_body,
            http_client.CONFLICT)
        fake_session = mock.Mock(spec=requests.Session)
        fake_session.request.return_value = fake_resp

        client = _session_client(session=fake_session)
        client.conflict_max_retries = http.DEFAULT_MAX_RETRIES + 1

        self.assertRaises(exc.Conflict, client.json_request,
                          'GET', '/v1/resources')
        self.assertEqual(http.DEFAULT_MAX_RETRIES + 2,
                         fake_session.request.call_count)
