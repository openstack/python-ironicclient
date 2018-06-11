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

from ironicclient.tests.functional.osc.v1 import base


class BaremetalDriverTests(base.TestCase):
    """Functional tests for baremetal driver commands."""

    def test_show(self):
        """Show specified driver.

        Test step:
        1) Check output of baremetal driver show command.
        """
        driver = self.driver_show(self.driver_name)
        self.assertEqual(self.driver_name, driver['name'])

    def test_list(self):
        """List available drivers.

        Test steps:
        1) Get list of drivers.
        2) Check that list of drivers is not empty.
        """
        drivers = [
            driver['Supported driver(s)'] for driver in self.driver_list()
        ]
        self.assertIn(self.driver_name, drivers)
