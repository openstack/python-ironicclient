#    Copyright (c) 2016 Mirantis, Inc.
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

from tempest.lib.common.utils import data_utils

from ironicclient.tests.functional.osc.v1 import base


class BaremetalChassisCreate(base.TestCase):
    """Functional tests for baremetal chassis create command with options."""

    def setUp(self):
        super(BaremetalChassisCreate, self).setUp()

    @staticmethod
    def generate_params(argument, params):
        params_str = ''
        for key, value in params.items():
            params_str += ' {0} {1}={2}'.format(argument, key, value)
        return params_str

    def test_description(self):
        """Create chassis with description.

        Test steps:
        1) Create chassis using --description argument.
        2) Check that chassis was successfully created with description.
        """
        description = 'Small Funny Test Chassis'
        arg = '--description'
        chassis = self.chassis_create(
            params="{0} '{1}'".format(arg, description))
        self.assertEqual(description, chassis['description'])

    def test_extras(self):
        """Create chassis with extra data.

        Test steps:
        1) Create chassis using --extra argument.
        2) Check that chassis was successfully created with extras.
        """
        extras = [{u'metadata': u'yes'},
                  {u'Size': '2U', u'Power(W)': 2000,
                   u'HDDs': 16, u'backplane': u'2.5-inch'}]
        arg = '--extra'
        for extra in extras:
            params = self.generate_params(arg, extra)
            chassis = self.chassis_create(params=params)
            self.assertEqual(extra, chassis['extra'])

    def test_specific_uuid(self):
        """Create chassis with specific UUID.

        Test steps:
        1) Create chassis using --uuid argument.
        2) Check that chassis was successfully created with specific UUID.
        """
        arg = '--uuid'
        chassis_uuid = data_utils.rand_uuid()
        chassis = self.chassis_create(params="{0} {1}"
                                      .format(arg, chassis_uuid))
        self.assertEqual(chassis_uuid, chassis['uuid'])
