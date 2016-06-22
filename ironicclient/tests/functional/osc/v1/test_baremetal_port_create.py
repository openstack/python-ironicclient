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


class BaremetalPortCreate(base.TestCase):
    """Detailed functional tests for baremetal port create command."""

    def setUp(self):
        super(BaremetalPortCreate, self).setUp()
        self.node = self.node_create()

    def test_extras(self):
        """Check baremetal port create command with extra data.

        Test steps:
        1) Create port using solitary and multiple --extra arguments.
        2) Check that port successfully created with right extras.
        """
        extras = [{'single_extra': 'yes'},
                  {'k1': 'v1', 'k2': 'v2', 'k3': 'v3'}]

        for extra in extras:
            params = self.generate_params('--extra', extra)
            port = self.port_create(self.node['uuid'], params=params)
            self.assert_dict_is_subset(extra, port['extra'])

    def test_pxe_1_19(self):
        """Check baremetal port create command with PXE option.

        Test steps:
        1) Create port using --pxe-enabled argument.
        2) Check that port successfully created with right PXE option.
        """
        pxe_values = [True, False]
        api_version = ' --os-baremetal-api-version 1.19'

        for value in pxe_values:
            port = self.port_create(
                self.node['uuid'],
                params='--pxe-enabled {0} {1}'.format(value, api_version))
            self.assertEqual(value, port['pxe_enabled'])

    def test_llc_1_19(self):
        """Check baremetal port create command with LLC option.

        Test steps:
        1) Create port using --local-link-connection argument.
        2) Check that port successfully created with right LLC data.
        """
        fake_port_id = data_utils.rand_name(prefix='ovs-node-')
        fake_switch_id = data_utils.rand_mac_address()
        llc_value = {"switch_info": "brbm",
                     "port_id": fake_port_id,
                     "switch_id": fake_switch_id}
        api_version = ' --os-baremetal-api-version 1.19'

        params = self.generate_params('--local-link-connection', llc_value)
        port = self.port_create(self.node['uuid'],
                                params='{0} {1}'.format(params, api_version))
        self.assert_dict_is_subset(llc_value, port['local_link_connection'])
