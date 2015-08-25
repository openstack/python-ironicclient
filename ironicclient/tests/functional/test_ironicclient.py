# Copyright 2015 Hewlett-Packard Development Company, L.P.
# All Rights Reserved.
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


class TestIronicClient(base.FunctionalTestBase):
    def test_node_list(self):
        list = self.ironic('node-list')
        self.assertTableHeaders(['UUID', 'Name', 'Instance UUID',
                                 'Power State', 'Provisioning State',
                                 'Maintenance'], list)

    def test_node_create_get_delete(self):
        node = self.create_node()
        got = self.ironic('node-show', params=node['uuid'])
        expected_node = self.get_dict_from_output(got)
        self.assertEqual(expected_node['uuid'], node['uuid'])
        self.ironic('node-delete', params=node['uuid'])
        self.assertNodeDeleted(node['uuid'])
