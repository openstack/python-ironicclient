# Copyright 2013 Hewlett-Packard Development Company, L.P.
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
import tempfile
import time

import mock
import six
import testtools
from testtools.matchers import HasLength

from ironicclient.common import utils as common_utils
from ironicclient import exc
from ironicclient.tests.unit import utils
from ironicclient.v1 import node
from ironicclient.v1 import volume_connector
from ironicclient.v1 import volume_target

if six.PY3:
    import io
    file = io.BytesIO

NODE1 = {'uuid': '66666666-7777-8888-9999-000000000000',
         'chassis_uuid': 'aaaaaaaa-1111-bbbb-2222-cccccccccccc',
         'maintenance': False,
         'provision_state': 'available',
         'driver': 'fake',
         'driver_info': {'user': 'foo', 'password': 'bar'},
         'properties': {'num_cpu': 4},
         'name': 'fake-node-1',
         'resource_class': 'foo',
         'extra': {},
         'conductor_group': 'in-the-closet-to-the-left'}
NODE2 = {'uuid': '66666666-7777-8888-9999-111111111111',
         'instance_uuid': '66666666-7777-8888-9999-222222222222',
         'chassis_uuid': 'aaaaaaaa-1111-bbbb-2222-cccccccccccc',
         'maintenance': True,
         'driver': 'fake too',
         'driver_info': {'user': 'foo', 'password': 'bar'},
         'properties': {'num_cpu': 4},
         'resource_class': 'bar',
         'extra': {},
         'owner': '33333333-2222-1111-0000-111111111111'}
PORT = {'uuid': '11111111-2222-3333-4444-555555555555',
        'node_uuid': '66666666-7777-8888-9999-000000000000',
        'address': 'AA:AA:AA:AA:AA:AA',
        'extra': {}}
PORTGROUP = {'uuid': '11111111-2222-3333-4444-555555555555',
             'name': 'Portgroup',
             'node_uuid': '66666666-7777-8888-9999-000000000000',
             'address': 'AA:BB:CC:DD:EE:FF',
             'extra': {}}
CONNECTOR = {'uuid': 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
             'node_uuid': NODE1['uuid'],
             'type': 'iqn',
             'connector_id': 'iqn.2010-10.org.openstack:test',
             'extra': {}}
TARGET = {'uuid': 'cccccccc-dddd-eeee-ffff-000000000000',
          'node_uuid': NODE1['uuid'],
          'volume_type': 'iscsi',
          'properties': {'target_iqn': 'iqn.foo'},
          'boot_index': 0,
          'volume_id': '12345678',
          'extra': {}}


POWER_STATE = {'power_state': 'power on',
               'target_power_state': 'power off'}

DRIVER_IFACES = {'deploy': {'result': True},
                 'power': {'result': False, 'reason': 'Invalid IPMI username'},
                 'console': {'result': None, 'reason': 'not supported'},
                 'rescue': {'result': None, 'reason': 'not supported'}}

NODE_STATES = {"last_error": None,
               "power_state": "power on",
               "provision_state": "active",
               "target_power_state": None,
               "target_provision_state": None}

CONSOLE_DATA_ENABLED = {'console_enabled': True,
                        'console_info': {'test-console': 'test-console-data'}}
CONSOLE_DATA_DISABLED = {'console_enabled': False, 'console_info': None}

CONSOLE_ENABLE = 'true'

BOOT_DEVICE = {'boot_device': 'pxe', 'persistent': False}
SUPPORTED_BOOT_DEVICE = {'supported_boot_devices': ['pxe']}

NODE_VENDOR_PASSTHRU_METHOD = {"heartbeat": {"attach": "false",
                                             "http_methods": ["POST"],
                                             "description": "",
                                             "async": "true"}}

VIFS = {'vifs': [{'id': 'aaa-aaa'}]}
TRAITS = {'traits': ['CUSTOM_FOO', 'CUSTOM_BAR']}

CREATE_NODE = copy.deepcopy(NODE1)
del CREATE_NODE['uuid']
del CREATE_NODE['maintenance']
del CREATE_NODE['provision_state']

UPDATED_NODE = copy.deepcopy(NODE1)
NEW_DRIVER = 'new-driver'
UPDATED_NODE['driver'] = NEW_DRIVER

CREATE_WITH_UUID = copy.deepcopy(NODE1)
del CREATE_WITH_UUID['maintenance']
del CREATE_WITH_UUID['provision_state']

