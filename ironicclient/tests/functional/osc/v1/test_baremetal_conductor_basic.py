# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from ironicclient.tests.functional.osc.v1 import base


class BaremetalConductorTests(base.TestCase):
    """Functional tests for baremetal conductor commands."""

    def test_list(self):
        """List available conductors.

        There is at lease one conductor in the functional tests, if not, other
        tests will fail too.
        """
        hostnames = [c['Hostname'] for c in self.conductor_list()]
        self.assertIsNotNone(hostnames)

    def test_show(self):
        """Show specified conductor.

        Conductor name varies in different environment, list first, then show
        one of them.
        """
        conductors = self.conductor_list()
        conductor = self.conductor_show(conductors[0]['Hostname'])
        self.assertIn('conductor_group', conductor)
        self.assertIn('alive', conductor)
        self.assertIn('drivers', conductor)
