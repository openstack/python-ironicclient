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


class ProvisionStateTests(base.TestCase):
    """Functional tests for baremetal node provision state commands."""

    def setUp(self):
        super(ProvisionStateTests, self).setUp()
        self.node = self.node_create()

    def test_deploy_rebuild_undeploy_manage(self):
        """Deploy, rebuild and undeploy node.

        Test steps:
        1) Create baremetal node in setUp.
        2) Check initial "enroll" provision state.
        3) Set baremetal node "manage" provision state.
        4) Check baremetal node provision_state field value is "manageable".
        5) Set baremetal node "provide" provision state.
        6) Check baremetal node provision_state field value is "available".
        7) Set baremetal node "deploy" provision state.
        8) Check baremetal node provision_state field value is "active".
        9) Set baremetal node "rebuild" provision state.
        10) Check baremetal node provision_state field value is "active".
        11) Set baremetal node "undeploy" provision state.
        12) Check baremetal node provision_state field value is "available".
        13) Set baremetal node "manage" provision state.
        14) Check baremetal node provision_state field value is "manageable".
        15) Set baremetal node "provide" provision state.
        16) Check baremetal node provision_state field value is "available".
        """
        show_prop = self.node_show(self.node['uuid'], ["provision_state"])
        self.assertEqual("enroll", show_prop["provision_state"])

        # manage
        self.openstack('baremetal node manage {0}'.format(self.node['uuid']))
        show_prop = self.node_show(self.node['uuid'], ["provision_state"])
        self.assertEqual("manageable", show_prop["provision_state"])

        # provide
        self.openstack('baremetal node provide {0}'.format(self.node['uuid']))
        show_prop = self.node_show(self.node['uuid'], ["provision_state"])
        self.assertEqual("available", show_prop["provision_state"])

        # deploy
        self.openstack('baremetal node deploy {0}'.format(self.node['uuid']))
        show_prop = self.node_show(self.node['uuid'], ["provision_state"])
        self.assertEqual("active", show_prop["provision_state"])

        # rebuild
        self.openstack('baremetal node rebuild {0}'.format(self.node['uuid']))

        show_prop = self.node_show(self.node['uuid'], ["provision_state"])
        self.assertEqual("active", show_prop["provision_state"])

        # undeploy
        self.openstack('baremetal node undeploy {0}'.format(self.node['uuid']))

        show_prop = self.node_show(self.node['uuid'], ["provision_state"])
        self.assertEqual("available", show_prop["provision_state"])

        # manage
        self.openstack('baremetal node manage {0}'.format(self.node['uuid']))
        show_prop = self.node_show(self.node['uuid'], ["provision_state"])
        self.assertEqual("manageable", show_prop["provision_state"])

        # provide back
        self.openstack('baremetal node provide {0}'.format(self.node['uuid']))
        show_prop = self.node_show(self.node['uuid'], ["provision_state"])
        self.assertEqual("available", show_prop["provision_state"])
