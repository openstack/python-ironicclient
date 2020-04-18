# Copyright 2015 Red Hat, Inc.
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

from http import client as http_client
from unittest import mock


from ironicclient.common.apiclient import exceptions
from ironicclient import exc
from ironicclient.tests.unit import utils as test_utils


@mock.patch.object(exceptions, 'from_response', autospec=True)
class ExcTest(test_utils.BaseTestCase):

    def setUp(self):
        super(ExcTest, self).setUp()
        self.message = 'SpongeBob SquarePants'
        self.traceback = 'Foo Traceback'
        self.method = 'call_spongebob'
        self.url = 'http://foo.bar'
        self.expected_json = {'error': {'message': self.message,
                                        'details': self.traceback}}

    def test_from_response(self, mock_apiclient):
        fake_response = mock.Mock(status_code=http_client.BAD_REQUEST)
        exc.from_response(fake_response, message=self.message,
                          traceback=self.traceback, method=self.method,
                          url=self.url)
        self.assertEqual(http_client.BAD_REQUEST, fake_response.status_code)
        self.assertEqual(self.expected_json, fake_response.json())
        mock_apiclient.assert_called_once_with(
            fake_response, method=self.method, url=self.url)

    def test_from_response_status(self, mock_apiclient):
        fake_response = mock.Mock(status=http_client.BAD_REQUEST)
        fake_response.getheader.return_value = 'fake-header'
        delattr(fake_response, 'status_code')

        exc.from_response(fake_response, message=self.message,
                          traceback=self.traceback, method=self.method,
                          url=self.url)
        expected_header = {'Content-Type': 'fake-header'}
        self.assertEqual(expected_header, fake_response.headers)
        self.assertEqual(http_client.BAD_REQUEST, fake_response.status_code)
        self.assertEqual(self.expected_json, fake_response.json())
        mock_apiclient.assert_called_once_with(
            fake_response, method=self.method, url=self.url)
