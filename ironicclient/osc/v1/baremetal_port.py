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

import logging

from cliff import show

from ironicclient.common import utils
from ironicclient.v1 import resource_fields as res_fields


class CreateBaremetalPort(show.ShowOne):
    """Create a new port"""

    log = logging.getLogger(__name__ + ".CreateBaremetalPort")

    def get_parser(self, prog_name):
        parser = super(CreateBaremetalPort, self).get_parser(prog_name)

        parser.add_argument(
            'address',
            metavar='<address>',
            help='MAC address for this port.')
        parser.add_argument(
            '--node',
            dest='node_uuid',
            metavar='<uuid>',
            required=True,
            help='UUID of the node that this port belongs to.')
        parser.add_argument(
            '--extra',
            metavar="<key=value>",
            action='append',
            help="Record arbitrary key/value metadata. "
                 "Can be specified multiple times.")
        parser.add_argument(
            '-l', '--local-link-connection',
            metavar="<key=value>",
            action='append',
            help="Key/value metadata describing Local link connection "
                 "information. Valid keys are switch_info, switch_id, "
                 "port_id. Can be specified multiple times.")
        parser.add_argument(
            '--pxe-enabled',
            metavar='<boolean>',
            help='Indicates whether this Port should be used when '
                 'PXE booting this Node.')

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)" % parsed_args)
        baremetal_client = self.app.client_manager.baremetal

        field_list = ['address', 'extra', 'node_uuid', 'pxe_enabled',
                      'local_link_connection']
        fields = dict((k, v) for (k, v) in vars(parsed_args).items()
                      if k in field_list and v is not None)
        fields = utils.args_array_to_dict(fields, 'extra')
        fields = utils.args_array_to_dict(fields, 'local_link_connection')
        port = baremetal_client.port.create(**fields)

        data = dict([(f, getattr(port, f, '')) for f in
                     res_fields.PORT_DETAILED_RESOURCE.fields])

        return self.dict2columns(data)
