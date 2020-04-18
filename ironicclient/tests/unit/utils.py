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

import copy
import io
import os
from unittest import mock

import fixtures
from oslo_utils import strutils
import requests
import testtools


class BaseTestCase(testtools.TestCase):
    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.useFixture(fixtures.FakeLogger())

        # If enabled, stdout and/or stderr is captured and will appear in
        # test results if that test fails.
        if strutils.bool_from_string(os.environ.get('OS_STDOUT_CAPTURE')):
            stdout = self.useFixture(fixtures.StringStream('stdout')).stream
            self.useFixture(fixtures.MonkeyPatch('sys.stdout', stdout))
        if strutils.bool_from_string(os.environ.get('OS_STDERR_CAPTURE')):
            stderr = self.useFixture(fixtures.StringStream('stderr')).stream
            self.useFixture(fixtures.MonkeyPatch('sys.stderr', stderr))


class FakeAPI(object):
    def __init__(self, responses, path_prefix=None):
        self.responses = responses
        self.calls = []
        self.path_prefix = path_prefix or ''
        self.endpoint_trimmed = 'http://127.0.0.1:6385' + self.path_prefix

    def _request(self, method, url, headers=None, body=None, params=None):
        # url should always just be a path here, e.g. /v1/nodes
        url = self.path_prefix + url

        call = (method, url, headers or {}, body)
        if params:
            call += (params,)
        self.calls.append(call)
        return self.responses[url][method]

    def raw_request(self, *args, **kwargs):
        response = self._request(*args, **kwargs)
        body_iter = iter(io.StringIO(response[1]))
        return FakeResponse(response[0]), body_iter

    def json_request(self, *args, **kwargs):
        response = self._request(*args, **kwargs)
        return FakeResponse(response[0]), response[1]


class FakeConnection(object):
    def __init__(self, response=None, path_prefix=None):
        self._response = response
        self._last_request = None

    def request(self, method, conn_url, **kwargs):
        self._last_request = (method, conn_url, kwargs)

    def setresponse(self, response):
        self._response = response

    def getresponse(self):
        return self._response

    def __repr__(self):
        return ("FakeConnection(response=%s)" % (self._response))


class FakeResponse(object):
    def __init__(self, headers, body=None, version=None, status=None,
                 reason=None, request_headers={}):
        """Fake object to help testing.

        :param headers: dict representing HTTP response headers
        :param body: file-like object
        """
        self.headers = headers
        self.body = body
        self.raw = mock.Mock()
        self.raw.version = version
        self.status_code = status
        self.reason = reason
        self.request = mock.Mock()
        self.request.headers = request_headers

    def getheaders(self):
        return copy.deepcopy(self.headers).items()

    def getheader(self, key, default):
        return self.headers.get(key, default)

    def read(self, amt):
        return self.body.read(amt)

    def __repr__(self):
        return ("FakeResponse(%s, body=%s, version=%s, status=%s, reason=%s, "
                "request_headers=%s)" %
                (self.headers, self.body, self.raw.version, self.status_code,
                 self.reason, self.request.headers))


def mockSessionResponse(headers, content=None, status_code=None, version=None,
                        request_headers={}):
    raw = mock.Mock()
    raw.version = version
    request = mock.Mock()
    request.headers = request_headers
    response = mock.Mock(spec=requests.Response,
                         headers=headers,
                         content=content,
                         status_code=status_code,
                         raw=raw,
                         reason='',
                         encoding='UTF-8',
                         request=request)
    response.text = content

    return response


def mockSession(headers, content=None, status_code=None, version=None):
    session = mock.Mock(spec=requests.Session,
                        verify=False,
                        cert=('test_cert', 'test_key'))
    session.get_endpoint = mock.Mock(return_value='https://test')
    response = mockSessionResponse(headers, content, status_code, version)
    session.request = mock.Mock(return_value=response)

    return session