fake_responses = {
    '/v1/nodes':
    {
        'GET': (
            {},
            {"nodes": [NODE1, NODE2]}
        ),
        'POST': (
            {},
            CREATE_NODE,
        ),
    },
    '/v1/nodes/detail':
    {
        'GET': (
            {},
            {"nodes": [NODE1, NODE2]}
        ),
    },
    '/v1/nodes/?fields=uuid,extra':
    {
        'GET': (
            {},
            {"nodes": [NODE1]}
        ),
    },
    '/v1/nodes/?associated=False':
    {
        'GET': (
            {},
            {"nodes": [NODE1]},
        )
    },
    '/v1/nodes/?associated=True':
    {
        'GET': (
            {},
            {"nodes": [NODE2]},
        )
    },
    '/v1/nodes/?maintenance=False':
    {
        'GET': (
            {},
            {"nodes": [NODE1]},
        )
    },
    '/v1/nodes/?maintenance=True':
    {
        'GET': (
            {},
            {"nodes": [NODE2]},
        )
    },
    '/v1/nodes/?associated=True&maintenance=True':
    {
        'GET': (
            {},
            {"nodes": [NODE2]},
        )
    },
    '/v1/nodes/?provision_state=available':
    {
        'GET': (
            {},
            {"nodes": [NODE1]},
        )
    },
    '/v1/nodes/?owner=%s' % NODE2['owner']:
    {
        'GET': (
            {},
            {"nodes": [NODE2]},
        )
    },
    '/v1/nodes/?driver=fake':
    {
        'GET': (
            {},
            {"nodes": [NODE1]},
        )
    },
    '/v1/nodes/?resource_class=foo':
    {
        'GET': (
            {},
            {"nodes": [NODE1]},
        )
    },
    '/v1/nodes/?conductor_group=foo':
    {
        'GET': (
            {},
            {"nodes": [NODE1]},
        )
    },
    '/v1/nodes/?chassis_uuid=%s' % NODE2['chassis_uuid']:
    {
        'GET': (
            {},
            {"nodes": [NODE2]},
        )
    },
    '/v1/nodes/?conductor=fake-conductor':
    {
        'GET': (
            {},
            {"nodes": [NODE2]},
        )
    },
    '/v1/nodes/detail?instance_uuid=%s' % NODE2['instance_uuid']:
    {
        'GET': (
            {},
            {"nodes": [NODE2]},
        )
    },
    '/v1/nodes/%s' % NODE1['uuid']:
    {
        'GET': (
            {},
            NODE1,
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_NODE,
        ),
    },
    '/v1/nodes/%s?fields=uuid,extra' % NODE1['uuid']:
    {
        'GET': (
            {},
            NODE1,
        ),
    },
    '/v1/nodes/%s' % NODE2['uuid']:
    {
        'GET': (
            {},
            NODE2,
        ),
    },
    '/v1/nodes/%s' % NODE1['name']:
    {
        'GET': (
            {},
            NODE1,
        ),
    },
    '/v1/nodes/%s/ports' % NODE1['uuid']:
    {
        'GET': (
            {},
            {"ports": [PORT]},
        ),
    },
    '/v1/nodes/%s/ports' % NODE1['name']:
    {
        'GET': (
            {},
            {"ports": [PORT]},
        ),
    },
    '/v1/nodes/%s/ports/detail' % NODE1['uuid']:
    {
        'GET': (
            {},
            {"ports": [PORT]},
        ),
    },
    '/v1/nodes/%s/ports/detail' % NODE1['name']:
    {
        'GET': (
            {},
            {"ports": [PORT]},
        ),
    },
    '/v1/nodes/%s/ports?fields=uuid,address' % NODE1['uuid']:
    {
        'GET': (
            {},
            {"ports": [PORT]},
        ),
    },
    '/v1/nodes/%s/portgroups' % NODE1['uuid']:
    {
        'GET': (
            {},
            {"portgroups": [PORTGROUP]},
        ),
    },
    '/v1/nodes/%s/portgroups/detail' % NODE1['uuid']:
    {
        'GET': (
            {},
            {"portgroups": [PORTGROUP]},
        ),
    },
    '/v1/nodes/%s/portgroups?fields=uuid,address' % NODE1['uuid']:
    {
        'GET': (
            {},
            {"portgroups": [PORTGROUP]},
        ),
    },
    '/v1/nodes/%s/volume/connectors' % NODE1['uuid']:
    {
        'GET': (
            {},
            {"connectors": [CONNECTOR]},
        ),
    },
    '/v1/nodes/%s/volume/connectors?detail=True' % NODE1['uuid']:
    {
        'GET': (
            {},
            {"connectors": [CONNECTOR]},
        ),
    },
    '/v1/nodes/%s/volume/connectors?fields=uuid,connector_id' % NODE1['uuid']:
    {
        'GET': (
            {},
            {"connectors": [CONNECTOR]},
        ),
    },    '/v1/nodes/%s/volume/targets' % NODE1['uuid']:
    {
        'GET': (
            {},
            {"targets": [TARGET]},
        ),
    },
    '/v1/nodes/%s/volume/targets?detail=True' % NODE1['uuid']:
    {
        'GET': (
            {},
            {"targets": [TARGET]},
        ),
    },
    '/v1/nodes/%s/volume/targets?fields=uuid,value' % NODE1['uuid']:
    {
        'GET': (
            {},
            {"targets": [TARGET]},
        ),
    },
    '/v1/nodes/%s/maintenance' % NODE1['uuid']:
    {
        'PUT': (
            {},
            None,
        ),
        'DELETE': (
            {},
            None,
        ),
    },
    '/v1/nodes/%s/states/power' % NODE1['uuid']:
    {
        'PUT': (
            {},
            POWER_STATE,
        ),
    },
    '/v1/nodes/%s/validate' % NODE1['uuid']:
    {
        'GET': (
            {},
            DRIVER_IFACES,
        ),
    },
    '/v1/nodes/%s/states/provision' % NODE1['uuid']:
    {
        'PUT': (
            {},
            None,
        ),
    },
    '/v1/nodes/%s/states' % NODE1['uuid']:
    {
        'GET': (
            {},
            NODE_STATES,
        ),
    },
    '/v1/nodes/%s/states/raid' % NODE1['uuid']:
    {
        'PUT': (
            {},
            None,
        ),
    },
    '/v1/nodes/%s/states/console' % NODE1['uuid']:
    {
        'GET': (
            {},
            CONSOLE_DATA_ENABLED,
        ),
        'PUT': (
            {'enabled': CONSOLE_ENABLE},
            None,
        ),
    },
    '/v1/nodes/%s/states/console' % NODE2['uuid']:
    {
        'GET': (
            {},
            CONSOLE_DATA_DISABLED,
        ),
    },
    '/v1/nodes/%s/management/boot_device' % NODE1['uuid']:
    {
        'GET': (
            {},
            BOOT_DEVICE,
        ),
        'PUT': (
            {},
            None,
        ),
    },
    '/v1/nodes/%s/management/inject_nmi' % NODE1['uuid']:
    {
        'PUT': (
            {},
            None,
        ),
    },
    '/v1/nodes/%s/management/boot_device/supported' % NODE1['uuid']:
    {
        'GET': (
            {},
            SUPPORTED_BOOT_DEVICE,
        ),
    },
    '/v1/nodes/%s/vendor_passthru/methods' % NODE1['uuid']:
    {
        'GET': (
            {},
            NODE_VENDOR_PASSTHRU_METHOD,
        ),
    },
    '/v1/nodes/%s/vifs' % NODE1['uuid']:
    {
        'GET': (
            {},
            VIFS,
        ),
    },
    '/v1/nodes/%s/traits' % NODE1['uuid']:
    {
        'GET': (
            {},
            TRAITS,
        ),
        'PUT': (
            {},
            None,
        ),
        'DELETE': (
            {},
            None,
        ),
    },
    '/v1/nodes/%s/traits/CUSTOM_FOO' % NODE1['uuid']:
    {
        'PUT': (
            {},
            None,
        ),
        'DELETE': (
            {},
            None,
        ),
    }
}

fake_responses_pagination = {
    '/v1/nodes':
    {
        'GET': (
            {},
            {"nodes": [NODE1],
             "next": "http://127.0.0.1:6385/v1/nodes/?limit=1"}
        ),
    },
    '/v1/nodes/?limit=1':
    {
        'GET': (
            {},
            {"nodes": [NODE2]}
        ),
    },
    '/v1/nodes/?marker=%s' % NODE1['uuid']:
    {
        'GET': (
            {},
            {"nodes": [NODE2]}
        ),
    },
    '/v1/nodes/%s/ports?limit=1' % NODE1['uuid']:
    {
        'GET': (
            {},
            {"ports": [PORT]},
        ),
    },
    '/v1/nodes/%s/ports?marker=%s' % (NODE1['uuid'], PORT['uuid']):
    {
        'GET': (
            {},
            {"ports": [PORT]},
        ),
    },
    '/v1/nodes/%s/portgroups?limit=1' % NODE1['uuid']:
    {
        'GET': (
            {},
            {"portgroups": [PORTGROUP]},
        ),
    },
    '/v1/nodes/%s/portgroups?marker=%s' % (NODE1['uuid'], PORTGROUP['uuid']):
    {
        'GET': (
            {},
            {"portgroups": [PORTGROUP]},
        ),
    },
    '/v1/nodes/%s/volume/connectors?limit=1' % NODE1['uuid']:
    {
        'GET': (
            {},
            {"connectors": [CONNECTOR]},
        ),
    },
    '/v1/nodes/%s/volume/connectors?marker=%s' % (NODE1['uuid'],
                                                  CONNECTOR['uuid']):
    {
        'GET': (
            {},
            {"connectors": [CONNECTOR]},
        ),
    },
    '/v1/nodes/%s/volume/targets?limit=1' % NODE1['uuid']:
    {
        'GET': (
            {},
            {"targets": [TARGET]},
        ),
    },
    '/v1/nodes/%s/volume/targets?marker=%s' % (NODE1['uuid'], TARGET['uuid']):
    {
        'GET': (
            {},
            {"targets": [TARGET]},
        ),
    },
}

fake_responses_pagination_path_prefix = {
    '/baremetal/v1/nodes':
    {
        'GET': (
            {},
            {"nodes": [NODE1],
             "next": "http://127.0.0.1:6385/baremetal/v1/nodes/?limit=1"}
        ),
    },
    '/baremetal/v1/nodes/?limit=1':
    {
        'GET': (
            {},
            {"nodes": [NODE2]}
        ),
    },
}

