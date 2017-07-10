# Copyright 2016 Hitachi, Ltd.
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
TARGET1 = {'uuid': '11111111-2222-3333-4444-555555555555',
           'node_uuid': NODE_UUID,
           'volume_type': 'iscsi',
           'properties': {'target_iqn': 'iqn.foo'},
           'boot_index': 0,
           'volume_id': '12345678',
           'extra': {}}

TARGET2 = {'uuid': '66666666-7777-8888-9999-000000000000',
           'node_uuid': NODE_UUID,
           'volume_type': 'fibre_channel',
           'properties': {'target_wwn': 'foobar'},
           'boot_index': 1,
           'volume_id': '87654321',
           'extra': {}}

CREATE_TARGET = copy.deepcopy(TARGET1)
del CREATE_TARGET['uuid']

CREATE_TARGET_WITH_UUID = copy.deepcopy(TARGET1)

UPDATED_TARGET = copy.deepcopy(TARGET1)
NEW_VALUE = '100'
UPDATED_TARGET['boot_index'] = NEW_VALUE

fake_responses = {
    '/v1/volume/targets':
    {
        'GET': (
            {},
            {"targets": [TARGET1]},
        ),
        'POST': (
            {},
            TARGET1
        ),
    },
    '/v1/volume/targets/?detail=True':
    {
        'GET': (
            {},
            {"targets": [TARGET1]},
        ),
    },
    '/v1/volume/targets/?fields=uuid,boot_index':
    {
        'GET': (
            {},
            {"targets": [TARGET1]},
        ),
    },
    '/v1/volume/targets/%s' % TARGET1['uuid']:
    {
        'GET': (
            {},
            TARGET1,
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_TARGET,
        ),
    },
    '/v1/volume/targets/%s?fields=uuid,boot_index' % TARGET1['uuid']:
    {
        'GET': (
            {},
            TARGET1,
        ),
    },
    '/v1/volume/targets/?detail=True&node=%s' % NODE_UUID:
    {
        'GET': (
            {},
            {"targets": [TARGET1]},
        ),
    },
    '/v1/volume/targets/?node=%s' % NODE_UUID:
    {
        'GET': (
            {},
            {"targets": [TARGET1]},
        ),
    }
}

fake_responses_pagination = {
    '/v1/volume/targets':
    {
        'GET': (
            {},
            {"targets": [TARGET1],
             "next": "http://127.0.0.1:6385/v1/volume/targets/?marker=%s" %
             TARGET1['uuid']}
        ),
    },
    '/v1/volume/targets/?limit=1':
    {
        'GET': (
            {},
            {"targets": [TARGET1],
             "next": "http://127.0.0.1:6385/v1/volume/targets/?limit=1"
                     "&marker=%s" % TARGET1['uuid']}
        ),
    },
    '/v1/volume/targets/?limit=1&marker=%s' % TARGET1['uuid']:
    {
        'GET': (
            {},
            {"targets": [TARGET2]}
        ),
    },
    '/v1/volume/targets/?marker=%s' % TARGET1['uuid']:
    {
        'GET': (
            {},
            {"targets": [TARGET2]}
        ),
    },
}

fake_responses_sorting = {
    '/v1/volume/targets/?sort_key=updated_at':
    {
        'GET': (
            {},
            {"targets": [TARGET2, TARGET1]}
        ),
    },
    '/v1/volume/targets/?sort_dir=desc':
    {
        'GET': (
            {},
            {"targets": [TARGET2, TARGET1]}
        ),
    },
}


class VolumeTargetManagerTestBase(testtools.TestCase):

    def _validate_obj(self, expect, obj):
        self.assertEqual(expect['uuid'], obj.uuid)
        self.assertEqual(expect['volume_type'], obj.volume_type)
        self.assertEqual(expect['boot_index'], obj.boot_index)
        self.assertEqual(expect['volume_id'], obj.volume_id)
        self.assertEqual(expect['node_uuid'], obj.node_uuid)

    def _validate_list(self, expect_request,
                       expect_targets, actual_targets):
        self.assertEqual(expect_request, self.api.calls)
        self.assertEqual(len(expect_targets), len(actual_targets))
        for expect, obj in zip(expect_targets, actual_targets):
            self._validate_obj(expect, obj)


