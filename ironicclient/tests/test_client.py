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

from ironicclient.client import get_client
from ironicclient import exc
from ironicclient.tests import utils


def fake_get_ksclient(**kwargs):
    return utils.FakeKeystone('KSCLIENT_AUTH_TOKEN')


class ClientTest(utils.BaseTestCase):

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
        self.assertRaises(exc.AmbigiousAuthSystem, get_client, '1', **kwargs)
