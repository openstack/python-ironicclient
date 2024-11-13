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

import copy

from ironicclient.osc.v1 import baremetal_shard
from ironicclient.tests.unit.osc.v1 import fakes as baremetal_fakes


class TestBaremetalShard(baremetal_fakes.TestBaremetal):
    def setUp(self):
        super(TestBaremetalShard, self).setUp()
        self.baremetal_mock = self.app.client_manager.baremetal
        self.baremetal_mock.reset_mock()


class TestBaremetalShardList(TestBaremetalShard):
    def setUp(self):
        super(TestBaremetalShardList, self).setUp()

        # Return a list containing mocked shard data to
        # simulate the expected output
        self.baremetal_mock.shard.list.return_value = [
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.SHARD),
                loaded=True,
            ),
        ]

        # Get the command object to test
        self.cmd = baremetal_shard.ListBaremetalShard(self.app, None)

    def test_shard_list(self):
        arglist = []
        verifylist = []

        # Parse arguments and invoke command
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Define expected columns and data output
        collist = ("Name", "Count")
        datalist = ((baremetal_fakes.baremetal_shard_name,
                     baremetal_fakes.baremetal_shard_count), )

        self.assertEqual(collist, columns)
        self.assertEqual(datalist, tuple(data))
