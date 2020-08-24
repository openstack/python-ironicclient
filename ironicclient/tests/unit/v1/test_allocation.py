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
from unittest import mock

import testtools

from ironicclient import exc
from ironicclient.tests.unit import utils
import ironicclient.v1.allocation

ALLOCATION = {'uuid': '11111111-2222-3333-4444-555555555555',
              'name': 'Allocation-name',
              'owner': None,
              'state': 'active',
              'node_uuid': '66666666-7777-8888-9999-000000000000',
              'last_error': None,
              'resource_class': 'baremetal',
              'traits': [],
              'candidate_nodes': [],
              'extra': {}}

ALLOCATION2 = {'uuid': '55555555-4444-3333-2222-111111111111',
               'name': 'Allocation2-name',
               'owner': 'fake-owner',
               'state': 'allocating',
               'node_uuid': None,
               'last_error': None,
               'resource_class': 'baremetal',
               'traits': [],
               'candidate_nodes': [],
               'extra': {}}

CREATE_ALLOCATION = copy.deepcopy(ALLOCATION)
for field in ('state', 'node_uuid', 'last_error'):
    del CREATE_ALLOCATION[field]

fake_responses = {
    '/v1/allocations':
    {
        'GET': (
            {},
            {"allocations": [ALLOCATION, ALLOCATION2]},
        ),
        'POST': (
            {},
            CREATE_ALLOCATION,
        ),
    },
    '/v1/allocations/%s' % ALLOCATION['uuid']:
    {
        'GET': (
            {},
            ALLOCATION,
        ),
        'DELETE': (
            {},
            None,
        ),
    },
    '/v1/allocations/?node=%s' % ALLOCATION['node_uuid']:
    {
        'GET': (
            {},
            {"allocations": [ALLOCATION]},
        ),
    },
    '/v1/allocations/?owner=%s' % ALLOCATION2['owner']:
    {
        'GET': (
            {},
            {"allocations": [ALLOCATION2]},
        ),
    },
}

fake_responses_pagination = {
    '/v1/allocations':
    {
        'GET': (
            {},
            {"allocations": [ALLOCATION],
             "next": "http://127.0.0.1:6385/v1/allocations/?limit=1"}
        ),
    },
    '/v1/allocations/?limit=1':
    {
        'GET': (
            {},
            {"allocations": [ALLOCATION2]}
        ),
    },
    '/v1/allocations/?marker=%s' % ALLOCATION['uuid']:
    {
        'GET': (
            {},
            {"allocations": [ALLOCATION2]}
        ),
    },
}

fake_responses_sorting = {
    '/v1/allocations/?sort_key=updated_at':
    {
        'GET': (
            {},
            {"allocations": [ALLOCATION2, ALLOCATION]}
        ),
    },
    '/v1/allocations/?sort_dir=desc':
    {
        'GET': (
            {},
            {"allocations": [ALLOCATION2, ALLOCATION]}
        ),
    },
}


