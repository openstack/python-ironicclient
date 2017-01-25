#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import argparse

import mock
import testtools

from ironicclient.common import http
from ironicclient.osc import plugin
from ironicclient.tests.unit.osc import fakes
from ironicclient.v1 import client


class MakeClientTest(testtools.TestCase):

    @mock.patch.object(client, 'Client', autospec=True)
    def test_make_client(self, mock_client):
        instance = fakes.FakeClientManager()
        instance.get_endpoint_for_service_type = mock.Mock(
            return_value='endpoint')
        plugin.make_client(instance)
        mock_client.assert_called_once_with(os_ironic_api_version='1.6',
                                            session=instance.session,
                                            region_name=instance._region_name,
                                            endpoint='endpoint')
        instance.get_endpoint_for_service_type.assert_called_once_with(
            'baremetal', region_name=instance._region_name,
            interface=instance.interface)


class BuildOptionParserTest(testtools.TestCase):

    @mock.patch.object(argparse.ArgumentParser, 'add_argument')
    def test_build_option_parser(self, mock_add_argument):
        parser = argparse.ArgumentParser()
        mock_add_argument.reset_mock()
        plugin.build_option_parser(parser)
        version_list = ['1'] + ['1.%d' % i for i in range(
            1, plugin.LAST_KNOWN_API_VERSION + 1)] + ['latest']
        mock_add_argument.assert_called_once_with(
            '--os-baremetal-api-version', action=plugin.ReplaceLatestVersion,
            choices=version_list, default=http.DEFAULT_VER, help=mock.ANY,
            metavar='<baremetal-api-version>')


class ReplaceLatestVersionTest(testtools.TestCase):

    def test___call___latest(self):
        parser = argparse.ArgumentParser()
        plugin.build_option_parser(parser)
        namespace = argparse.Namespace()
        parser.parse_known_args(['--os-baremetal-api-version', 'latest'],
                                namespace)
        self.assertEqual('1.%d' % plugin.LAST_KNOWN_API_VERSION,
                         namespace.os_baremetal_api_version)

    def test___call___specific_version(self):
        parser = argparse.ArgumentParser()
        plugin.build_option_parser(parser)
        namespace = argparse.Namespace()
        parser.parse_known_args(['--os-baremetal-api-version', '1.4'],
                                namespace)
        self.assertEqual('1.4', namespace.os_baremetal_api_version)
