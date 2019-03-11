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

import json

import ddt
import six
from tempest.lib.common.utils import data_utils
from tempest.lib import exceptions

from ironicclient.tests.functional.osc.v1 import base


@ddt.ddt
class BaremetalDeployTemplateTests(base.TestCase):
    """Functional tests for baremetal deploy template commands."""

    @staticmethod
    def _get_random_trait():
        return data_utils.rand_name('CUSTOM', '').replace('-', '_')

    def setUp(self):
        super(BaremetalDeployTemplateTests, self).setUp()
        self.steps = json.dumps([{
            'interface': 'bios',
            'step': 'apply_configuration',
            'args': {},
            'priority': 10,
        }])
        name = self._get_random_trait()
        self.template = self.deploy_template_create(
            name, params="--steps '%s'" % self.steps)

    def tearDown(self):
        if self.template is not None:
            self.deploy_template_delete(self.template['uuid'])
        super(BaremetalDeployTemplateTests, self).tearDown()

    def test_list(self):
        """Check baremetal deploy template list command.

        Test steps:
        1) Create baremetal deploy template in setUp.
        2) List baremetal deploy templates.
        3) Check deploy template name and UUID in deploy templates list.
        """
        template_list = self.deploy_template_list()
        self.assertIn(self.template['name'],
                      [template['Name']
                       for template in template_list])
        self.assertIn(self.template['uuid'],
                      [template['UUID']
                       for template in template_list])

    def test_list_long(self):
        """Check baremetal deploy template list --long command

        Test steps:
        1) Create baremetal deploy template in setUp.
        2) List baremetal deploy templates with detail=True.
        3) Check deploy template fields in output.
        """
        template_list = self.deploy_template_list(params='--long')
        template = [template for template in template_list
                    if template['Name'] == self.template['name']][0]
        self.assertEqual(self.template['extra'], template['Extra'])
        self.assertEqual(self.template['name'], template['Name'])
        self.assertEqual(self.template['steps'], template['Steps'])
        self.assertEqual(self.template['uuid'], template['UUID'])

    def test_show(self):
        """Check baremetal deploy template show command with UUID.

        Test steps:
        1) Create baremetal deploy template in setUp.
        2) Show baremetal deploy template calling it by UUID.
        3) Check deploy template fields in output.
        """
        template = self.deploy_template_show(self.template['uuid'])
        self.assertEqual(self.template['extra'], template['extra'])
        self.assertEqual(self.template['name'], template['name'])
        self.assertEqual(self.template['steps'], template['steps'])
        self.assertEqual(self.template['uuid'], template['uuid'])

    def test_delete(self):
        """Check baremetal deploy template delete command.

        Test steps:
        1) Create baremetal deploy template in setUp.
        2) Delete baremetal deploy template by UUID.
        3) Check that deploy template deleted successfully and not in list.
        """
        output = self.deploy_template_delete(self.template['uuid'])
        self.assertIn('Deleted deploy template {0}'.format(
                      self.template['uuid']), output)
        template_list = self.deploy_template_list()
        self.assertNotIn(self.template['name'],
                         [template['Name'] for template in template_list])
        self.assertNotIn(self.template['uuid'],
                         [template['UUID'] for template in template_list])
        self.template = None

    def test_set_steps(self):
        """Check baremetal deploy template set command for steps.

        Test steps:
        1) Create baremetal deploy template in setUp.
        2) Set steps for deploy template.
        3) Check that baremetal deploy template steps were set.
        """
        steps = [{
            'interface': 'bios',
            'step': 'apply_configuration',
            'args': {},
            'priority': 20,
        }]
        self.openstack("baremetal deploy template set --steps '{0}' {1}"
                       .format(json.dumps(steps), self.template['uuid']))

        show_prop = self.deploy_template_show(self.template['uuid'],
                                              fields=['steps'])
        self.assertEqual(steps, show_prop['steps'])

    def test_set_unset(self):
        """Check baremetal deploy template set and unset commands.

        Test steps:
        1) Create baremetal deploy template in setUp.
        2) Set extra data for deploy template.
        3) Check that baremetal deploy template extra data was set.
        4) Unset extra data for deploy template.
        5) Check that baremetal deploy template  extra data was unset.
        """
        extra_key = 'ext'
        extra_value = 'testdata'
        self.openstack(
            'baremetal deploy template set --extra {0}={1} {2}'
            .format(extra_key, extra_value, self.template['uuid']))

        show_prop = self.deploy_template_show(self.template['uuid'],
                                              fields=['extra'])
        self.assertEqual(extra_value, show_prop['extra'][extra_key])

        self.openstack('baremetal deploy template unset --extra {0} {1}'
                       .format(extra_key, self.template['uuid']))

        show_prop = self.deploy_template_show(self.template['uuid'],
                                              fields=['extra'])
        self.assertNotIn(extra_key, show_prop['extra'])

    @ddt.data(
        ('--uuid', '', 'expected one argument'),
        ('--uuid', '!@#$^*&%^', 'Expected a UUID'),
        ('', '',
         'too few arguments' if six.PY2
         else 'the following arguments are required'),
        ('', 'not/a/name', 'Deploy template name must be a valid trait'),
        ('', 'foo', 'Deploy template name must be a valid trait'),
        ('--steps', '', 'expected one argument'),
        ('--steps', '[]', 'No deploy steps specified'))
    @ddt.unpack
    def test_create_negative(self, argument, value, ex_text):
        """Check errors on invalid input parameters."""
        base_cmd = 'baremetal deploy template create'
        if argument != '':
            base_cmd += ' %s' % self._get_random_trait()
        if argument != '--steps':
            base_cmd += " --steps '%s'" % self.steps
        command = self.construct_cmd(base_cmd, argument, value)
        self.assertRaisesRegex(exceptions.CommandFailed, ex_text,
                               self.openstack, command)