class AllocationManagerTest(testtools.TestCase):

    def setUp(self):
        super(AllocationManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = ironicclient.v1.allocation.AllocationManager(self.api)

    def test_allocations_list(self):
        allocations = self.mgr.list()
        expect = [
            ('GET', '/v1/allocations', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(allocations))

        expected_resp = ({}, {"allocations": [ALLOCATION, ALLOCATION2]},)
        self.assertEqual(expected_resp,
                         self.api.responses['/v1/allocations']['GET'])

    def test_allocations_list_by_node(self):
        allocations = self.mgr.list(node=ALLOCATION['node_uuid'])
        expect = [
            ('GET', '/v1/allocations/?node=%s' % ALLOCATION['node_uuid'], {},
             None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(allocations))

        expected_resp = ({}, {"allocations": [ALLOCATION, ALLOCATION2]},)
        self.assertEqual(expected_resp,
                         self.api.responses['/v1/allocations']['GET'])

    def test_allocations_list_by_owner(self):
        allocations = self.mgr.list(owner=ALLOCATION2['owner'])
        expect = [
            ('GET', '/v1/allocations/?owner=%s' % ALLOCATION2['owner'], {},
             None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(allocations))

        expected_resp = ({}, {"allocations": [ALLOCATION, ALLOCATION2]},)
        self.assertEqual(expected_resp,
                         self.api.responses['/v1/allocations']['GET'])

    def test_allocations_show(self):
        allocation = self.mgr.get(ALLOCATION['uuid'])
        expect = [
            ('GET', '/v1/allocations/%s' % ALLOCATION['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(ALLOCATION['uuid'], allocation.uuid)
        self.assertEqual(ALLOCATION['name'], allocation.name)
        self.assertEqual(ALLOCATION['owner'], allocation.owner)
        self.assertEqual(ALLOCATION['node_uuid'], allocation.node_uuid)
        self.assertEqual(ALLOCATION['state'], allocation.state)
        self.assertEqual(ALLOCATION['resource_class'],
                         allocation.resource_class)

        expected_resp = ({}, ALLOCATION,)
        self.assertEqual(
            expected_resp,
            self.api.responses['/v1/allocations/%s'
                               % ALLOCATION['uuid']]['GET'])

    def test_create(self):
        allocation = self.mgr.create(**CREATE_ALLOCATION)
        expect = [
            ('POST', '/v1/allocations', {}, CREATE_ALLOCATION),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(allocation)

        self.assertIn(
            ALLOCATION,
            self.api.responses['/v1/allocations']['GET'][1]['allocations'])

    def test_delete(self):
        allocation = self.mgr.delete(allocation_id=ALLOCATION['uuid'])
        expect = [
            ('DELETE', '/v1/allocations/%s' % ALLOCATION['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(allocation)

        expected_resp = ({}, ALLOCATION,)
        self.assertEqual(
            expected_resp,
            self.api.responses['/v1/allocations/%s'
                               % ALLOCATION['uuid']]['GET'])


class AllocationManagerPaginationTest(testtools.TestCase):

    def setUp(self):
        super(AllocationManagerPaginationTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = ironicclient.v1.allocation.AllocationManager(self.api)

    def test_allocations_list_limit(self):
        allocations = self.mgr.list(limit=1)
        expect = [
            ('GET', '/v1/allocations/?limit=1', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(allocations))

        expected_resp = (
            {}, {"next": "http://127.0.0.1:6385/v1/allocations/?limit=1",
                 "allocations": [ALLOCATION]},)
        self.assertEqual(expected_resp,
                         self.api.responses['/v1/allocations']['GET'])

    def test_allocations_list_marker(self):
        allocations = self.mgr.list(marker=ALLOCATION['uuid'])
        expect = [
            ('GET', '/v1/allocations/?marker=%s' % ALLOCATION['uuid'],
             {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(allocations))

        expected_resp = (
            {}, {"next": "http://127.0.0.1:6385/v1/allocations/?limit=1",
                 "allocations": [ALLOCATION]},)
        self.assertEqual(expected_resp,
                         self.api.responses['/v1/allocations']['GET'])

    def test_allocations_list_pagination_no_limit(self):
        allocations = self.mgr.list(limit=0)
        expect = [
            ('GET', '/v1/allocations', {}, None),
            ('GET', '/v1/allocations/?limit=1', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(allocations))

        expected_resp = (
            {}, {"next": "http://127.0.0.1:6385/v1/allocations/?limit=1",
                 "allocations": [ALLOCATION]},)
        self.assertEqual(expected_resp,
                         self.api.responses['/v1/allocations']['GET'])


class AllocationManagerSortingTest(testtools.TestCase):

    def setUp(self):
        super(AllocationManagerSortingTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = ironicclient.v1.allocation.AllocationManager(self.api)

    def test_allocations_list_sort_key(self):
        allocations = self.mgr.list(sort_key='updated_at')
        expect = [
            ('GET', '/v1/allocations/?sort_key=updated_at', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(allocations))

        expected_resp = ({}, {"allocations": [ALLOCATION2, ALLOCATION]},)
        self.assertEqual(
            expected_resp,
            self.api.responses['/v1/allocations/?sort_key=updated_at']['GET'])

    def test_allocations_list_sort_dir(self):
        allocations = self.mgr.list(sort_dir='desc')
        expect = [
            ('GET', '/v1/allocations/?sort_dir=desc', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(allocations))

        expected_resp = ({}, {"allocations": [ALLOCATION2, ALLOCATION]},)
        self.assertEqual(
            expected_resp,
            self.api.responses['/v1/allocations/?sort_dir=desc']['GET'])


@mock.patch('time.sleep', autospec=True)
@mock.patch('ironicclient.v1.allocation.AllocationManager.get', autospec=True)
class AllocationWaitTest(testtools.TestCase):

    def setUp(self):
        super(AllocationWaitTest, self).setUp()
        self.mgr = ironicclient.v1.allocation.AllocationManager(mock.Mock())

    def _fake_allocation(self, state, error=None):
        return mock.Mock(state=state, last_error=error)

    def test_success(self, mock_get, mock_sleep):
        allocations = [
            self._fake_allocation('allocating'),
            self._fake_allocation('allocating'),
            self._fake_allocation('active'),
        ]
        mock_get.side_effect = allocations

        result = self.mgr.wait('alloc1')
        self.assertIs(result, allocations[2])
        self.assertEqual(3, mock_get.call_count)
        self.assertEqual(2, mock_sleep.call_count)
        mock_get.assert_called_with(
            self.mgr, 'alloc1', os_ironic_api_version=None,
            global_request_id=None)

    def test_error(self, mock_get, mock_sleep):
        allocations = [
            self._fake_allocation('allocating'),
            self._fake_allocation('error'),
        ]
        mock_get.side_effect = allocations

        self.assertRaises(exc.StateTransitionFailed,
                          self.mgr.wait, 'alloc1')

        self.assertEqual(2, mock_get.call_count)
        self.assertEqual(1, mock_sleep.call_count)
        mock_get.assert_called_with(
            self.mgr, 'alloc1', os_ironic_api_version=None,
            global_request_id=None)

    def test_timeout(self, mock_get, mock_sleep):
        mock_get.return_value = self._fake_allocation('allocating')

        self.assertRaises(exc.StateTransitionTimeout,
                          self.mgr.wait, 'alloc1', timeout=0.001)

        mock_get.assert_called_with(
            self.mgr, 'alloc1', os_ironic_api_version=None,
            global_request_id=None)
