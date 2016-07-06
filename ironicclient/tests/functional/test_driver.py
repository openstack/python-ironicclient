# Copyright (c) 2015 Mirantis, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from ironicclient.tests.functional import base


class DriverSanityTestIronicClient(base.FunctionalTestBase):
    """Sanity tests for testing actions with driver.

    Smoke test for the Ironic CLI commands which checks basic actions with
    driver command like driver-show, driver-properties.
    """

    def test_driver_show(self):
        """Test steps:

        1) get drivers names
        2) check that each driver exists in driver-show output
        """
        drivers_names = self.get_drivers_names()
        for driver in drivers_names:
            driver_show = self.show_driver(driver)
            self.assertEqual(driver, driver_show['name'])

    def test_driver_properties(self):
        """Test steps:

        1) get drivers names
        2) check that each driver has some properties
        """
        drivers_names = self.get_drivers_names()
        for driver in drivers_names:
            driver_properties = self.properties_driver(driver)
            self.assertNotEqual([], [x['Property'] for x in driver_properties])

    def test_driver_list(self):
        """Test steps:

        1) get list of drivers
        2) check that list of drivers is not empty
        """
        driver = 'fake'
        available_drivers = self.get_drivers_names()
        self.assertTrue(len(available_drivers) > 0)
        self.assertIn(driver, available_drivers)
