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

import builtins
from unittest import mock

import jsonschema

from ironicclient import exc
from ironicclient.tests.unit import utils
from ironicclient.v1 import create_resources

valid_json = {
    "chassis": [{
        "description": "testing resources import",
        "nodes": [{
            "driver": "agent_ssh",
            "extra": {
                "kv1": True,
                "vk1": None
            },
            "properties": {
                "a": "c"
            },
            "ports": [{
                "address": "00:00:00:00:00:01",
                "extra": {
                    "a": "b"
                }
            }],
            "portgroups": [{
                "address": "00:00:00:00:00:02",
                "name": "portgroup1",
                "ports": [{
                    "address": "00:00:00:00:00:03"
                }]
            }]
        }]
    }],
    "nodes": [{
        "driver": "fake",
        "driver_info": {
            "fake_key": "fake",
            "dict_prop": {
                "a": "b"
            },
            "arr_prop": [
                1, 2, 3
            ]
        },
        "chassis_uuid": "10f99593-b8c2-4fcb-8858-494c1a47cee6"
    }]
}

ironic_pov_invalid_json = {
    "nodes": [{
        "driver": "non_existent",
        "ports": [{
            "address": "invalid_address"
        }]
    }]
}

schema_pov_invalid_json = {"meow": "woof!"}


class CreateSchemaTest(utils.BaseTestCase):

    def test_schema(self):
        schema = create_resources._CREATE_SCHEMA
        jsonschema.validate(valid_json, schema)
        jsonschema.validate(ironic_pov_invalid_json, schema)
        self.assertRaises(jsonschema.ValidationError, jsonschema.validate,
                          schema_pov_invalid_json, schema)


class CreateResourcesTest(utils.BaseTestCase):

    def setUp(self):
        super(CreateResourcesTest, self).setUp()
        self.client = mock.MagicMock()

    @mock.patch.object(create_resources, 'create_nodes', autospec=True)
    @mock.patch.object(create_resources, 'create_chassis', autospec=True)
    @mock.patch.object(jsonschema, 'validate', autospec=True)
    @mock.patch.object(create_resources, 'load_from_file',
                       side_effect=[valid_json], autospec=True)
    def test_create_resources(
            self, mock_load, mock_validate, mock_chassis, mock_nodes):
        resources_files = ['file.json']
        create_resources.create_resources(self.client, resources_files)
        mock_load.assert_has_calls([
            mock.call('file.json')
        ])
        mock_validate.assert_called_once_with(valid_json, mock.ANY)
        mock_chassis.assert_called_once_with(self.client,
                                             valid_json['chassis'])
        mock_nodes.assert_called_once_with(self.client,
                                           valid_json['nodes'])

    @mock.patch.object(create_resources, 'create_nodes', autospec=True)
    @mock.patch.object(create_resources, 'create_chassis', autospec=True)
    @mock.patch.object(jsonschema, 'validate', autospec=True)
    @mock.patch.object(create_resources, 'load_from_file',
                       side_effect=exc.ClientException, autospec=True)
    def test_create_resources_cannot_read_schema(
            self, mock_load, mock_validate, mock_chassis, mock_nodes):
        resources_files = ['file.json']
        self.assertRaises(exc.ClientException,
                          create_resources.create_resources,
                          self.client, resources_files)
        mock_load.assert_called_once_with('file.json')
        self.assertFalse(mock_validate.called)
        self.assertFalse(mock_chassis.called)
        self.assertFalse(mock_nodes.called)

    @mock.patch.object(create_resources, 'create_nodes', autospec=True)
    @mock.patch.object(create_resources, 'create_chassis', autospec=True)
    @mock.patch.object(jsonschema, 'validate',
                       side_effect=jsonschema.ValidationError(''),
                       autospec=True)
    @mock.patch.object(create_resources, 'load_from_file',
                       side_effect=[schema_pov_invalid_json], autospec=True)
    def test_create_resources_validation_fails(
            self, mock_load, mock_validate, mock_chassis, mock_nodes):
        resources_files = ['file.json']
        self.assertRaises(exc.ClientException,
                          create_resources.create_resources,
                          self.client, resources_files)
        mock_load.assert_has_calls([
            mock.call('file.json')
        ])
        mock_validate.assert_called_once_with(schema_pov_invalid_json,
                                              mock.ANY)
        self.assertFalse(mock_chassis.called)
        self.assertFalse(mock_nodes.called)

    @mock.patch.object(create_resources, 'create_nodes', autospec=True)
    @mock.patch.object(create_resources, 'create_chassis', autospec=True)
    @mock.patch.object(jsonschema, 'validate',
                       side_effect=[None, jsonschema.ValidationError('')],
                       autospec=True)
    @mock.patch.object(create_resources, 'load_from_file',
                       side_effect=[valid_json, schema_pov_invalid_json],
                       autospec=True)
    def test_create_resources_validation_fails_multiple(
            self, mock_load, mock_validate, mock_chassis, mock_nodes):
        resources_files = ['file.json', 'file2.json']
        self.assertRaises(exc.ClientException,
                          create_resources.create_resources,
                          self.client, resources_files)
        mock_load.assert_has_calls([
            mock.call('file.json'), mock.call('file2.json')
        ])
        mock_validate.assert_has_calls([
            mock.call(valid_json, mock.ANY),
            mock.call(schema_pov_invalid_json, mock.ANY)
        ])
        self.assertFalse(mock_chassis.called)
        self.assertFalse(mock_nodes.called)

    @mock.patch.object(create_resources, 'create_nodes', autospec=True)
    @mock.patch.object(create_resources, 'create_chassis', autospec=True)
    @mock.patch.object(jsonschema, 'validate', autospec=True)
    @mock.patch.object(create_resources, 'load_from_file',
                       side_effect=[ironic_pov_invalid_json], autospec=True)
    def test_create_resources_ironic_fails_to_create(
            self, mock_load, mock_validate, mock_chassis, mock_nodes):
        mock_nodes.return_value = [exc.ClientException('cannot create that')]
        mock_chassis.return_value = []
        resources_files = ['file.json']
        self.assertRaises(exc.ClientException,
                          create_resources.create_resources,
                          self.client, resources_files)
        mock_load.assert_has_calls([
            mock.call('file.json')
        ])
        mock_validate.assert_called_once_with(ironic_pov_invalid_json,
                                              mock.ANY)
        mock_chassis.assert_called_once_with(self.client, [])
        mock_nodes.assert_called_once_with(
            self.client, ironic_pov_invalid_json['nodes'])


