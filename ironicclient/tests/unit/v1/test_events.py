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

import testtools

from ironicclient.tests.unit import utils
from ironicclient.v1 import events

FAKE_EVENT = {"event": "type.event"}
FAKE_NETWORK_PORT_EVENT = {
    'event': "network.bind_port",
    'port_id': '11111111-aaaa-bbbb-cccc-555555555555',
    'mac_address': 'de:ad:ca:fe:ba:be',
    'status': 'ACTIVE',
    'device_id': '22222222-aaaa-bbbb-cccc-555555555555',
    'binding:host_id': '22222222-aaaa-bbbb-cccc-555555555555',
    'binding:vnic_type': 'baremetal',
}
FAKE_EVENTS = {'events': [FAKE_EVENT]}
FAKE_NETWORK_PORT_EVENTS = {'events': [FAKE_NETWORK_PORT_EVENT]}

fake_responses = {
    '/v1/events':
        {
            'POST': (
                {},
                None
            )
        }
}


class EventManagerTest(testtools.TestCase):
    def setUp(self):
        super(EventManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = events.EventManager(self.api)

    def test_event(self):
        evts = self.mgr.create(**FAKE_EVENTS)
        expect = [('POST', '/v1/events', {}, FAKE_EVENTS)]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(evts)

    def test_network_port_event(self):
        evts = self.mgr.create(**FAKE_NETWORK_PORT_EVENTS)
        expect = [('POST', '/v1/events', {}, FAKE_NETWORK_PORT_EVENTS)]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(evts)