fake_responses_sorting = {
    '/v1/nodes/?sort_key=updated_at':
    {
        'GET': (
            {},
            {"nodes": [NODE2, NODE1]}
        ),
    },
    '/v1/nodes/?sort_dir=desc':
    {
        'GET': (
            {},
            {"nodes": [NODE2, NODE1]}
        ),
    },
    '/v1/nodes/%s/ports?sort_key=updated_at' % NODE1['uuid']:
    {
        'GET': (
            {},
            {"ports": [PORT]},
        ),
    },
    '/v1/nodes/%s/ports?sort_dir=desc' % NODE1['uuid']:
    {
        'GET': (
            {},
            {"ports": [PORT]},
        ),
    },
    '/v1/nodes/%s/portgroups?sort_key=updated_at' % NODE1['uuid']:
    {
        'GET': (
            {},
            {"portgroups": [PORTGROUP]},
        ),
    },
    '/v1/nodes/%s/portgroups?sort_dir=desc' % NODE1['uuid']:
    {
        'GET': (
            {},
            {"portgroups": [PORTGROUP]},
        ),
    },
    '/v1/nodes/%s/volume/connectors?sort_key=updated_at' % NODE1['uuid']:
    {
        'GET': (
            {},
            {"connectors": [CONNECTOR]},
        ),
    },
    '/v1/nodes/%s/volume/connectors?sort_dir=desc' % NODE1['uuid']:
    {
        'GET': (
            {},
            {"connectors": [CONNECTOR]},
        ),
    },
    '/v1/nodes/%s/volume/targets?sort_key=updated_at' % NODE1['uuid']:
    {
        'GET': (
            {},
            {"targets": [TARGET]},
        ),
    },
    '/v1/nodes/%s/volume/targets?sort_dir=desc' % NODE1['uuid']:
    {
        'GET': (
            {},
            {"targets": [TARGET]},
        ),
    },
}


