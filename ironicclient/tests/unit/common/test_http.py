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
                              endpoint_override='http://%s:%s' % (
                                  DEFAULT_HOST, DEFAULT_PORT),
                              **kwargs)


class VersionNegotiationMixinTest(utils.BaseTestCase):

    def setUp(self):
        super(VersionNegotiationMixinTest, self).setUp()
        self.test_object = http.VersionNegotiationMixin()
        self.test_object.os_ironic_api_version = '1.6'
        self.test_object.api_version_select_state = 'default'
        self.test_object.endpoint_override = "http://localhost:1234"
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
        host, port = http.get_server(self.test_object.endpoint_override)
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

    @mock.patch.object(filecache, 'save_data', autospec=True)
    @mock.patch.object(http.VersionNegotiationMixin, '_parse_version_headers',
                       autospec=True)
    def test_negotiate_version_strict_version_comparison(self, mock_pvh,
                                                         mock_save_data):
        # Test version comparison with StrictVersion
        max_ver = '1.10'
        mock_pvh.return_value = ('1.2', max_ver)
        mock_conn = mock.MagicMock()
        self.test_object.os_ironic_api_version = '1.10'
        result = self.test_object.negotiate_version(mock_conn, self.response)
        self.assertEqual(max_ver, result)
        self.assertEqual(1, mock_pvh.call_count)
        host, port = http.get_server(self.test_object.endpoint_override)
        mock_save_data.assert_called_once_with(host=host, port=port,
                                               data=max_ver)

    @mock.patch.object(filecache, 'save_data', autospec=True)
    @mock.patch.object(http.VersionNegotiationMixin, '_make_simple_request',
                       autospec=True)
    @mock.patch.object(http.VersionNegotiationMixin, '_parse_version_headers',
                       autospec=True)
    def test_negotiate_version_server_user_latest(
            self, mock_pvh, mock_msr, mock_save_data):
        # have to retry with simple get
        mock_pvh.side_effect = iter([(None, None), ('1.1', '1.99')])
        mock_conn = mock.MagicMock()
        self.test_object.api_version_select_state = 'user'
        self.test_object.os_ironic_api_version = 'latest'
        result = self.test_object.negotiate_version(mock_conn, None)
        self.assertEqual(http.LATEST_VERSION, result)
        self.assertEqual('negotiated',
                         self.test_object.api_version_select_state)
        self.assertEqual(http.LATEST_VERSION,
                         self.test_object.os_ironic_api_version)

        self.assertTrue(mock_msr.called)
        self.assertEqual(2, mock_pvh.call_count)
        self.assertEqual(1, mock_save_data.call_count)

    @mock.patch.object(filecache, 'save_data', autospec=True)
    @mock.patch.object(http.VersionNegotiationMixin, '_make_simple_request',
                       autospec=True)
    @mock.patch.object(http.VersionNegotiationMixin, '_parse_version_headers',
                       autospec=True)
    def test_negotiate_version_server_user_list(
            self, mock_pvh, mock_msr, mock_save_data):
        # have to retry with simple get
        mock_pvh.side_effect = [(None, None), ('1.1', '1.26')]
        mock_conn = mock.MagicMock()
        self.test_object.api_version_select_state = 'user'
        self.test_object.os_ironic_api_version = ['1.1', '1.6', '1.25',
                                                  '1.26', '1.26.1', '1.27',
                                                  '1.30']
        result = self.test_object.negotiate_version(mock_conn, self.response)
        self.assertEqual('1.26', result)
        self.assertEqual('negotiated',
                         self.test_object.api_version_select_state)
        self.assertEqual('1.26',
                         self.test_object.os_ironic_api_version)

        self.assertTrue(mock_msr.called)
        self.assertEqual(2, mock_pvh.call_count)
        self.assertEqual(1, mock_save_data.call_count)

    @mock.patch.object(filecache, 'save_data', autospec=True)
    @mock.patch.object(http.VersionNegotiationMixin, '_make_simple_request',
                       autospec=True)
    @mock.patch.object(http.VersionNegotiationMixin, '_parse_version_headers',
                       autospec=True)
    def test_negotiate_version_server_user_list_fails_nomatch(
            self, mock_pvh, mock_msr, mock_save_data):
        # have to retry with simple get
        mock_pvh.side_effect = iter([(None, None), ('1.2', '1.26')])
        mock_conn = mock.MagicMock()
        self.test_object.api_version_select_state = 'user'
        self.test_object.os_ironic_api_version = ['1.39', '1.1']
        self.assertRaises(
            exc.UnsupportedVersion,
            self.test_object.negotiate_version,
            mock_conn, self.response)
        self.assertEqual('user',
                         self.test_object.api_version_select_state)
        self.assertEqual(['1.39', '1.1'],
                         self.test_object.os_ironic_api_version)
        self.assertEqual(2, mock_pvh.call_count)
        self.assertEqual(0, mock_save_data.call_count)

    @mock.patch.object(filecache, 'save_data', autospec=True)
    @mock.patch.object(http.VersionNegotiationMixin, '_make_simple_request',
                       autospec=True)
    @mock.patch.object(http.VersionNegotiationMixin, '_parse_version_headers',
                       autospec=True)
    def test_negotiate_version_server_user_list_single_value(
            self, mock_pvh, mock_msr, mock_save_data):
        # have to retry with simple get
        mock_pvh.side_effect = iter([(None, None), ('1.1', '1.26')])
        mock_conn = mock.MagicMock()
        self.test_object.api_version_select_state = 'user'
        # NOTE(TheJulia): Lets test this value explicitly because the
        # minor number is actually the same.
        self.test_object.os_ironic_api_version = ['1.01']
        result = self.test_object.negotiate_version(mock_conn, None)
        self.assertEqual('1.1', result)
        self.assertEqual('negotiated',
                         self.test_object.api_version_select_state)
        self.assertEqual('1.1',
                         self.test_object.os_ironic_api_version)
        self.assertTrue(mock_msr.called)
        self.assertEqual(2, mock_pvh.call_count)
        self.assertEqual(1, mock_save_data.call_count)

    @mock.patch.object(filecache, 'save_data', autospec=True)
    @mock.patch.object(http.VersionNegotiationMixin, '_make_simple_request',
                       autospec=True)
    @mock.patch.object(http.VersionNegotiationMixin, '_parse_version_headers',
                       autospec=True)
    def test_negotiate_version_server_user_list_fails_latest(
            self, mock_pvh, mock_msr, mock_save_data):
        # have to retry with simple get
        mock_pvh.side_effect = iter([(None, None), ('1.1', '1.2')])
        mock_conn = mock.MagicMock()
        self.test_object.api_version_select_state = 'user'
        self.test_object.os_ironic_api_version = ['1.01', 'latest']
        self.assertRaises(
            ValueError,
            self.test_object.negotiate_version,
            mock_conn, self.response)
        self.assertEqual('user',
                         self.test_object.api_version_select_state)
        self.assertEqual(['1.01', 'latest'],
                         self.test_object.os_ironic_api_version)
        self.assertEqual(2, mock_pvh.call_count)
        self.assertEqual(0, mock_save_data.call_count)

    @mock.patch.object(filecache, 'save_data', autospec=True)
    @mock.patch.object(http.VersionNegotiationMixin, '_make_simple_request',
                       autospec=True)
    @mock.patch.object(http.VersionNegotiationMixin, '_parse_version_headers',
                       autospec=True)
    def test_negotiate_version_explicit_version_request(
            self, mock_pvh, mock_msr, mock_save_data):
        mock_pvh.side_effect = iter([(None, None), ('1.1', '1.99')])
        mock_conn = mock.MagicMock()
        self.test_object.api_version_select_state = 'negotiated'
        self.test_object.os_ironic_api_version = '1.30'
        req_header = {'X-OpenStack-Ironic-API-Version': '1.29'}
        response = utils.FakeResponse(
            {}, status=http_client.NOT_ACCEPTABLE,
            request_headers=req_header)
        self.assertRaisesRegex(exc.UnsupportedVersion,
                               ".*is not supported by the server.*",
                               self.test_object.negotiate_version,
                               mock_conn, response)
        self.assertTrue(mock_msr.called)
        self.assertEqual(2, mock_pvh.call_count)
        self.assertFalse(mock_save_data.called)

    def test_get_server(self):
        host = 'ironic-host'
        port = '6385'
        endpoint_override = 'http://%s:%s/ironic/v1/' % (host, port)
        self.assertEqual((host, port), http.get_server(endpoint_override))


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

    def test_make_simple_request(self):
        session = utils.mockSession({})

        client = _session_client(session=session)
        res = client._make_simple_request(session, 'GET', 'url')

        session.request.assert_called_once_with(
            'url', 'GET', raise_exc=False,
            endpoint_filter={
                'interface': 'publicURL',
                'service_type': 'baremetal',
                'region_name': ''
            },
            endpoint_override='http://localhost:1234',
            user_agent=http.USER_AGENT)
        self.assertEqual(res, session.request.return_value)

    @mock.patch.object(http.SessionClient, 'get_endpoint', autospec=True)
    def test_endpoint_not_found(self, mock_get_endpoint):
        mock_get_endpoint.return_value = None

        self.assertRaises(exc.EndpointNotFound, _session_client,
                          session=utils.mockSession({}))


@mock.patch.object(time, 'sleep', lambda *_: None)
class RetriesTestCase(utils.BaseTestCase):

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
        fake_session = utils.mockSession({})
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
        fake_session = utils.mockSession({})
        fake_session.request.side_effect = iter((fake_resp, ok_resp))

        client = _session_client(session=fake_session)
        client.json_request('GET', '/v1/resources')
        self.assertEqual(2, fake_session.request.call_count)

    def test_session_retry_connection_refused(self):
        ok_resp = utils.mockSessionResponse(
            {'Content-Type': 'application/json'},
            b"OK",
            http_client.OK)
        fake_session = utils.mockSession({})
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
        fake_session = utils.mockSession({})
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
        fake_session = utils.mockSession({})
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
        fake_session = utils.mockSession({})
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
        fake_session = utils.mockSession({})
        fake_session.request.return_value = fake_resp

        client = _session_client(session=fake_session)
        client.conflict_max_retries = http.DEFAULT_MAX_RETRIES + 1

        self.assertRaises(exc.Conflict, client.json_request,
                          'GET', '/v1/resources')
        self.assertEqual(http.DEFAULT_MAX_RETRIES + 2,
                         fake_session.request.call_count)
