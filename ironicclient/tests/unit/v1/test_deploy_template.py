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
import ironicclient.v1.deploy_template

DEPLOY_TEMPLATE = {'uuid': '11111111-2222-3333-4444-555555555555',
                   'name': 'fake-template',
                   'steps': {},
                   'extra': {}}

DEPLOY_TEMPLATE2 = {'uuid': '55555555-4444-3333-2222-111111111111',
                    'name': 'fake-template2',
                    'steps': {},
                    'extra': {}}

CREATE_DEPLOY_TEMPLATE = copy.deepcopy(DEPLOY_TEMPLATE)
del CREATE_DEPLOY_TEMPLATE['uuid']

CREATE_DEPLOY_TEMPLATE_WITH_UUID = copy.deepcopy(DEPLOY_TEMPLATE)

UPDATED_DEPLOY_TEMPLATE = copy.deepcopy(DEPLOY_TEMPLATE)
NEW_NAME = 'fake-template3'
UPDATED_DEPLOY_TEMPLATE['name'] = NEW_NAME

fake_responses = {
    '/v1/deploy_templates':
    {
        'GET': (
            {},
            {"deploy_templates": [DEPLOY_TEMPLATE]},
        ),
        'POST': (
            {},
            CREATE_DEPLOY_TEMPLATE,
        ),
    },
    '/v1/deploy_templates/?detail=True':
    {
        'GET': (
            {},
            {"deploy_templates": [DEPLOY_TEMPLATE]},
        ),
    },
    '/v1/deploy_templates/?fields=uuid,name':
    {
        'GET': (
            {},
            {"deploy_templates": [DEPLOY_TEMPLATE]},
        ),
    },
    '/v1/deploy_templates/%s' % DEPLOY_TEMPLATE['uuid']:
    {
        'GET': (
            {},
            DEPLOY_TEMPLATE,
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_DEPLOY_TEMPLATE,
        ),
    },
    '/v1/deploy_templates/%s?fields=uuid,name' % DEPLOY_TEMPLATE['uuid']:
    {
        'GET': (
            {},
            DEPLOY_TEMPLATE,
        ),
    },
}

fake_responses_pagination = {
    '/v1/deploy_templates':
    {
        'GET': (
            {},
            {"deploy_templates": [DEPLOY_TEMPLATE],
             "next": "http://127.0.0.1:6385/v1/deploy_templates/?limit=1"}
        ),
    },
    '/v1/deploy_templates/?limit=1':
    {
        'GET': (
            {},
            {"deploy_templates": [DEPLOY_TEMPLATE2]}
        ),
    },
    '/v1/deploy_templates/?marker=%s' % DEPLOY_TEMPLATE['uuid']:
    {
        'GET': (
            {},
            {"deploy_templates": [DEPLOY_TEMPLATE2]}
        ),
    },
}

fake_responses_sorting = {
    '/v1/deploy_templates/?sort_key=updated_at':
    {
        'GET': (
            {},
            {"deploy_templates": [DEPLOY_TEMPLATE2, DEPLOY_TEMPLATE]}
        ),
    },
    '/v1/deploy_templates/?sort_dir=desc':
    {
        'GET': (
            {},
            {"deploy_templates": [DEPLOY_TEMPLATE2, DEPLOY_TEMPLATE]}
        ),
    },
}


