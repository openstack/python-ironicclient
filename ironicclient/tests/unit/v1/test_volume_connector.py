# Copyright 2015 Hitachi Data Systems
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

import testtools

from ironicclient import exc
from ironicclient.tests.unit import utils
import ironicclient.v1.port

NODE_UUID = '55555555-4444-3333-2222-111111111111'
CONNECTOR1 = {'uuid': '11111111-2222-3333-4444-555555555555',
              'node_uuid': NODE_UUID,
              'type': 'iqn',
              'connector_id': 'iqn.2010-10.org.openstack:test',
              'extra': {}}

CONNECTOR2 = {'uuid': '66666666-7777-8888-9999-000000000000',
              'node_uuid': NODE_UUID,
              'type': 'wwpn',
              'connector_id': '1234567890543216',
              'extra': {}}

CREATE_CONNECTOR = copy.deepcopy(CONNECTOR1)
del CREATE_CONNECTOR['uuid']

CREATE_CONNECTOR_WITH_UUID = copy.deepcopy(CONNECTOR1)

UPDATED_CONNECTOR = copy.deepcopy(CONNECTOR1)
NEW_CONNECTOR_ID = '1234567890123456'
UPDATED_CONNECTOR['connector_id'] = NEW_CONNECTOR_ID

fake_responses = {
    '/v1/volume/connectors':
    {
        'GET': (
            {},
            {"connectors": [CONNECTOR1]},
        ),
        'POST': (
            {},
            CONNECTOR1,
        ),
    },
    '/v1/volume/connectors/?detail=True':
    {
        'GET': (
            {},
            {"connectors": [CONNECTOR1]},
        ),
    },
    '/v1/volume/connectors/?fields=uuid,connector_id':
    {
        'GET': (
            {},
            {"connectors": [CONNECTOR1]},
        ),
    },
    '/v1/volume/connectors/%s' % CONNECTOR1['uuid']:
    {
        'GET': (
            {},
            CONNECTOR1,
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_CONNECTOR,
        ),
    },
    '/v1/volume/connectors/%s?fields=uuid,connector_id' % CONNECTOR1['uuid']:
    {
        'GET': (
            {},
            CONNECTOR1,
        ),
    },
    '/v1/volume/connectors/?detail=True&node=%s' % NODE_UUID:
    {
        'GET': (
            {},
            {"connectors": [CONNECTOR1]},
        ),
    },
    '/v1/volume/connectors/?node=%s' % NODE_UUID:
    {
        'GET': (
            {},
            {"connectors": [CONNECTOR1]},
        ),
    }
}

fake_responses_pagination = {
    '/v1/volume/connectors':
    {
        'GET': (
            {},
            {"connectors": [CONNECTOR1],
             "next": "http://127.0.0.1:6385/v1/volume/connectors/?marker=%s" %
                     CONNECTOR1['uuid']}
        ),
    },
    '/v1/volume/connectors/?limit=1':
    {
        'GET': (
            {},
            {"connectors": [CONNECTOR1],
             "next": "http://127.0.0.1:6385/v1/volume/connectors/?limit=1"
                     "&marker=%s" % CONNECTOR1['uuid']}
        ),
    },
    '/v1/volume/connectors/?limit=1&marker=%s' % CONNECTOR1['uuid']:
    {
        'GET': (
            {},
            {"connectors": [CONNECTOR2]}
        ),
    },
    '/v1/volume/connectors/?marker=%s' % CONNECTOR1['uuid']:
    {
        'GET': (
            {},
            {"connectors": [CONNECTOR2]}
        ),
    },
}

fake_responses_sorting = {
    '/v1/volume/connectors/?sort_key=updated_at':
    {
        'GET': (
            {},
            {"connectors": [CONNECTOR2, CONNECTOR1]}
        ),
    },
    '/v1/volume/connectors/?sort_dir=desc':
    {
        'GET': (
            {},
            {"connectors": [CONNECTOR2, CONNECTOR1]}
        ),
    },
}


class VolumeConnectorManagerTestBase(testtools.TestCase):

    def _validate_obj(self, expect, obj):
        self.assertEqual(expect['uuid'], obj.uuid)
        self.assertEqual(expect['type'], obj.type)
        self.assertEqual(expect['connector_id'], obj.connector_id)
        self.assertEqual(expect['node_uuid'], obj.node_uuid)

    def _validate_list(self, expect_request,
                       expect_connectors, actual_connectors):
        self.assertEqual(expect_request, self.api.calls)
        self.assertEqual(len(expect_connectors), len(actual_connectors))
        for expect, obj in zip(expect_connectors, actual_connectors):
            self._validate_obj(expect, obj)


