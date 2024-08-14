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

import testtools
from testtools.matchers import HasLength

from ironicclient import exc
from ironicclient.tests.unit import utils
import ironicclient.v1.runbook

RUNBOOK = {'uuid': '11111111-2222-3333-4444-555555555555',
           'name': 'CUSTOM_RUNBOOK',
           'steps': {},
           'extra': {}}

RUNBOOK2 = {'uuid': '55555555-4444-3333-2222-111111111111',
            'name': 'CUSTOM_RUNBOOK2',
            'steps': {},
            'extra': {}}

CREATE_RUNBOOK = copy.deepcopy(RUNBOOK)
del CREATE_RUNBOOK['uuid']

CREATE_RUNBOOK_WITH_UUID = copy.deepcopy(RUNBOOK)

UPDATED_RUNBOOK = copy.deepcopy(RUNBOOK)
NEW_NAME = 'CUSTOM_RUNBOOK3'
UPDATED_RUNBOOK['name'] = NEW_NAME

fake_responses = {
    '/v1/runbooks':
    {
        'GET': (
            {},
            {"runbooks": [RUNBOOK]},
        ),
        'POST': (
            {},
            CREATE_RUNBOOK,
        ),
    },
    '/v1/runbooks/?detail=True':
    {
        'GET': (
            {},
            {"runbooks": [RUNBOOK]},
        ),
    },
    '/v1/runbooks/?fields=uuid,name':
    {
        'GET': (
            {},
            {"runbooks": [RUNBOOK]},
        ),
    },
    '/v1/runbooks/%s' % RUNBOOK['uuid']:
    {
        'GET': (
            {},
            RUNBOOK,
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_RUNBOOK,
        ),
    },
    '/v1/runbooks/%s?fields=uuid,name' % RUNBOOK['uuid']:
    {
        'GET': (
            {},
            RUNBOOK,
        ),
    },
}

fake_responses_pagination = {
    '/v1/runbooks':
    {
        'GET': (
            {},
            {"runbooks": [RUNBOOK],
             "next": "http://127.0.0.1:6385/v1/runbooks/?limit=1"}
        ),
    },
    '/v1/runbooks/?limit=1':
    {
        'GET': (
            {},
            {"runbooks": [RUNBOOK2]}
        ),
    },
    '/v1/runbooks/?marker=%s' % RUNBOOK['uuid']:
    {
        'GET': (
            {},
            {"runbooks": [RUNBOOK2]}
        ),
    },
}

fake_responses_sorting = {
    '/v1/runbooks/?sort_key=updated_at':
    {
        'GET': (
            {},
            {"runbooks": [RUNBOOK2, RUNBOOK]}
        ),
    },
    '/v1/runbooks/?sort_dir=desc':
    {
        'GET': (
            {},
            {"runbooks": [RUNBOOK2, RUNBOOK]}
        ),
    },
}


class RunbookManagerTest(testtools.TestCase):

    def setUp(self):
        super(RunbookManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = ironicclient.v1.runbook.RunbookManager(
            self.api)

    def test_runbooks_list(self):
        runbooks = self.mgr.list()
        expect = [
            ('GET', '/v1/runbooks', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(runbooks))

    def test_runbooks_list_detail(self):
        runbooks = self.mgr.list(detail=True)
        expect = [
            ('GET', '/v1/runbooks/?detail=True', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(runbooks))

    def test_runbook_list_fields(self):
        runbooks = self.mgr.list(fields=['uuid', 'name'])
        expect = [
            ('GET', '/v1/runbooks/?fields=uuid,name', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(runbooks))

    def test_runbook_list_detail_and_fields_fail(self):
        self.assertRaises(exc.InvalidAttribute, self.mgr.list,
                          detail=True, fields=['uuid', 'name'])

    def test_runbooks_list_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = ironicclient.v1.runbook.RunbookManager(
            self.api)
        runbooks = self.mgr.list(limit=1)
        expect = [
            ('GET', '/v1/runbooks/?limit=1', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(runbooks, HasLength(1))

    def test_runbooks_list_marker(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = ironicclient.v1.runbook.RunbookManager(
            self.api)
        runbooks = self.mgr.list(marker=RUNBOOK['uuid'])
        expect = [
            ('GET',
             '/v1/runbooks/?marker=%s' % RUNBOOK['uuid'], {},
             None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(runbooks, HasLength(1))

    def test_runbooks_list_pagination_no_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = ironicclient.v1.runbook.RunbookManager(
            self.api)
        runbooks = self.mgr.list(limit=0)
        expect = [
            ('GET', '/v1/runbooks', {}, None),
            ('GET', '/v1/runbooks/?limit=1', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(runbooks, HasLength(2))

    def test_runbooks_list_sort_key(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = ironicclient.v1.runbook.RunbookManager(
            self.api)
        runbooks = self.mgr.list(sort_key='updated_at')
        expect = [
            ('GET', '/v1/runbooks/?sort_key=updated_at', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(runbooks))

    def test_runbooks_list_sort_dir(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = ironicclient.v1.runbook.RunbookManager(
            self.api)
        runbooks = self.mgr.list(sort_dir='desc')
        expect = [
            ('GET', '/v1/runbooks/?sort_dir=desc', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(runbooks))

    def test_runbooks_show(self):
        runbook = self.mgr.get(RUNBOOK['uuid'])
        expect = [
            ('GET', '/v1/runbooks/%s' % RUNBOOK['uuid'], {},
             None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(RUNBOOK['uuid'], runbook.uuid)
        self.assertEqual(RUNBOOK['name'], runbook.name)
        self.assertEqual(RUNBOOK['steps'], runbook.steps)
        self.assertEqual(RUNBOOK['extra'], runbook.extra)

    def test_runbook_show_fields(self):
        runbook = self.mgr.get(RUNBOOK['uuid'],
                               fields=['uuid', 'name'])
        expect = [
            ('GET', '/v1/runbooks/%s?fields=uuid,name' %
             RUNBOOK['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(RUNBOOK['uuid'], runbook.uuid)
        self.assertEqual(RUNBOOK['name'], runbook.name)

    def test_create(self):
        runbook = self.mgr.create(**CREATE_RUNBOOK)
        expect = [
            ('POST', '/v1/runbooks', {}, CREATE_RUNBOOK),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(runbook)

    def test_create_with_uuid(self):
        runbook = self.mgr.create(**CREATE_RUNBOOK_WITH_UUID)
        expect = [
            ('POST', '/v1/runbooks', {},
             CREATE_RUNBOOK_WITH_UUID),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(runbook)

    def test_delete(self):
        runbook = self.mgr.delete(
            runbook_id=RUNBOOK['uuid'])
        expect = [
            ('DELETE', '/v1/runbooks/%s' % RUNBOOK['uuid'], {},
             None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(runbook)

    def test_update(self):
        patch = {'op': 'replace',
                 'value': NEW_NAME,
                 'path': '/name'}
        runbook = self.mgr.update(
            runbook_id=RUNBOOK['uuid'], patch=patch)
        expect = [
            ('PATCH', '/v1/runbooks/%s' % RUNBOOK['uuid'],
             {}, patch),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NEW_NAME, runbook.name)