class DeployTemplateManagerTest(testtools.TestCase):

    def setUp(self):
        super(DeployTemplateManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = ironicclient.v1.deploy_template.DeployTemplateManager(
            self.api)

    def test_deploy_templates_list(self):
        deploy_templates = self.mgr.list()
        expect = [
            ('GET', '/v1/deploy_templates', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(deploy_templates))

    def test_deploy_templates_list_detail(self):
        deploy_templates = self.mgr.list(detail=True)
        expect = [
            ('GET', '/v1/deploy_templates/?detail=True', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(deploy_templates))

    def test_deploy_template_list_fields(self):
        deploy_templates = self.mgr.list(fields=['uuid', 'name'])
        expect = [
            ('GET', '/v1/deploy_templates/?fields=uuid,name', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(deploy_templates))

    def test_deploy_template_list_detail_and_fields_fail(self):
        self.assertRaises(exc.InvalidAttribute, self.mgr.list,
                          detail=True, fields=['uuid', 'name'])

    def test_deploy_templates_list_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = ironicclient.v1.deploy_template.DeployTemplateManager(
            self.api)
        deploy_templates = self.mgr.list(limit=1)
        expect = [
            ('GET', '/v1/deploy_templates/?limit=1', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(deploy_templates, HasLength(1))

    def test_deploy_templates_list_marker(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = ironicclient.v1.deploy_template.DeployTemplateManager(
            self.api)
        deploy_templates = self.mgr.list(marker=DEPLOY_TEMPLATE['uuid'])
        expect = [
            ('GET',
             '/v1/deploy_templates/?marker=%s' % DEPLOY_TEMPLATE['uuid'], {},
             None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(deploy_templates, HasLength(1))

    def test_deploy_templates_list_pagination_no_limit(self):
        self.api = utils.FakeAPI(fake_responses_pagination)
        self.mgr = ironicclient.v1.deploy_template.DeployTemplateManager(
            self.api)
        deploy_templates = self.mgr.list(limit=0)
        expect = [
            ('GET', '/v1/deploy_templates', {}, None),
            ('GET', '/v1/deploy_templates/?limit=1', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(deploy_templates, HasLength(2))

    def test_deploy_templates_list_sort_key(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = ironicclient.v1.deploy_template.DeployTemplateManager(
            self.api)
        deploy_templates = self.mgr.list(sort_key='updated_at')
        expect = [
            ('GET', '/v1/deploy_templates/?sort_key=updated_at', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(deploy_templates))

    def test_deploy_templates_list_sort_dir(self):
        self.api = utils.FakeAPI(fake_responses_sorting)
        self.mgr = ironicclient.v1.deploy_template.DeployTemplateManager(
            self.api)
        deploy_templates = self.mgr.list(sort_dir='desc')
        expect = [
            ('GET', '/v1/deploy_templates/?sort_dir=desc', {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(2, len(deploy_templates))

    def test_deploy_templates_show(self):
        deploy_template = self.mgr.get(DEPLOY_TEMPLATE['uuid'])
        expect = [
            ('GET', '/v1/deploy_templates/%s' % DEPLOY_TEMPLATE['uuid'], {},
             None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(DEPLOY_TEMPLATE['uuid'], deploy_template.uuid)
        self.assertEqual(DEPLOY_TEMPLATE['name'], deploy_template.name)
        self.assertEqual(DEPLOY_TEMPLATE['steps'], deploy_template.steps)
        self.assertEqual(DEPLOY_TEMPLATE['extra'], deploy_template.extra)

    def test_deploy_template_show_fields(self):
        deploy_template = self.mgr.get(DEPLOY_TEMPLATE['uuid'],
                                       fields=['uuid', 'name'])
        expect = [
            ('GET', '/v1/deploy_templates/%s?fields=uuid,name' %
             DEPLOY_TEMPLATE['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(DEPLOY_TEMPLATE['uuid'], deploy_template.uuid)
        self.assertEqual(DEPLOY_TEMPLATE['name'], deploy_template.name)

    def test_create(self):
        deploy_template = self.mgr.create(**CREATE_DEPLOY_TEMPLATE)
        expect = [
            ('POST', '/v1/deploy_templates', {}, CREATE_DEPLOY_TEMPLATE),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(deploy_template)

    def test_create_with_uuid(self):
        deploy_template = self.mgr.create(**CREATE_DEPLOY_TEMPLATE_WITH_UUID)
        expect = [
            ('POST', '/v1/deploy_templates', {},
             CREATE_DEPLOY_TEMPLATE_WITH_UUID),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(deploy_template)

    def test_delete(self):
        deploy_template = self.mgr.delete(
            template_id=DEPLOY_TEMPLATE['uuid'])
        expect = [
            ('DELETE', '/v1/deploy_templates/%s' % DEPLOY_TEMPLATE['uuid'], {},
             None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(deploy_template)

    def test_update(self):
        patch = {'op': 'replace',
                 'value': NEW_NAME,
                 'path': '/name'}
        deploy_template = self.mgr.update(
            template_id=DEPLOY_TEMPLATE['uuid'], patch=patch)
        expect = [
            ('PATCH', '/v1/deploy_templates/%s' % DEPLOY_TEMPLATE['uuid'],
             {}, patch),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NEW_NAME, deploy_template.name)