class VolumeConnectorManagerTest(VolumeConnectorManagerTestBase):

    def setUp(self):
        super(VolumeConnectorManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = ironicclient.v1.volume_connector.VolumeConnectorManager(
            self.api)

    def test_volume_connectors_list(self):
        volume_connectors = self.mgr.list()
        expect = [
            ('GET', '/v1/volume/connectors', {}, None),
        ]
        expect_connectors = [CONNECTOR1]
        self._validate_list(expect, expect_connectors, volume_connectors)

    def test_volume_connectors_list_by_node(self):
        volume_connectors = self.mgr.list(node=NODE_UUID)
        expect = [
            ('GET', '/v1/volume/connectors/?node=%s' % NODE_UUID, {}, None),
        ]
        expect_connectors = [CONNECTOR1]
        self._validate_list(expect, expect_connectors, volume_connectors)

    def test_volume_connectors_list_by_node_detail(self):
        volume_connectors = self.mgr.list(node=NODE_UUID, detail=True)
        expect = [
            ('GET', '/v1/volume/connectors/?detail=True&node=%s' % NODE_UUID,
             {}, None),
        ]
        expect_connectors = [CONNECTOR1]
        self._validate_list(expect, expect_connectors, volume_connectors)

    def test_volume_connectors_list_detail(self):
        volume_connectors = self.mgr.list(detail=True)
        expect = [
            ('GET', '/v1/volume/connectors/?detail=True', {}, None),
        ]
        expect_connectors = [CONNECTOR1]
        self._validate_list(expect, expect_connectors, volume_connectors)

    def test_volume_connector_list_fields(self):
        volume_connectors = self.mgr.list(fields=['uuid', 'connector_id'])
        expect = [
            ('GET',
             '/v1/volume/connectors/?fields=uuid,connector_id',
             {},
             None),
        ]
        expect_connectors = [CONNECTOR1]
        self._validate_list(expect, expect_connectors, volume_connectors)

    def test_volume_connector_list_detail_and_fields_fail(self):
        self.assertRaises(exc.InvalidAttribute, self.mgr.list,
                          detail=True, fields=['uuid', 'connector_id'])

    def test_volume_connectors_show(self):
        volume_connector = self.mgr.get(CONNECTOR1['uuid'])
        expect = [
            ('GET', '/v1/volume/connectors/%s' % CONNECTOR1['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self._validate_obj(CONNECTOR1, volume_connector)

    def test_volume_connector_show_fields(self):
        volume_connector = self.mgr.get(CONNECTOR1['uuid'],
                                        fields=['uuid', 'connector_id'])
        expect = [
            ('GET', '/v1/volume/connectors/%s?fields=uuid,connector_id' %
             CONNECTOR1['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(CONNECTOR1['uuid'], volume_connector.uuid)
        self.assertEqual(CONNECTOR1['connector_id'],
                         volume_connector.connector_id)

    def test_create(self):
        volume_connector = self.mgr.create(**CREATE_CONNECTOR)
        expect = [
            ('POST', '/v1/volume/connectors', {}, CREATE_CONNECTOR),
        ]
        self.assertEqual(expect, self.api.calls)
        self._validate_obj(CONNECTOR1, volume_connector)

    def test_create_with_uuid(self):
        volume_connector = self.mgr.create(**CREATE_CONNECTOR_WITH_UUID)
        expect = [
            ('POST', '/v1/volume/connectors', {}, CREATE_CONNECTOR_WITH_UUID),
        ]
        self.assertEqual(expect, self.api.calls)
        self._validate_obj(CREATE_CONNECTOR_WITH_UUID, volume_connector)

    def test_delete(self):
        volume_connector = self.mgr.delete(CONNECTOR1['uuid'])
        expect = [
            ('DELETE', '/v1/volume/connectors/%s' % CONNECTOR1['uuid'],
             {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(volume_connector)

    def test_update(self):
        patch = {'op': 'replace',
                 'connector_id': NEW_CONNECTOR_ID,
                 'path': '/connector_id'}
        volume_connector = self.mgr.update(
            volume_connector_id=CONNECTOR1['uuid'], patch=patch)
        expect = [
            ('PATCH', '/v1/volume/connectors/%s' % CONNECTOR1['uuid'],
             {}, patch),
        ]
        self.assertEqual(expect, self.api.calls)
        self._validate_obj(UPDATED_CONNECTOR, volume_connector)


class VolumeConnectorManagerPaginationTest(VolumeConnectorManagerTestBase):

    def setUp(self):
        super(VolumeConnectorManagerPaginationTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = ironicclient.v1.volume_connector.VolumeConnectorManager(
            self.api)

    def test_volume_connectors_list_limit(self):
        volume_connectors = self.mgr.list(limit=1)
        expect = [
            ('GET', '/v1/volume/connectors/?limit=1', {}, None),
        ]
        expect_connectors = [CONNECTOR1]
        self._validate_list(expect, expect_connectors, volume_connectors)

    def test_volume_connectors_list_marker(self):
        volume_connectors = self.mgr.list(marker=CONNECTOR1['uuid'])
        expect = [
            ('GET', '/v1/volume/connectors/?marker=%s' % CONNECTOR1['uuid'],
             {}, None),
        ]
        expect_connectors = [CONNECTOR2]
        self._validate_list(expect, expect_connectors, volume_connectors)

    def test_volume_connectors_list_pagination_no_limit(self):
        volume_connectors = self.mgr.list(limit=0)
        expect = [
            ('GET', '/v1/volume/connectors', {}, None),
            ('GET', '/v1/volume/connectors/?marker=%s' % CONNECTOR1['uuid'],
             {}, None)
        ]
        expect_connectors = [CONNECTOR1, CONNECTOR2]
        self._validate_list(expect, expect_connectors, volume_connectors)


class VolumeConnectorManagerSortingTest(VolumeConnectorManagerTestBase):

    def setUp(self):
        super(VolumeConnectorManagerSortingTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = ironicclient.v1.volume_connector.VolumeConnectorManager(
            self.api)

    def test_volume_connectors_list_sort_key(self):
        volume_connectors = self.mgr.list(sort_key='updated_at')
        expect = [
            ('GET', '/v1/volume/connectors/?sort_key=updated_at', {}, None)
        ]
        expect_connectors = [CONNECTOR2, CONNECTOR1]
        self._validate_list(expect, expect_connectors, volume_connectors)

    def test_volume_connectors_list_sort_dir(self):
        volume_connectors = self.mgr.list(sort_dir='desc')
        expect = [
            ('GET', '/v1/volume/connectors/?sort_dir=desc', {}, None)
        ]
        expect_connectors = [CONNECTOR2, CONNECTOR1]
        self._validate_list(expect, expect_connectors, volume_connectors)