class LoadFromFileTest(utils.BaseTestCase):

    @mock.patch.object(builtins, 'open',
                       mock.mock_open(read_data='{"a": "b"}'))
    def test_load_json(self):
        fname = 'abc.json'
        res = create_resources.load_from_file(fname)
        self.assertEqual({'a': 'b'}, res)

    @mock.patch.object(builtins, 'open',
                       mock.mock_open(read_data='{"a": "b"}'))
    def test_load_unknown_extension(self):
        fname = 'abc'
        self.assertRaisesRegex(exc.ClientException,
                               'must have .json or .yaml extension',
                               create_resources.load_from_file, fname)

    @mock.patch.object(builtins, 'open', autospec=True)
    def test_load_ioerror(self, mock_open):
        mock_open.side_effect = IOError('file does not exist')
        fname = 'abc.json'
        self.assertRaisesRegex(exc.ClientException,
                               'Cannot read file',
                               create_resources.load_from_file, fname)

    @mock.patch.object(builtins, 'open',
                       mock.mock_open(read_data='{{bbb'))
    def test_load_incorrect_json(self):
        fname = 'abc.json'
        self.assertRaisesRegex(
            exc.ClientException, 'File "%s" is invalid' % fname,
            create_resources.load_from_file, fname)

    @mock.patch.object(builtins, 'open',
                       mock.mock_open(read_data='---\na: b'))
    def test_load_yaml(self):
        fname = 'abc.yaml'
        res = create_resources.load_from_file(fname)
        self.assertEqual({'a': 'b'}, res)

    @mock.patch.object(builtins, 'open',
                       mock.mock_open(read_data='---\na-: - b'))
    def test_load_incorrect_yaml(self):
        fname = 'abc.yaml'
        self.assertRaisesRegex(
            exc.ClientException, 'File "%s" is invalid' % fname,
            create_resources.load_from_file, fname)