class NodeManagerTest(testtools.TestCase):

    def setUp(self):
        super(NodeManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = node.NodeManager(self.api)

    def test_node_list(self):
        nodes = self.mgr.list()
        expect = [
            ('GET', '/v1/nodes', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(nodes))

    def test_node_list_shows_name(self):
        nodes = self.mgr.list()
        self.assertIsNotNone(getattr(nodes[0], 'name'))

    def test_node_list_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = node.NodeManager(self.api)
        nodes = self.mgr.list(limit=1)
        expect = [
            ('GET', '/v1/nodes/?limit=1', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(nodes, HasLength(1))

    def test_node_list_marker(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = node.NodeManager(self.api)
        nodes = self.mgr.list(marker=NODE1['uuid'])
        expect = [
            ('GET', '/v1/nodes/?marker=%s' % NODE1['uuid'], {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(nodes, HasLength(1))

    def test_node_list_pagination_no_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = node.NodeManager(self.api)
        nodes = self.mgr.list(limit=0)
        expect = [
            ('GET', '/v1/nodes', {}, None),
            ('GET', '/v1/nodes/?limit=1', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(nodes))

    def test_node_list_pagination_no_limit_path_prefix(self):
        self.api = utils.FakeAPI(fake_responses_pagination_path_prefix,
                                 path_prefix='/baremetal')
        self.mgr = node.NodeManager(self.api)
        nodes = self.mgr.list(limit=0)
        expect = [
            ('GET', '/baremetal/v1/nodes', {}, None),
            ('GET', '/baremetal/v1/nodes/?limit=1', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(nodes))

    def test_node_list_sort_key(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = node.NodeManager(self.api)
        nodes = self.mgr.list(sort_key='updated_at')
        expect = [
            ('GET', '/v1/nodes/?sort_key=updated_at', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(nodes))

    def test_node_list_sort_dir(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = node.NodeManager(self.api)
        nodes = self.mgr.list(sort_dir='desc')
        expect = [
            ('GET', '/v1/nodes/?sort_dir=desc', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(nodes))

    def test_node_list_associated(self):
        nodes = self.mgr.list(associated=True)
        expect = [
            ('GET', '/v1/nodes/?associated=True', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(nodes, HasLength(1))
        self.assertEqual(NODE2['uuid'], getattr(nodes[0], 'uuid'))

    def test_node_list_unassociated(self):
        nodes = self.mgr.list(associated=False)
        expect = [
            ('GET', '/v1/nodes/?associated=False', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(nodes, HasLength(1))
        self.assertEqual(NODE1['uuid'], getattr(nodes[0], 'uuid'))

    def test_node_list_unassociated_string(self):
        nodes = self.mgr.list(associated="False")
        expect = [
            ('GET', '/v1/nodes/?associated=False', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(nodes, HasLength(1))
        self.assertEqual(NODE1['uuid'], getattr(nodes[0], 'uuid'))

    def test_node_list_maintenance(self):
        nodes = self.mgr.list(maintenance=True)
        expect = [
            ('GET', '/v1/nodes/?maintenance=True', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(nodes, HasLength(1))
        self.assertEqual(NODE2['uuid'], getattr(nodes[0], 'uuid'))

    def test_node_list_maintenance_string(self):
        nodes = self.mgr.list(maintenance="True")
        expect = [
            ('GET', '/v1/nodes/?maintenance=True', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(nodes, HasLength(1))
        self.assertEqual(NODE2['uuid'], getattr(nodes[0], 'uuid'))

    def test_node_list_provision_state(self):
        nodes = self.mgr.list(provision_state="available")
        expect = [
            ('GET', '/v1/nodes/?provision_state=available', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(nodes, HasLength(1))
        self.assertEqual(NODE1['uuid'], getattr(nodes[0], 'uuid'))

    def test_node_list_owner(self):
        nodes = self.mgr.list(owner=NODE2['owner'])
        expect = [
            ('GET', '/v1/nodes/?owner=%s' % NODE2['owner'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(nodes, HasLength(1))
        self.assertEqual(NODE2['owner'], getattr(nodes[0], 'owner'))

    def test_node_list_provision_state_fail(self):
        self.assertRaises(KeyError, self.mgr.list,
                          provision_state="test")

    def test_node_list_driver(self):
        nodes = self.mgr.list(driver="fake")
        expect = [
            ('GET', '/v1/nodes/?driver=fake', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(nodes, HasLength(1))
        self.assertEqual(NODE1['uuid'], getattr(nodes[0], 'uuid'))

    def test_node_list_resource_class(self):
        nodes = self.mgr.list(resource_class="foo")
        expect = [
            ('GET', '/v1/nodes/?resource_class=foo', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(nodes, HasLength(1))
        self.assertEqual(NODE1['uuid'], getattr(nodes[0], 'uuid'))

    def test_node_list_conductor_group(self):
        nodes = self.mgr.list(conductor_group='foo')
        expect = [
            ('GET', '/v1/nodes/?conductor_group=foo', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(nodes, HasLength(1))
        self.assertEqual(NODE1['uuid'], getattr(nodes[0], 'uuid'))

    def test_node_list_chassis(self):
        ch2 = NODE2['chassis_uuid']
        nodes = self.mgr.list(chassis=ch2)
        expect = [
            ('GET', '/v1/nodes/?chassis_uuid=%s' % ch2, {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(nodes, HasLength(1))
        self.assertEqual(NODE2['uuid'], getattr(nodes[0], 'uuid'))

    def test_node_list_no_maintenance(self):
        nodes = self.mgr.list(maintenance=False)
        expect = [
            ('GET', '/v1/nodes/?maintenance=False', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(nodes, HasLength(1))
        self.assertEqual(NODE1['uuid'], getattr(nodes[0], 'uuid'))

    def test_node_list_associated_and_maintenance(self):
        nodes = self.mgr.list(associated=True, maintenance=True)
        expect = [
            ('GET', '/v1/nodes/?associated=True&maintenance=True', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(nodes, HasLength(1))
        self.assertEqual(NODE2['uuid'], getattr(nodes[0], 'uuid'))

    def test_node_list_with_conductor(self):
        nodes = self.mgr.list(conductor='fake-conductor')
        expect = [
            ('GET', '/v1/nodes/?conductor=fake-conductor', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(nodes, HasLength(1))
        self.assertEqual(NODE2['uuid'], getattr(nodes[0], 'uuid'))

    def test_node_list_detail(self):
        nodes = self.mgr.list(detail=True)
        expect = [
            ('GET', '/v1/nodes/detail', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(nodes))
        self.assertEqual(nodes[0].extra, {})

    def test_node_list_detail_microversion_override(self):
        nodes = self.mgr.list(detail=True, os_ironic_api_version='1.30')
        expect = [
            ('GET', '/v1/nodes/detail',
             {'X-OpenStack-Ironic-API-Version': '1.30'}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(nodes))
        self.assertEqual(nodes[0].extra, {})

    def test_node_list_fields(self):
        nodes = self.mgr.list(fields=['uuid', 'extra'])
        expect = [
            ('GET', '/v1/nodes/?fields=uuid,extra', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(nodes))

    def test_node_list_detail_and_fields_fail(self):
        self.assertRaises(exc.InvalidAttribute, self.mgr.list,
                          detail=True, fields=['uuid', 'extra'])

    def test_node_show(self):
        node = self.mgr.get(NODE1['uuid'])
        expect = [
            ('GET', '/v1/nodes/%s' % NODE1['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NODE1['uuid'], node.uuid)

    def test_node_show_by_instance(self):
        node = self.mgr.get_by_instance_uuid(NODE2['instance_uuid'])
        expect = [
            ('GET', '/v1/nodes/detail?instance_uuid=%s' %
             NODE2['instance_uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NODE2['uuid'], node.uuid)

    def test_node_show_by_name(self):
        node = self.mgr.get(NODE1['name'])
        expect = [
            ('GET', '/v1/nodes/%s' % NODE1['name'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NODE1['uuid'], node.uuid)

    def test_node_show_fields(self):
        node = self.mgr.get(NODE1['uuid'], fields=['uuid', 'extra'])
        expect = [
            ('GET', '/v1/nodes/%s?fields=uuid,extra' %
             NODE1['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NODE1['uuid'], node.uuid)

    def test_create(self):
        node = self.mgr.create(**CREATE_NODE)
        expect = [
            ('POST', '/v1/nodes', {}, CREATE_NODE),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(node)

    def test_create_with_uuid(self):
        node = self.mgr.create(**CREATE_WITH_UUID)
        expect = [
            ('POST', '/v1/nodes', {}, CREATE_WITH_UUID),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(node)

    def test_delete(self):
        node = self.mgr.delete(node_id=NODE1['uuid'])
        expect = [
            ('DELETE', '/v1/nodes/%s' % NODE1['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(node)

    def test_update(self):
        patch = {'op': 'replace',
                 'value': NEW_DRIVER,
                 'path': '/driver'}
        node = self.mgr.update(node_id=NODE1['uuid'], patch=patch)
        expect = [
            ('PATCH', '/v1/nodes/%s' % NODE1['uuid'], {}, patch),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NEW_DRIVER, node.driver)

    def test_update_with_reset_interfaces(self):
        patch = {'op': 'replace',
                 'value': NEW_DRIVER,
                 'path': '/driver'}
        node = self.mgr.update(node_id=NODE1['uuid'], patch=patch,
                               reset_interfaces=True)
        expect = [
            ('PATCH', '/v1/nodes/%s' % NODE1['uuid'],
             {}, patch, {'reset_interfaces': True}),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NEW_DRIVER, node.driver)

    def test_update_microversion_override(self):
        patch = {'op': 'replace',
                 'value': NEW_DRIVER,
                 'path': '/driver'}
        node = self.mgr.update(node_id=NODE1['uuid'], patch=patch,
                               os_ironic_api_version='1.24')
        expect = [
            ('PATCH', '/v1/nodes/%s' % NODE1['uuid'],
             {'X-OpenStack-Ironic-API-Version': '1.24'}, patch),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NEW_DRIVER, node.driver)

    def test_node_port_list_with_uuid(self):
        ports = self.mgr.list_ports(NODE1['uuid'])
        expect = [
            ('GET', '/v1/nodes/%s/ports' % NODE1['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(ports, HasLength(1))
        self.assertEqual(PORT['uuid'], ports[0].uuid)
        self.assertEqual(PORT['address'], ports[0].address)

    def test_node_port_list_with_name(self):
        ports = self.mgr.list_ports(NODE1['name'])
        expect = [
            ('GET', '/v1/nodes/%s/ports' % NODE1['name'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(ports, HasLength(1))
        self.assertEqual(PORT['uuid'], ports[0].uuid)
        self.assertEqual(PORT['address'], ports[0].address)

    def test_node_port_list_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = node.NodeManager(self.api)
        ports = self.mgr.list_ports(NODE1['uuid'], limit=1)
        expect = [
            ('GET', '/v1/nodes/%s/ports?limit=1' % NODE1['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(ports, HasLength(1))
        self.assertEqual(PORT['uuid'], ports[0].uuid)
        self.assertEqual(PORT['address'], ports[0].address)

    def test_node_port_list_marker(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = node.NodeManager(self.api)
        ports = self.mgr.list_ports(NODE1['uuid'], marker=PORT['uuid'])
        expect = [
            ('GET', '/v1/nodes/%s/ports?marker=%s' % (NODE1['uuid'],
                                                      PORT['uuid']), {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(ports, HasLength(1))

    def test_node_port_list_sort_key(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = node.NodeManager(self.api)
        ports = self.mgr.list_ports(NODE1['uuid'], sort_key='updated_at')
        expect = [
            ('GET', '/v1/nodes/%s/ports?sort_key=updated_at' % NODE1['uuid'],
             {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(ports, HasLength(1))
        self.assertEqual(PORT['uuid'], ports[0].uuid)
        self.assertEqual(PORT['address'], ports[0].address)

    def test_node_port_list_sort_dir(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = node.NodeManager(self.api)
        ports = self.mgr.list_ports(NODE1['uuid'], sort_dir='desc')
        expect = [
            ('GET', '/v1/nodes/%s/ports?sort_dir=desc' % NODE1['uuid'],
             {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(ports, HasLength(1))
        self.assertEqual(PORT['uuid'], ports[0].uuid)
        self.assertEqual(PORT['address'], ports[0].address)

    def test_node_port_list_detail_with_uuid(self):
        ports = self.mgr.list_ports(NODE1['uuid'], detail=True)
        expect = [
            ('GET', '/v1/nodes/%s/ports/detail' % NODE1['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(ports, HasLength(1))

    def test_node_port_list_detail_with_name(self):
        ports = self.mgr.list_ports(NODE1['name'], detail=True)
        expect = [
            ('GET', '/v1/nodes/%s/ports/detail' % NODE1['name'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(ports, HasLength(1))

    def test_node_port_list_fields(self):
        ports = self.mgr.list_ports(NODE1['uuid'], fields=['uuid', 'address'])
        expect = [
            ('GET', '/v1/nodes/%s/ports?fields=uuid,address' %
             NODE1['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(ports, HasLength(1))

    def test_node_port_list_detail_and_fields_fail(self):
        self.assertRaises(exc.InvalidAttribute, self.mgr.list_ports,
                          NODE1['uuid'], detail=True, fields=['uuid', 'extra'])

    def _validate_node_volume_connector_list(self, expect, volume_connectors):
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(volume_connectors))
        self.assertIsInstance(volume_connectors[0],
                              volume_connector.VolumeConnector)
        self.assertEqual(CONNECTOR['uuid'], volume_connectors[0].uuid)
        self.assertEqual(CONNECTOR['type'], volume_connectors[0].type)
        self.assertEqual(CONNECTOR['connector_id'],
                         volume_connectors[0].connector_id)

    def test_node_volume_connector_list(self):
        volume_connectors = self.mgr.list_volume_connectors(NODE1['uuid'])
        expect = [
            ('GET', '/v1/nodes/%s/volume/connectors' % NODE1['uuid'],
             {}, None),
        ]
        self._validate_node_volume_connector_list(expect, volume_connectors)

    def test_node_volume_connector_list_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = node.NodeManager(self.api)
        volume_connectors = self.mgr.list_volume_connectors(NODE1['uuid'],
                                                            limit=1)
        expect = [
            ('GET', '/v1/nodes/%s/volume/connectors?limit=1' % NODE1['uuid'],
             {}, None),
        ]
        self._validate_node_volume_connector_list(expect, volume_connectors)

    def test_node_volume_connector_list_marker(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = node.NodeManager(self.api)
        volume_connectors = self.mgr.list_volume_connectors(
            NODE1['uuid'], marker=CONNECTOR['uuid'])
        expect = [
            ('GET', '/v1/nodes/%s/volume/connectors?marker=%s' % (
                NODE1['uuid'], CONNECTOR['uuid']), {}, None),
        ]
        self._validate_node_volume_connector_list(expect, volume_connectors)

    def test_node_volume_connector_list_sort_key(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = node.NodeManager(self.api)
        volume_connectors = self.mgr.list_volume_connectors(
            NODE1['uuid'], sort_key='updated_at')
        expect = [
            ('GET', '/v1/nodes/%s/volume/connectors?sort_key=updated_at' %
             NODE1['uuid'], {}, None),
        ]
        self._validate_node_volume_connector_list(expect, volume_connectors)

    def test_node_volume_connector_list_sort_dir(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = node.NodeManager(self.api)
        volume_connectors = self.mgr.list_volume_connectors(NODE1['uuid'],
                                                            sort_dir='desc')
        expect = [
            ('GET', '/v1/nodes/%s/volume/connectors?sort_dir=desc' %
             NODE1['uuid'], {}, None),
        ]
        self._validate_node_volume_connector_list(expect, volume_connectors)

    def test_node_volume_connector_list_detail(self):
        volume_connectors = self.mgr.list_volume_connectors(NODE1['uuid'],
                                                            detail=True)
        expect = [
            ('GET',
             '/v1/nodes/%s/volume/connectors?detail=True' % NODE1['uuid'],
             {}, None),
        ]
        self._validate_node_volume_connector_list(expect, volume_connectors)

    def test_node_volume_connector_list_fields(self):
        volume_connectors = self.mgr.list_volume_connectors(
            NODE1['uuid'], fields=['uuid', 'connector_id'])
        expect = [
            ('GET', '/v1/nodes/%s/volume/connectors?fields=uuid,connector_id' %
             NODE1['uuid'], {}, None),
        ]
        self._validate_node_volume_connector_list(expect, volume_connectors)

    def test_node_volume_connector_list_detail_and_fields_fail(self):
        self.assertRaises(exc.InvalidAttribute,
                          self.mgr.list_volume_connectors,
                          NODE1['uuid'], detail=True, fields=['uuid', 'extra'])

    def _validate_node_volume_target_list(self, expect, volume_targets):
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(volume_targets))
        self.assertIsInstance(volume_targets[0],
                              volume_target.VolumeTarget)
        self.assertEqual(TARGET['uuid'], volume_targets[0].uuid)
        self.assertEqual(TARGET['volume_type'], volume_targets[0].volume_type)
        self.assertEqual(TARGET['boot_index'], volume_targets[0].boot_index)
        self.assertEqual(TARGET['volume_id'], volume_targets[0].volume_id)
        self.assertEqual(TARGET['node_uuid'], volume_targets[0].node_uuid)

    def test_node_volume_target_list(self):
        volume_targets = self.mgr.list_volume_targets(NODE1['uuid'])
        expect = [
            ('GET', '/v1/nodes/%s/volume/targets' % NODE1['uuid'],
             {}, None),
        ]
        self._validate_node_volume_target_list(expect, volume_targets)

    def test_node_volume_target_list_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = node.NodeManager(self.api)
        volume_targets = self.mgr.list_volume_targets(NODE1['uuid'], limit=1)
        expect = [
            ('GET', '/v1/nodes/%s/volume/targets?limit=1' % NODE1['uuid'],
             {}, None),
        ]
        self._validate_node_volume_target_list(expect, volume_targets)

    def test_node_volume_target_list_marker(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = node.NodeManager(self.api)
        volume_targets = self.mgr.list_volume_targets(
            NODE1['uuid'], marker=TARGET['uuid'])
        expect = [
            ('GET', '/v1/nodes/%s/volume/targets?marker=%s' % (
                NODE1['uuid'], TARGET['uuid']), {}, None),
        ]
        self._validate_node_volume_target_list(expect, volume_targets)

    def test_node_volume_target_list_sort_key(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = node.NodeManager(self.api)
        volume_targets = self.mgr.list_volume_targets(
            NODE1['uuid'], sort_key='updated_at')
        expect = [
            ('GET', '/v1/nodes/%s/volume/targets?sort_key=updated_at' %
             NODE1['uuid'], {}, None),
        ]
        self._validate_node_volume_target_list(expect, volume_targets)

    def test_node_volume_target_list_sort_dir(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = node.NodeManager(self.api)
        volume_targets = self.mgr.list_volume_targets(NODE1['uuid'],
                                                      sort_dir='desc')
        expect = [
            ('GET', '/v1/nodes/%s/volume/targets?sort_dir=desc' %
             NODE1['uuid'], {}, None),
        ]
        self._validate_node_volume_target_list(expect, volume_targets)

    def test_node_volume_target_list_detail(self):
        volume_targets = self.mgr.list_volume_targets(NODE1['uuid'],
                                                      detail=True)
        expect = [
            ('GET', '/v1/nodes/%s/volume/targets?detail=True' % NODE1['uuid'],
             {}, None),
        ]
        self._validate_node_volume_target_list(expect, volume_targets)

    def test_node_volume_target_list_fields(self):
        volume_targets = self.mgr.list_volume_targets(
            NODE1['uuid'], fields=['uuid', 'value'])
        expect = [
            ('GET', '/v1/nodes/%s/volume/targets?fields=uuid,value' %
             NODE1['uuid'], {}, None),
        ]
        self._validate_node_volume_target_list(expect, volume_targets)

    def test_node_volume_target_list_detail_and_fields_fail(self):
        self.assertRaises(exc.InvalidAttribute,
                          self.mgr.list_volume_targets,
                          NODE1['uuid'], detail=True, fields=['uuid', 'extra'])

    def test_node_set_maintenance_true(self):
        maintenance = self.mgr.set_maintenance(NODE1['uuid'], 'true',
                                               maint_reason='reason')
        body = {'reason': 'reason'}
        expect = [
            ('PUT', '/v1/nodes/%s/maintenance' % NODE1['uuid'], {}, body),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(maintenance)

    def test_node_set_maintenance_false(self):
        maintenance = self.mgr.set_maintenance(NODE1['uuid'], 'false')
        expect = [
            ('DELETE', '/v1/nodes/%s/maintenance' % NODE1['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(maintenance)

    def test_node_set_maintenance_on(self):
        maintenance = self.mgr.set_maintenance(NODE1['uuid'], 'on',
                                               maint_reason='reason')
        body = {'reason': 'reason'}
        expect = [
            ('PUT', '/v1/nodes/%s/maintenance' % NODE1['uuid'], {}, body),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(maintenance)

    def test_node_set_maintenance_off(self):
        maintenance = self.mgr.set_maintenance(NODE1['uuid'], 'off')
        expect = [
            ('DELETE', '/v1/nodes/%s/maintenance' % NODE1['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(maintenance)

    def test_node_set_maintenance_bad(self):
        self.assertRaises(exc.InvalidAttribute, self.mgr.set_maintenance,
                          NODE1['uuid'], 'bad')

    def test_node_set_maintenance_bool(self):
        maintenance = self.mgr.set_maintenance(NODE1['uuid'], True,
                                               maint_reason='reason')
        body = {'reason': 'reason'}
        expect = [
            ('PUT', '/v1/nodes/%s/maintenance' % NODE1['uuid'], {}, body),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(maintenance)

    def test_node_set_power_state(self):
        power_state = self.mgr.set_power_state(NODE1['uuid'], "off")
        body = {'target': 'power off'}
        expect = [
            ('PUT', '/v1/nodes/%s/states/power' % NODE1['uuid'], {}, body),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual('power off', power_state.target_power_state)

    def test_node_set_power_timeout(self):
        power_state = self.mgr.set_power_state(NODE1['uuid'], "off", timeout=2)
        body = {'target': 'power off', 'timeout': 2}
        expect = [
            ('PUT', '/v1/nodes/%s/states/power' % NODE1['uuid'], {}, body),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual('power off', power_state.target_power_state)

    def test_node_set_power_timeout_str(self):
        power_state = self.mgr.set_power_state(NODE1['uuid'], "off",
                                               timeout="2")
        body = {'target': 'power off', 'timeout': 2}
        expect = [
            ('PUT', '/v1/nodes/%s/states/power' % NODE1['uuid'], {}, body),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual('power off', power_state.target_power_state)

    def test_node_set_power_state_soft(self):
        power_state = self.mgr.set_power_state(NODE1['uuid'], "off", soft=True)
        body = {'target': 'soft power off'}
        expect = [
            ('PUT', '/v1/nodes/%s/states/power' % NODE1['uuid'], {}, body),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual('power off', power_state.target_power_state)

    def test_node_set_power_state_soft_fail(self):
        self.assertRaises(ValueError,
                          self.mgr.set_power_state,
                          NODE1['uuid'], 'on', soft=True)

    def test_node_set_power_state_on_timeout_fail(self):
        self.assertRaises(ValueError,
                          self.mgr.set_power_state,
                          NODE1['uuid'], 'off', soft=False, timeout=0)

    def test_node_set_power_state_on_timeout_type_error(self):
        self.assertRaises(ValueError,
                          self.mgr.set_power_state,
                          NODE1['uuid'], 'off', soft=False, timeout='a')

    def test_set_target_raid_config(self):
        self.mgr.set_target_raid_config(
            NODE1['uuid'], {'fake': 'config'})

        expect = [('PUT', '/v1/nodes/%s/states/raid' % NODE1['uuid'],
                  {},
                  {'fake': 'config'})]
        self.assertEqual(expect, self.api.calls)

    def test_node_validate(self):
        ifaces = self.mgr.validate(NODE1['uuid'])
        expect = [
            ('GET', '/v1/nodes/%s/validate' % NODE1['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(DRIVER_IFACES['power'], ifaces.power)
        self.assertEqual(DRIVER_IFACES['deploy'], ifaces.deploy)
        self.assertEqual(DRIVER_IFACES['rescue'], ifaces.rescue)
        self.assertEqual(DRIVER_IFACES['console'], ifaces.console)

    def test_node_set_provision_state(self):
        target_state = 'active'
        self.mgr.set_provision_state(NODE1['uuid'], target_state)
        body = {'target': target_state}
        expect = [
            ('PUT', '/v1/nodes/%s/states/provision' % NODE1['uuid'], {}, body),
        ]
        self.assertEqual(expect, self.api.calls)

    def test_node_set_provision_state_microversion_override(self):
        target_state = 'active'
        self.mgr.set_provision_state(NODE1['uuid'], target_state,
                                     os_ironic_api_version="1.35")
        body = {'target': target_state}
        expect = [
            ('PUT', '/v1/nodes/%s/states/provision' % NODE1['uuid'],
             {'X-OpenStack-Ironic-API-Version': '1.35'}, body),
        ]
        self.assertEqual(expect, self.api.calls)

    def test_node_set_provision_state_with_configdrive(self):
        target_state = 'active'
        self.mgr.set_provision_state(NODE1['uuid'], target_state,
                                     configdrive='foo')
        body = {'target': target_state, 'configdrive': 'foo'}
        expect = [
            ('PUT', '/v1/nodes/%s/states/provision' % NODE1['uuid'], {}, body),
        ]
        self.assertEqual(expect, self.api.calls)

    def test_node_set_provision_state_with_configdrive_as_dict(self):
        target_state = 'active'
        self.mgr.set_provision_state(NODE1['uuid'], target_state,
                                     configdrive={'user_data': ''})
        body = {'target': target_state, 'configdrive': {'user_data': ''}}
        expect = [
            ('PUT', '/v1/nodes/%s/states/provision' % NODE1['uuid'], {}, body),
        ]
        self.assertEqual(expect, self.api.calls)

    def test_node_set_provision_state_with_configdrive_file(self):
        target_state = 'active'
        file_content = b'foo bar cat meow dog bark'

        with tempfile.NamedTemporaryFile() as f:
            f.write(file_content)
            f.flush()
            self.mgr.set_provision_state(NODE1['uuid'], target_state,
                                         configdrive=f.name)

        body = {'target': target_state, 'configdrive': file_content}
        expect = [
            ('PUT', '/v1/nodes/%s/states/provision' % NODE1['uuid'], {}, body),
        ]
        self.assertEqual(expect, self.api.calls)

    @mock.patch.object(common_utils, 'make_configdrive', autospec=True)
    def test_node_set_provision_state_with_configdrive_dir(self,
                                                           mock_configdrive):
        mock_configdrive.return_value = 'fake-configdrive'
        target_state = 'active'

        with common_utils.tempdir() as dirname:
            self.mgr.set_provision_state(NODE1['uuid'], target_state,
                                         configdrive=dirname)
            mock_configdrive.assert_called_once_with(dirname)

        body = {'target': target_state, 'configdrive': 'fake-configdrive'}
        expect = [
            ('PUT', '/v1/nodes/%s/states/provision' % NODE1['uuid'], {}, body),
        ]
        self.assertEqual(expect, self.api.calls)

    def test_node_set_provision_state_with_cleansteps(self):
        cleansteps = [{"step": "upgrade", "interface": "deploy"}]
        target_state = 'clean'
        self.mgr.set_provision_state(NODE1['uuid'], target_state,
                                     cleansteps=cleansteps)
        body = {'target': target_state, 'clean_steps': cleansteps}
        expect = [
            ('PUT', '/v1/nodes/%s/states/provision' % NODE1['uuid'], {}, body),
        ]
        self.assertEqual(expect, self.api.calls)

    def test_node_set_provision_state_with_rescue_password(self):
        rescue_password = 'supersecret'
        target_state = 'rescue'
        self.mgr.set_provision_state(NODE1['uuid'], target_state,
                                     rescue_password=rescue_password)
        body = {'target': target_state, 'rescue_password': rescue_password}
        expect = [
            ('PUT', '/v1/nodes/%s/states/provision' % NODE1['uuid'], {}, body),
        ]
        self.assertEqual(expect, self.api.calls)

    def test_node_states(self):
        states = self.mgr.states(NODE1['uuid'])
        expect = [
            ('GET', '/v1/nodes/%s/states' % NODE1['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        expected_fields = ['last_error', 'power_state', 'provision_state',
                           'target_power_state', 'target_provision_state']
        self.assertEqual(sorted(expected_fields),
                         sorted(states.to_dict().keys()))

    def test_node_set_console_mode(self):
        global ENABLE
        for enabled in ['true', True, 'False', False]:
            self.api.calls = []
            ENABLE = enabled
            self.mgr.set_console_mode(NODE1['uuid'], enabled)
            body = {'enabled': enabled}
            expect = [
                ('PUT', '/v1/nodes/%s/states/console' % NODE1['uuid'], {},
                 body),
            ]
            self.assertEqual(expect, self.api.calls)

    def test_node_get_console(self):
        info = self.mgr.get_console(NODE1['uuid'])
        expect = [
            ('GET', '/v1/nodes/%s/states/console' % NODE1['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(CONSOLE_DATA_ENABLED, info)

    def test_node_get_console_disabled(self):
        info = self.mgr.get_console(NODE2['uuid'])
        expect = [
            ('GET', '/v1/nodes/%s/states/console' % NODE2['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(CONSOLE_DATA_DISABLED, info)

    @mock.patch.object(node.NodeManager, 'update', autospec=True)
    def test_vendor_passthru_update(self, update_mock):
        # For now just mock the tests because vendor-passthru doesn't return
        # anything to verify.
        vendor_passthru_args = {'arg1': 'val1'}
        kwargs = {
            'node_id': 'node_uuid',
            'method': 'method',
            'args': vendor_passthru_args
            }

        final_path = 'node_uuid/vendor_passthru/method'
        for http_method in ('POST', 'PUT', 'PATCH'):
            kwargs['http_method'] = http_method
            self.mgr.vendor_passthru(**kwargs)
            update_mock.assert_called_once_with(mock.ANY, final_path,
                                                vendor_passthru_args,
                                                http_method=http_method)
            update_mock.reset_mock()

    @mock.patch.object(node.NodeManager, 'get', autospec=True)
    def test_vendor_passthru_get(self, get_mock):
        kwargs = {
            'node_id': 'node_uuid',
            'method': 'method',
            'http_method': 'GET',
            }

        final_path = 'node_uuid/vendor_passthru/method'
        self.mgr.vendor_passthru(**kwargs)
        get_mock.assert_called_once_with(mock.ANY, final_path)

    @mock.patch.object(node.NodeManager, 'delete', autospec=True)
    def test_vendor_passthru_delete(self, delete_mock):
        kwargs = {
            'node_id': 'node_uuid',
            'method': 'method',
            'http_method': 'DELETE',
            }

        final_path = 'node_uuid/vendor_passthru/method'
        self.mgr.vendor_passthru(**kwargs)
        delete_mock.assert_called_once_with(mock.ANY, final_path)

    @mock.patch.object(node.NodeManager, 'delete', autospec=True)
    def test_vendor_passthru_unknown_http_method(self, delete_mock):
        kwargs = {
            'node_id': 'node_uuid',
            'method': 'method',
            'http_method': 'UNKNOWN',
            }
        self.assertRaises(exc.InvalidAttribute, self.mgr.vendor_passthru,
                          **kwargs)

    @mock.patch.object(node.NodeManager, '_list', autospec=True)
    def test_vif_list(self, _list_mock):
        kwargs = {
            'node_ident': NODE1['uuid'],
            }

        final_path = '/v1/nodes/%s/vifs' % NODE1['uuid']
        self.mgr.vif_list(**kwargs)
        _list_mock.assert_called_once_with(mock.ANY, final_path, "vifs")

    @mock.patch.object(node.NodeManager, 'update', autospec=True)
    def test_vif_attach(self, update_mock):
        kwargs = {
            'node_ident': NODE1['uuid'],
            'vif_id': 'vif_id',
            }

        final_path = '%s/vifs' % NODE1['uuid']
        self.mgr.vif_attach(**kwargs)
        update_mock.assert_called_once_with(
            mock.ANY, final_path, {'id': 'vif_id'}, http_method="POST")

    @mock.patch.object(node.NodeManager, 'update', autospec=True)
    def test_vif_attach_custom_fields(self, update_mock):
        kwargs = {
            'node_ident': NODE1['uuid'],
            'vif_id': 'vif_id',
            'foo': 'bar',
            }

        final_path = '%s/vifs' % NODE1['uuid']
        self.mgr.vif_attach(**kwargs)
        update_mock.assert_called_once_with(
            mock.ANY,
            final_path, {'id': 'vif_id', 'foo': 'bar'},
            http_method="POST")

    @mock.patch.object(node.NodeManager, 'update', autospec=True)
    def test_vif_attach_custom_fields_id(self, update_mock):
        kwargs = {
            'node_ident': NODE1['uuid'],
            'vif_id': 'vif_id',
            'id': 'bar',
            }
        self.assertRaises(
            exc.InvalidAttribute,
            self.mgr.vif_attach, **kwargs)

    @mock.patch.object(node.NodeManager, 'delete', autospec=True)
    def test_vif_detach(self, delete_mock):
        kwargs = {
            'node_ident': NODE1['uuid'],
            'vif_id': 'vif_id',
            }

        final_path = '%s/vifs/vif_id' % NODE1['uuid']
        self.mgr.vif_detach(**kwargs)
        delete_mock.assert_called_once_with(mock.ANY, final_path)

    def _test_node_set_boot_device(self, boot_device, persistent=False):
        self.mgr.set_boot_device(NODE1['uuid'], boot_device, persistent)
        body = {'boot_device': boot_device, 'persistent': persistent}
        expect = [
            ('PUT', '/v1/nodes/%s/management/boot_device' % NODE1['uuid'],
             {}, body),
        ]
        self.assertEqual(expect, self.api.calls)

    def test_node_set_boot_device(self):
        self._test_node_set_boot_device('pxe')

    def test_node_set_boot_device_persistent(self):
        self._test_node_set_boot_device('pxe', persistent=True)

    def test_node_get_boot_device(self):
        boot_device = self.mgr.get_boot_device(NODE1['uuid'])
        expect = [
            ('GET', '/v1/nodes/%s/management/boot_device' % NODE1['uuid'],
             {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(BOOT_DEVICE, boot_device)

    def test_node_inject_nmi(self):
        self.mgr.inject_nmi(NODE1['uuid'])
        expect = [
            ('PUT', '/v1/nodes/%s/management/inject_nmi' % NODE1['uuid'],
             {}, {}),
        ]
        self.assertEqual(expect, self.api.calls)

    def test_node_get_supported_boot_devices(self):
        boot_device = self.mgr.get_supported_boot_devices(NODE1['uuid'])
        expect = [
            ('GET', '/v1/nodes/%s/management/boot_device/supported' %
             NODE1['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(SUPPORTED_BOOT_DEVICE, boot_device)

    def test_node_get_vendor_passthru_methods(self):
        vendor_methods = self.mgr.get_vendor_passthru_methods(NODE1['uuid'])
        expect = [
            ('GET', '/v1/nodes/%s/vendor_passthru/methods' % NODE1['uuid'],
             {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NODE_VENDOR_PASSTHRU_METHOD, vendor_methods)

    def _fake_node_for_wait(self, state, error=None, target=None):
        spec = ['provision_state', 'last_error', 'target_provision_state']
        return mock.Mock(provision_state=state,
                         last_error=error,
                         target_provision_state=target,
                         spec=spec)

    @mock.patch.object(time, 'sleep', autospec=True)
    @mock.patch.object(node.NodeManager, 'get', autospec=True)
    def test_wait_for_provision_state(self, mock_get, mock_sleep):
        mock_get.side_effect = [
            self._fake_node_for_wait('deploying', target='active'),
            # Sometimes non-fatal errors can be recorded in last_error
            self._fake_node_for_wait('deploying', target='active',
                                     error='Node locked'),
            self._fake_node_for_wait('active')
        ]

        self.mgr.wait_for_provision_state('node', 'active')

        mock_get.assert_called_with(self.mgr, 'node')
        self.assertEqual(3, mock_get.call_count)
        mock_sleep.assert_called_with(node._DEFAULT_POLL_INTERVAL)
        self.assertEqual(2, mock_sleep.call_count)

    @mock.patch.object(time, 'sleep', autospec=True)
    @mock.patch.object(node.NodeManager, 'get', autospec=True)
    def test_wait_for_provision_state_timeout(self, mock_get, mock_sleep):
        mock_get.return_value = self._fake_node_for_wait(
            'deploying', target='active')

        self.assertRaises(exc.StateTransitionTimeout,
                          self.mgr.wait_for_provision_state, 'node', 'active',
                          timeout=0.001)

    @mock.patch.object(time, 'sleep', autospec=True)
    @mock.patch.object(node.NodeManager, 'get', autospec=True)
    def test_wait_for_provision_state_error(self, mock_get, mock_sleep):
        mock_get.side_effect = [
            self._fake_node_for_wait('deploying', target='active'),
            self._fake_node_for_wait('deploy failed', error='boom'),
        ]

        self.assertRaisesRegex(exc.StateTransitionFailed,
                               'boom',
                               self.mgr.wait_for_provision_state,
                               'node', 'active')

        mock_get.assert_called_with(self.mgr, 'node')
        self.assertEqual(2, mock_get.call_count)
        mock_sleep.assert_called_with(node._DEFAULT_POLL_INTERVAL)
        self.assertEqual(1, mock_sleep.call_count)

    @mock.patch.object(node.NodeManager, 'get', autospec=True)
    def test_wait_for_provision_state_custom_delay(self, mock_get):
        mock_get.side_effect = [
            self._fake_node_for_wait('deploying', target='active'),
            self._fake_node_for_wait('active')
        ]

        delay_mock = mock.Mock()
        self.mgr.wait_for_provision_state('node', 'active',
                                          poll_delay_function=delay_mock)

        mock_get.assert_called_with(self.mgr, 'node')
        self.assertEqual(2, mock_get.call_count)
        delay_mock.assert_called_with(node._DEFAULT_POLL_INTERVAL)
        self.assertEqual(1, delay_mock.call_count)

    def test_wait_for_provision_state_wrong_input(self):
        self.assertRaises(ValueError, self.mgr.wait_for_provision_state,
                          'node', 'active', timeout='42')
        self.assertRaises(ValueError, self.mgr.wait_for_provision_state,
                          'node', 'active', timeout=-1)
        self.assertRaises(TypeError, self.mgr.wait_for_provision_state,
                          'node', 'active', poll_delay_function={})

    @mock.patch.object(time, 'sleep', autospec=True)
    @mock.patch.object(node.NodeManager, 'get', autospec=True)
    def test_wait_for_provision_state_unexpected_stable_state(
            self, mock_get, mock_sleep):
        # This simulates aborted deployment
        mock_get.side_effect = [
            self._fake_node_for_wait('deploying', target='active'),
            self._fake_node_for_wait('available'),
        ]

        self.assertRaisesRegex(exc.StateTransitionFailed,
                               'available',
                               self.mgr.wait_for_provision_state,
                               'node', 'active')

        mock_get.assert_called_with(self.mgr, 'node')
        self.assertEqual(2, mock_get.call_count)
        mock_sleep.assert_called_with(node._DEFAULT_POLL_INTERVAL)
        self.assertEqual(1, mock_sleep.call_count)

    @mock.patch.object(time, 'sleep', autospec=True)
    @mock.patch.object(node.NodeManager, 'get', autospec=True)
    def test_wait_for_provision_state_unexpected_stable_state_allowed(
            self, mock_get, mock_sleep):
        mock_get.side_effect = [
            self._fake_node_for_wait('deploying', target='active'),
            self._fake_node_for_wait('available'),
            self._fake_node_for_wait('deploying', target='active'),
            self._fake_node_for_wait('active'),
        ]

        self.mgr.wait_for_provision_state('node', 'active',
                                          fail_on_unexpected_state=False)

        mock_get.assert_called_with(self.mgr, 'node')
        self.assertEqual(4, mock_get.call_count)
        mock_sleep.assert_called_with(node._DEFAULT_POLL_INTERVAL)
        self.assertEqual(3, mock_sleep.call_count)

    def test_node_get_traits(self):
        traits = self.mgr.get_traits(NODE1['uuid'])
        expect = [
            ('GET', '/v1/nodes/%s/traits' % NODE1['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(TRAITS['traits'], traits)

    def test_node_add_trait(self):
        trait = 'CUSTOM_FOO'
        resp = self.mgr.add_trait(NODE1['uuid'], trait)
        expect = [
            ('PUT', '/v1/nodes/%s/traits/%s' % (NODE1['uuid'], trait),
                {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(resp)

    def test_node_set_traits(self):
        traits = ['CUSTOM_FOO', 'CUSTOM_BAR']
        resp = self.mgr.set_traits(NODE1['uuid'], traits)
        expect = [
            ('PUT', '/v1/nodes/%s/traits' % NODE1['uuid'],
                {}, {'traits': traits}),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(resp)

    def test_node_remove_all_traits(self):
        resp = self.mgr.remove_all_traits(NODE1['uuid'])
        expect = [
            ('DELETE', '/v1/nodes/%s/traits' % NODE1['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(resp)

    def test_node_remove_trait(self):
        trait = 'CUSTOM_FOO'
        resp = self.mgr.remove_trait(NODE1['uuid'], trait)
        expect = [
            ('DELETE', '/v1/nodes/%s/traits/%s' % (NODE1['uuid'], trait),
                {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(resp)
