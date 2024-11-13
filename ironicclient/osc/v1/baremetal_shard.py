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

import logging

from osc_lib.command import command
from osc_lib import utils as oscutils

from ironicclient.v1 import resource_fields as res_fields


class ListBaremetalShard(command.Lister):
    """List baremetal shards."""

    log = logging.getLogger(__name__ + ".ListBaremetalShard")

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.baremetal

        data = client.shard.list()
        columns = res_fields.SHARD_RESOURCE.fields
        labels = res_fields.SHARD_RESOURCE.labels

        return (labels,
                (oscutils.get_item_properties(s, columns) for s in data))