class CreateMethodsTest(utils.BaseTestCase):

    def setUp(self):
        super(CreateMethodsTest, self).setUp()
        self.client = mock.MagicMock()

    def test_create_single_node(self):
        params = {'driver': 'fake'}
        self.client.node.create.return_value = mock.Mock(uuid='uuid')
        self.assertEqual(
            ('uuid', None),
            create_resources.create_single_node(self.client, **params)
        )
        self.client.node.create.assert_called_once_with(driver='fake')

    def test_create_single_node_with_traits(self):
        params = {'driver': 'fake', 'traits': ['CUSTOM_PERFORMANCE']}
        self.client.node.create.return_value = mock.Mock(uuid='uuid')
        self.assertEqual(
            ('uuid', None),
            create_resources.create_single_node(self.client, **params)
        )
        self.client.node.create.assert_called_once_with(driver='fake')
        self.client.node.set_traits.assert_called_once_with(
            mock.ANY, ['CUSTOM_PERFORMANCE'])

    def test_create_single_node_with_ports(self):
        params = {'driver': 'fake', 'ports': ['some ports here']}
        self.client.node.create.return_value = mock.Mock(uuid='uuid')
        self.assertEqual(
            ('uuid', None),
            create_resources.create_single_node(self.client, **params)
        )
        self.client.node.create.assert_called_once_with(driver='fake')

    def test_create_single_node_with_portgroups(self):
        params = {'driver': 'fake', 'portgroups': ['some portgroups']}
        self.client.node.create.return_value = mock.Mock(uuid='uuid')
        self.assertEqual(
            ('uuid', None),
            create_resources.create_single_node(self.client, **params)
        )
        self.client.node.create.assert_called_once_with(driver='fake')

    def test_create_single_node_raises_client_exception(self):
        params = {'driver': 'fake'}
        e = exc.ClientException('foo')
        self.client.node.create.side_effect = e
        res, err = create_resources.create_single_node(self.client, **params)
        self.assertIsNone(res)
        self.assertIsInstance(err, exc.ClientException)
        self.assertIn('Unable to create the node', str(err))
        self.client.node.create.assert_called_once_with(driver='fake')

    def test_create_single_node_raises_invalid_exception(self):
        params = {'driver': 'fake'}
        e = exc.InvalidAttribute('foo')
        self.client.node.create.side_effect = e
        res, err = create_resources.create_single_node(self.client, **params)
        self.assertIsNone(res)
        self.assertIsInstance(err, exc.InvalidAttribute)
        self.assertIn('Cannot create the node with attributes', str(err))
        self.client.node.create.assert_called_once_with(driver='fake')

    def test_create_single_port(self):
        params = {'address': 'fake-address', 'node_uuid': 'fake-node-uuid'}
        self.client.port.create.return_value = mock.Mock(uuid='fake-port-uuid')
        self.assertEqual(
            ('fake-port-uuid', None),
            create_resources.create_single_port(self.client, **params)
        )
        self.client.port.create.assert_called_once_with(**params)

    def test_create_single_portgroup(self):
        params = {'address': 'fake-address', 'node_uuid': 'fake-node-uuid'}
        self.client.portgroup.create.return_value = mock.Mock(
            uuid='fake-portgroup-uuid')
        self.assertEqual(
            ('fake-portgroup-uuid', None),
            create_resources.create_single_portgroup(self.client, **params)
        )
        self.client.portgroup.create.assert_called_once_with(**params)

    def test_create_single_portgroup_with_ports(self):
        params = {'ports': ['some ports'], 'node_uuid': 'fake-node-uuid'}
        self.client.portgroup.create.return_value = mock.Mock(
            uuid='fake-portgroup-uuid')
        self.assertEqual(
            ('fake-portgroup-uuid', None),
            create_resources.create_single_portgroup(
                self.client, **params)
        )
        self.client.portgroup.create.assert_called_once_with(
            node_uuid='fake-node-uuid')

    def test_create_single_chassis(self):
        self.client.chassis.create.return_value = mock.Mock(uuid='uuid')
        self.assertEqual(
            ('uuid', None),
            create_resources.create_single_chassis(self.client)
        )
        self.client.chassis.create.assert_called_once_with()

    def test_create_single_chassis_with_nodes(self):
        params = {'nodes': ['some nodes here']}
        self.client.chassis.create.return_value = mock.Mock(uuid='uuid')
        self.assertEqual(
            ('uuid', None),
            create_resources.create_single_chassis(self.client, **params)
        )
        self.client.chassis.create.assert_called_once_with()

    def test_create_ports(self):
        port = {'address': 'fake-address'}
        port_with_node_uuid = port.copy()
        port_with_node_uuid.update(node_uuid='fake-node-uuid')
        self.client.port.create.return_value = mock.Mock(uuid='uuid')
        self.assertEqual([], create_resources.create_ports(self.client, [port],
                                                           'fake-node-uuid'))
        self.client.port.create.assert_called_once_with(**port_with_node_uuid)

    def test_create_ports_two_node_uuids(self):
        port = {'address': 'fake-address', 'node_uuid': 'node-uuid-1'}
        errs = create_resources.create_ports(self.client, [port],
                                             'node-uuid-2')
        self.assertIsInstance(errs[0], exc.ClientException)
        self.assertEqual(1, len(errs))
        self.assertFalse(self.client.port.create.called)

    def test_create_ports_two_portgroup_uuids(self):
        port = {'address': 'fake-address', 'node_uuid': 'node-uuid-1',
                'portgroup_uuid': 'pg-uuid-1'}
        errs = create_resources.create_ports(self.client, [port],
                                             'node-uuid-1', 'pg-uuid-2')
        self.assertEqual(1, len(errs))
        self.assertIsInstance(errs[0], exc.ClientException)
        self.assertIn('port group', str(errs[0]))
        self.assertFalse(self.client.port.create.called)

    @mock.patch.object(create_resources, 'create_portgroups', autospec=True)
    @mock.patch.object(create_resources, 'create_ports', autospec=True)
    def test_create_nodes(self, mock_create_ports, mock_create_portgroups):
        node = {'driver': 'fake', 'ports': ['list of ports'],
                'portgroups': ['list of portgroups']}
        self.client.node.create.return_value = mock.Mock(uuid='uuid')
        self.assertEqual([], create_resources.create_nodes(self.client,
                                                           [node]))
        self.client.node.create.assert_called_once_with(driver='fake')
        mock_create_ports.assert_called_once_with(
            self.client, ['list of ports'], node_uuid='uuid')
        mock_create_portgroups.assert_called_once_with(
            self.client, ['list of portgroups'], node_uuid='uuid')

    @mock.patch.object(create_resources, 'create_portgroups', autospec=True)
    @mock.patch.object(create_resources, 'create_ports', autospec=True)
    def test_create_nodes_exception(self, mock_create_ports,
                                    mock_create_portgroups):
        node = {'driver': 'fake', 'ports': ['list of ports'],
                'portgroups': ['list of portgroups']}
        self.client.node.create.side_effect = exc.ClientException('bar')
        errs = create_resources.create_nodes(self.client, [node])
        self.assertIsInstance(errs[0], exc.ClientException)
        self.assertEqual(1, len(errs))
        self.client.node.create.assert_called_once_with(driver='fake')
        self.assertFalse(mock_create_ports.called)
        self.assertFalse(mock_create_portgroups.called)

    @mock.patch.object(create_resources, 'create_ports', autospec=True)
    def test_create_nodes_two_chassis_uuids(self, mock_create_ports):
        node = {'driver': 'fake', 'ports': ['list of ports'],
                'chassis_uuid': 'chassis-uuid-1'}
        errs = create_resources.create_nodes(self.client, [node],
                                             chassis_uuid='chassis-uuid-2')
        self.assertFalse(self.client.node.create.called)
        self.assertFalse(mock_create_ports.called)
        self.assertEqual(1, len(errs))
        self.assertIsInstance(errs[0], exc.ClientException)

    @mock.patch.object(create_resources, 'create_portgroups', autospec=True)
    @mock.patch.object(create_resources, 'create_ports', autospec=True)
    def test_create_nodes_no_ports_portgroups(self, mock_create_ports,
                                              mock_create_portgroups):
        node = {'driver': 'fake'}
        self.client.node.create.return_value = mock.Mock(uuid='uuid')
        self.assertEqual([], create_resources.create_nodes(self.client,
                                                           [node]))
        self.client.node.create.assert_called_once_with(driver='fake')
        self.assertFalse(mock_create_ports.called)
        self.assertFalse(mock_create_portgroups.called)

    @mock.patch.object(create_resources, 'create_nodes', autospec=True)
    def test_create_chassis(self, mock_create_nodes):
        chassis = {'description': 'fake', 'nodes': ['list of nodes']}
        self.client.chassis.create.return_value = mock.Mock(uuid='uuid')
        self.assertEqual([], create_resources.create_chassis(self.client,
                                                             [chassis]))
        self.client.chassis.create.assert_called_once_with(description='fake')
        mock_create_nodes.assert_called_once_with(
            self.client, ['list of nodes'], chassis_uuid='uuid')

    @mock.patch.object(create_resources, 'create_nodes', autospec=True)
    def test_create_chassis_exception(self, mock_create_nodes):
        chassis = {'description': 'fake', 'nodes': ['list of nodes']}
        self.client.chassis.create.side_effect = exc.ClientException('bar')
        errs = create_resources.create_chassis(self.client, [chassis])
        self.client.chassis.create.assert_called_once_with(description='fake')
        self.assertFalse(mock_create_nodes.called)
        self.assertEqual(1, len(errs))
        self.assertIsInstance(errs[0], exc.ClientException)

    @mock.patch.object(create_resources, 'create_nodes', autospec=True)
    def test_create_chassis_no_nodes(self, mock_create_nodes):
        chassis = {'description': 'fake'}
        self.client.chassis.create.return_value = mock.Mock(uuid='uuid')
        self.assertEqual([], create_resources.create_chassis(self.client,
                                                             [chassis]))
        self.client.chassis.create.assert_called_once_with(description='fake')
        self.assertFalse(mock_create_nodes.called)

    @mock.patch.object(create_resources, 'create_ports', autospec=True)
    def test_create_portgroups(self, mock_create_ports):
        portgroup = {'name': 'fake', 'ports': ['list of ports']}
        portgroup_posted = {'name': 'fake', 'node_uuid': 'fake-node-uuid'}
        self.client.portgroup.create.return_value = mock.Mock(uuid='uuid')
        self.assertEqual([], create_resources.create_portgroups(
            self.client, [portgroup], node_uuid='fake-node-uuid'))
        self.client.portgroup.create.assert_called_once_with(
            **portgroup_posted)
        mock_create_ports.assert_called_once_with(
            self.client, ['list of ports'], node_uuid='fake-node-uuid',
            portgroup_uuid='uuid')

    @mock.patch.object(create_resources, 'create_ports', autospec=True)
    def test_create_portgroups_exception(self, mock_create_ports):
        portgroup = {'name': 'fake', 'ports': ['list of ports']}
        portgroup_posted = {'name': 'fake', 'node_uuid': 'fake-node-uuid'}
        self.client.portgroup.create.side_effect = exc.ClientException('bar')
        errs = create_resources.create_portgroups(
            self.client, [portgroup], node_uuid='fake-node-uuid')
        self.client.portgroup.create.assert_called_once_with(
            **portgroup_posted)
        self.assertFalse(mock_create_ports.called)
        self.assertEqual(1, len(errs))
        self.assertIsInstance(errs[0], exc.ClientException)

    @mock.patch.object(create_resources, 'create_ports', autospec=True)
    def test_create_portgroups_two_node_uuids(self, mock_create_ports):
        portgroup = {'name': 'fake', 'node_uuid': 'fake-node-uuid-1',
                     'ports': ['list of ports']}
        self.client.portgroup.create.side_effect = exc.ClientException('bar')
        errs = create_resources.create_portgroups(
            self.client, [portgroup], node_uuid='fake-node-uuid-2')
        self.assertFalse(self.client.portgroup.create.called)
        self.assertFalse(mock_create_ports.called)
        self.assertEqual(1, len(errs))
        self.assertIsInstance(errs[0], exc.ClientException)

    @mock.patch.object(create_resources, 'create_ports', autospec=True)
    def test_create_portgroups_no_ports(self, mock_create_ports):
        portgroup = {'name': 'fake'}
        portgroup_posted = {'name': 'fake', 'node_uuid': 'fake-node-uuid'}
        self.client.portgroup.create.return_value = mock.Mock(uuid='uuid')
        self.assertEqual([], create_resources.create_portgroups(
            self.client, [portgroup], node_uuid='fake-node-uuid'))
        self.client.portgroup.create.assert_called_once_with(
            **portgroup_posted)
        self.assertFalse(mock_create_ports.called)
