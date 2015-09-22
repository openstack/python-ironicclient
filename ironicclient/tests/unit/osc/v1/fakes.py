#
#   Copyright 2015 Red Hat, Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import mock
from openstackclient.tests import utils

from ironicclient.tests.unit.osc import fakes

baremetal_uuid = 'xxx-xxxxxx-xxxx'
baremetal_name = 'fake name'
baremetal_instance_uuid = 'yyy-yyyyyy-yyyy'
baremetal_power_state = None
baremetal_provision_state = None
baremetal_maintenance = False

BAREMETAL = {
    'uuid': baremetal_uuid,
    'name': baremetal_name,
    'instance_uuid': baremetal_instance_uuid,
    'power_state': baremetal_power_state,
    'provision_state': baremetal_provision_state,
    'maintenance': baremetal_maintenance,
    'links': []
}


class TestBaremetal(utils.TestCommand):

    def setUp(self):
        super(TestBaremetal, self).setUp()

        self.app.client_manager.auth_ref = mock.Mock(auth_token="TOKEN")
        self.app.client_manager.baremetal = mock.Mock()


class FakeBaremetalResource(fakes.FakeResource):

    def get_keys(self):
        return {'property': 'value'}
