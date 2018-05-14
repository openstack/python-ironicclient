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

from ironicclient.osc import plugin
from ironicclient.tests.unit.osc import fakes
from ironicclient.v1 import client


class MakeClientTest(testtools.TestCase):

    @mock.patch.object(plugin, 'OS_BAREMETAL_API_LATEST', new=False)
    @mock.patch.object(client, 'Client', autospec=True)
    def test_make_client_explicit_version(self, mock_client):
        instance = fakes.FakeClientManager()
        instance.get_endpoint_for_service_type = mock.Mock(
            return_value='endpoint')
        plugin.make_client(instance)
        mock_client.assert_called_once_with(
            os_ironic_api_version=fakes.API_VERSION,
            allow_api_version_downgrade=False,
            session=instance.session,
            region_name=instance._region_name,
            endpoint_override='endpoint')
        instance.get_endpoint_for_service_type.assert_called_once_with(
            'baremetal', region_name=instance._region_name,
            interface=instance.interface)

    @mock.patch.object(plugin, 'OS_BAREMETAL_API_LATEST', new=True)
    @mock.patch.object(client, 'Client', autospec=True)
    def test_make_client_latest(self, mock_client):
        instance = fakes.FakeClientManager()
        instance.get_endpoint_for_service_type = mock.Mock(
            return_value='endpoint')
        instance._api_version = {'baremetal': plugin.LATEST_VERSION}
        plugin.make_client(instance)
        mock_client.assert_called_once_with(
            # NOTE(dtantsur): "latest" is changed to an actual version before
            # make_client is called.
            os_ironic_api_version=plugin.LATEST_VERSION,
            allow_api_version_downgrade=True,
            session=instance.session,
            region_name=instance._region_name,
            endpoint_override='endpoint')
        instance.get_endpoint_for_service_type.assert_called_once_with(
            'baremetal', region_name=instance._region_name,
            interface=instance.interface)

    @mock.patch.object(plugin, 'OS_BAREMETAL_API_LATEST', new=False)
    @mock.patch.object(client, 'Client', autospec=True)
    def test_make_client_v1(self, mock_client):
        instance = fakes.FakeClientManager()
        instance.get_endpoint_for_service_type = mock.Mock(
            return_value='endpoint')
        instance._api_version = {'baremetal': '1'}
        plugin.make_client(instance)
        mock_client.assert_called_once_with(
            os_ironic_api_version=plugin.LATEST_VERSION,
            allow_api_version_downgrade=True,
            session=instance.session,
            region_name=instance._region_name,
            endpoint_override='endpoint')
        instance.get_endpoint_for_service_type.assert_called_once_with(
            'baremetal', region_name=instance._region_name,
            interface=instance.interface)


@mock.patch.object(plugin, 'OS_BAREMETAL_API_LATEST', new=True)
@mock.patch.object(argparse.ArgumentParser, 'add_argument', autospec=True)
class BuildOptionParserTest(testtools.TestCase):

    @mock.patch.object(plugin.utils, 'env', lambda x: None)
    def test_build_option_parser(self, mock_add_argument):
        parser = argparse.ArgumentParser()
        mock_add_argument.reset_mock()
        plugin.build_option_parser(parser)
        version_list = ['1'] + ['1.%d' % i for i in range(
            1, plugin.LAST_KNOWN_API_VERSION + 1)] + ['latest']
        mock_add_argument.assert_called_once_with(
            mock.ANY, '--os-baremetal-api-version',
            action=plugin.ReplaceLatestVersion, choices=version_list,
            default=plugin.LATEST_VERSION, help=mock.ANY,
            metavar='<baremetal-api-version>')
        self.assertTrue(plugin.OS_BAREMETAL_API_LATEST)

    @mock.patch.object(plugin.utils, 'env', lambda x: "latest")
    def test_build_option_parser_env_latest(self, mock_add_argument):
        parser = argparse.ArgumentParser()
        mock_add_argument.reset_mock()
        plugin.build_option_parser(parser)
        version_list = ['1'] + ['1.%d' % i for i in range(
            1, plugin.LAST_KNOWN_API_VERSION + 1)] + ['latest']
        mock_add_argument.assert_called_once_with(
            mock.ANY, '--os-baremetal-api-version',
            action=plugin.ReplaceLatestVersion, choices=version_list,
            default=plugin.LATEST_VERSION, help=mock.ANY,
            metavar='<baremetal-api-version>')
        self.assertTrue(plugin.OS_BAREMETAL_API_LATEST)

    @mock.patch.object(plugin.utils, 'env', lambda x: "1.1")
    def test_build_option_parser_env(self, mock_add_argument):
        parser = argparse.ArgumentParser()
        mock_add_argument.reset_mock()
        plugin.build_option_parser(parser)
        version_list = ['1'] + ['1.%d' % i for i in range(
            1, plugin.LAST_KNOWN_API_VERSION + 1)] + ['latest']
        mock_add_argument.assert_called_once_with(
            mock.ANY, '--os-baremetal-api-version',
            action=plugin.ReplaceLatestVersion, choices=version_list,
            default='1.1', help=mock.ANY,
            metavar='<baremetal-api-version>')
        self.assertFalse(plugin.OS_BAREMETAL_API_LATEST)


@mock.patch.object(plugin.utils, 'env', lambda x: None)
class ReplaceLatestVersionTest(testtools.TestCase):

    @mock.patch.object(plugin, 'OS_BAREMETAL_API_LATEST', new=False)
    def test___call___latest(self):
        parser = argparse.ArgumentParser()
        plugin.build_option_parser(parser)
        namespace = argparse.Namespace()
        parser.parse_known_args(['--os-baremetal-api-version', 'latest'],
                                namespace)
        self.assertEqual(plugin.LATEST_VERSION,
                         namespace.os_baremetal_api_version)
        self.assertTrue(plugin.OS_BAREMETAL_API_LATEST)

    @mock.patch.object(plugin, 'OS_BAREMETAL_API_LATEST', new=True)
    def test___call___specific_version(self):
        parser = argparse.ArgumentParser()
        plugin.build_option_parser(parser)
        namespace = argparse.Namespace()
        parser.parse_known_args(['--os-baremetal-api-version', '1.4'],
                                namespace)
        self.assertEqual('1.4', namespace.os_baremetal_api_version)
        self.assertFalse(plugin.OS_BAREMETAL_API_LATEST)

    @mock.patch.object(plugin, 'OS_BAREMETAL_API_LATEST', new=True)
    def test___call___default(self):
        parser = argparse.ArgumentParser()
        plugin.build_option_parser(parser)
        namespace = argparse.Namespace()
        parser.parse_known_args([], namespace)
        self.assertEqual(plugin.LATEST_VERSION,
                         namespace.os_baremetal_api_version)
        self.assertTrue(plugin.OS_BAREMETAL_API_LATEST)