class VolumeTargetManagerTest(VolumeTargetManagerTestBase):

    def setUp(self):
        super(VolumeTargetManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = ironicclient.v1.volume_target.VolumeTargetManager(self.api)

    def test_volume_targets_list(self):
        volume_targets = self.mgr.list()
        expect = [
            ('GET', '/v1/volume/targets', {}, None),
        ]
        expect_targets = [TARGET1]
        self._validate_list(expect, expect_targets, volume_targets)

    def test_volume_targets_list_by_node(self):
        volume_targets = self.mgr.list(node=NODE_UUID)
        expect = [
            ('GET', '/v1/volume/targets/?node=%s' % NODE_UUID, {}, None),
        ]
        expect_targets = [TARGET1]
        self._validate_list(expect, expect_targets, volume_targets)

    def test_volume_targets_list_by_node_detail(self):
        volume_targets = self.mgr.list(node=NODE_UUID, detail=True)
        expect = [
            ('GET', '/v1/volume/targets/?detail=True&node=%s' % NODE_UUID,
             {}, None),
        ]
        expect_targets = [TARGET1]
        self._validate_list(expect, expect_targets, volume_targets)

    def test_volume_targets_list_detail(self):
        volume_targets = self.mgr.list(detail=True)
        expect = [
            ('GET', '/v1/volume/targets/?detail=True', {}, None),
        ]
        expect_targets = [TARGET1]
        self._validate_list(expect, expect_targets, volume_targets)

    def test_volume_target_list_fields(self):
        volume_targets = self.mgr.list(fields=['uuid', 'boot_index'])
        expect = [
            ('GET', '/v1/volume/targets/?fields=uuid,boot_index', {}, None),
        ]
        expect_targets = [TARGET1]
        self._validate_list(expect, expect_targets, volume_targets)

    def test_volume_target_list_detail_and_fields_fail(self):
        self.assertRaises(exc.InvalidAttribute, self.mgr.list,
                          detail=True, fields=['uuid', 'boot_index'])

    def test_volume_targets_show(self):
        volume_target = self.mgr.get(TARGET1['uuid'])
        expect = [
            ('GET', '/v1/volume/targets/%s' % TARGET1['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self._validate_obj(TARGET1, volume_target)

    def test_volume_target_show_fields(self):
        volume_target = self.mgr.get(TARGET1['uuid'],
                                     fields=['uuid', 'boot_index'])
        expect = [
            ('GET', '/v1/volume/targets/%s?fields=uuid,boot_index' %
             TARGET1['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(TARGET1['uuid'], volume_target.uuid)
        self.assertEqual(TARGET1['boot_index'], volume_target.boot_index)

    def test_create(self):
        volume_target = self.mgr.create(**CREATE_TARGET)
        expect = [
            ('POST', '/v1/volume/targets', {}, CREATE_TARGET),
        ]
        self.assertEqual(expect, self.api.calls)
        self._validate_obj(TARGET1, volume_target)

    def test_create_with_uuid(self):
        volume_target = self.mgr.create(**CREATE_TARGET_WITH_UUID)
        expect = [
            ('POST', '/v1/volume/targets', {}, CREATE_TARGET_WITH_UUID),
        ]
        self.assertEqual(expect, self.api.calls)
        self._validate_obj(TARGET1, volume_target)

    def test_delete(self):
        volume_target = self.mgr.delete(TARGET1['uuid'])
        expect = [
            ('DELETE', '/v1/volume/targets/%s' % TARGET1['uuid'],
             {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(volume_target)

    def test_update(self):
        patch = {'op': 'replace',
                 'value': NEW_VALUE,
                 'path': '/boot_index'}
        volume_target = self.mgr.update(
            volume_target_id=TARGET1['uuid'], patch=patch)
        expect = [
            ('PATCH', '/v1/volume/targets/%s' % TARGET1['uuid'],
             {}, patch),
        ]
        self.assertEqual(expect, self.api.calls)
        self._validate_obj(UPDATED_TARGET, volume_target)


class VolumeTargetManagerPaginationTest(VolumeTargetManagerTestBase):

    def setUp(self):
        super(VolumeTargetManagerPaginationTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = ironicclient.v1.volume_target.VolumeTargetManager(self.api)

    def test_volume_targets_list_limit(self):
        volume_targets = self.mgr.list(limit=1)
        expect = [
            ('GET', '/v1/volume/targets/?limit=1', {}, None),
        ]
        expect_targets = [TARGET1]
        self._validate_list(expect, expect_targets, volume_targets)

    def test_volume_targets_list_marker(self):
        volume_targets = self.mgr.list(marker=TARGET1['uuid'])
        expect = [
            ('GET', '/v1/volume/targets/?marker=%s' % TARGET1['uuid'],
             {}, None),
        ]
        expect_targets = [TARGET2]
        self._validate_list(expect, expect_targets, volume_targets)

    def test_volume_targets_list_pagination_no_limit(self):
        volume_targets = self.mgr.list(limit=0)
        expect = [
            ('GET', '/v1/volume/targets', {}, None),
            ('GET', '/v1/volume/targets/?marker=%s' % TARGET1['uuid'],
             {}, None)
        ]
        expect_targets = [TARGET1, TARGET2]
        self._validate_list(expect, expect_targets, volume_targets)


class VolumeTargetManagerSortingTest(VolumeTargetManagerTestBase):

    def setUp(self):
        super(VolumeTargetManagerSortingTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = ironicclient.v1.volume_target.VolumeTargetManager(self.api)

    def test_volume_targets_list_sort_key(self):
        volume_targets = self.mgr.list(sort_key='updated_at')
        expect = [
            ('GET', '/v1/volume/targets/?sort_key=updated_at', {}, None)
        ]
        expect_targets = [TARGET2, TARGET1]
        self._validate_list(expect, expect_targets, volume_targets)

    def test_volume_targets_list_sort_dir(self):
        volume_targets = self.mgr.list(sort_dir='desc')
        expect = [
            ('GET', '/v1/volume/targets/?sort_dir=desc', {}, None)
        ]
        expect_targets = [TARGET2, TARGET1]
        self._validate_list(expect, expect_targets, volume_targets)
