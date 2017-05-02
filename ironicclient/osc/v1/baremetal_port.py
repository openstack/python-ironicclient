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

import itertools
import logging

from osc_lib.command import command
from osc_lib import utils as oscutils

from ironicclient.common.i18n import _
from ironicclient.common import utils
from ironicclient import exc
from ironicclient.v1 import resource_fields as res_fields


class CreateBaremetalPort(command.ShowOne):
    """Create a new port"""

    log = logging.getLogger(__name__ + ".CreateBaremetalPort")

    def get_parser(self, prog_name):
        parser = super(CreateBaremetalPort, self).get_parser(prog_name)

        parser.add_argument(
            'address',
            metavar='<address>',
            help=_('MAC address for this port.')
        )
        parser.add_argument(
            '--node',
            dest='node_uuid',
            metavar='<uuid>',
            required=True,
            help=_('UUID of the node that this port belongs to.')
        )
        parser.add_argument(
            '--uuid',
            dest='uuid',
            metavar='<uuid>',
            help=_('UUID of the port.'))
        parser.add_argument(
            '--extra',
            metavar="<key=value>",
            action='append',
            help=_("Record arbitrary key/value metadata. "
                   "Can be specified multiple times.")
        )
        parser.add_argument(
            '--local-link-connection',
            metavar="<key=value>",
            action='append',
            help=_("Key/value metadata describing Local link connection "
                   "information. Valid keys are 'switch_info', 'switch_id', "
                   "and 'port_id'. The keys 'switch_id' and 'port_id' are "
                   "required. Can be specified multiple times.")
        )
        parser.add_argument(
            '-l',
            dest='local_link_connection_deprecated',
            metavar="<key=value>",
            action='append',
            help=_("DEPRECATED. Please use --local-link-connection instead. "
                   "Key/value metadata describing Local link connection "
                   "information. Valid keys are 'switch_info', 'switch_id', "
                   "and 'port_id'. The keys 'switch_id' and 'port_id' are "
                   "required. Can be specified multiple times.")
        )
        parser.add_argument(
            '--pxe-enabled',
            metavar='<boolean>',
            help=_('Indicates whether this Port should be used when '
                   'PXE booting this Node.')
        )

        parser.add_argument(
            '--port-group',
            dest='portgroup_uuid',
            metavar='<uuid>',
            help=_("UUID of the port group that this port belongs to."))

        parser.add_argument(
            '--physical-network',
            dest='physical_network',
            metavar='<physical network>',
            help=_("Name of the physical network to which this port is "
                   "connected."))

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        baremetal_client = self.app.client_manager.baremetal

        if parsed_args.local_link_connection_deprecated:
            self.log.warning("Please use --local-link-connection instead "
                             "of -l, as it is deprecated and will be "
                             "removed in future releases.")
            # It is parsed to either None, or to an array
            if parsed_args.local_link_connection:
                parsed_args.local_link_connection.extend(
                    parsed_args.local_link_connection_deprecated)
            else:
                parsed_args.local_link_connection = (
                    parsed_args.local_link_connection_deprecated)

        field_list = ['address', 'uuid', 'extra', 'node_uuid', 'pxe_enabled',
                      'local_link_connection', 'portgroup_uuid',
                      'physical_network']
        fields = dict((k, v) for (k, v) in vars(parsed_args).items()
                      if k in field_list and v is not None)
        fields = utils.args_array_to_dict(fields, 'extra')
        fields = utils.args_array_to_dict(fields, 'local_link_connection')
        port = baremetal_client.port.create(**fields)

        data = dict([(f, getattr(port, f, '')) for f in
                     res_fields.PORT_DETAILED_RESOURCE.fields])

        return self.dict2columns(data)


class ShowBaremetalPort(command.ShowOne):
    """Show baremetal port details."""

    log = logging.getLogger(__name__ + ".ShowBaremetalPort")

    def get_parser(self, prog_name):
        parser = super(ShowBaremetalPort, self).get_parser(prog_name)
        parser.add_argument(
            "port",
            metavar="<id>",
            help=_("UUID of the port (or MAC address if --address is "
                   "specified).")
        )
        parser.add_argument(
            '--address',
            dest='address',
            action='store_true',
            default=False,
            help=_('<id> is the MAC address (instead of the UUID) of the '
                   'port.')
        )
        parser.add_argument(
            '--fields',
            nargs='+',
            dest='fields',
            metavar='<field>',
            action='append',
            choices=res_fields.PORT_DETAILED_RESOURCE.fields,
            default=[],
            help=_("One or more port fields. Only these fields will be "
                   "fetched from the server.")
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal
        fields = list(itertools.chain.from_iterable(parsed_args.fields))
        fields = fields if fields else None

        if parsed_args.address:
            port = baremetal_client.port.get_by_address(
                parsed_args.port, fields=fields)._info
        else:
            port = baremetal_client.port.get(
                parsed_args.port, fields=fields)._info

        port.pop("links", None)
        return zip(*sorted(port.items()))


class UnsetBaremetalPort(command.Command):
    """Unset baremetal port properties."""
    log = logging.getLogger(__name__ + ".UnsetBaremetalPort")

    def get_parser(self, prog_name):
        parser = super(UnsetBaremetalPort, self).get_parser(prog_name)

        parser.add_argument(
            'port',
            metavar='<port>',
            help=_("UUID of the port.")
        )
        parser.add_argument(
            "--extra",
            metavar="<key>",
            action='append',
            help=_('Extra to unset on this baremetal port '
                   '(repeat option to unset multiple extras)')
        )

        parser.add_argument(
            '--port-group',
            action='store_true',
            dest='portgroup',
            help=_("Remove port from the port group"))

        parser.add_argument(
            '--physical-network',
            action='store_true',
            dest='physical_network',
            help=_("Unset the physical network on this baremetal port."))

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal
        properties = []
        if parsed_args.extra:
            properties.extend(utils.args_array_to_patch(
                'remove',
                ['extra/' + x for x in parsed_args.extra]))
        if parsed_args.portgroup:
            properties.extend(utils.args_array_to_patch('remove',
                              ['portgroup_uuid']))
        if parsed_args.physical_network:
            properties.extend(utils.args_array_to_patch('remove',
                              ['physical_network']))

        if properties:
            baremetal_client.port.update(parsed_args.port, properties)
        else:
            self.log.warning("Please specify what to unset.")


class SetBaremetalPort(command.Command):
    """Set baremetal port properties."""

    log = logging.getLogger(__name__ + ".SetBaremetalPort")

    def get_parser(self, prog_name):
        parser = super(SetBaremetalPort, self).get_parser(prog_name)

        parser.add_argument(
            'port',
            metavar='<port>',
            help=_("UUID of the port")
        )
        parser.add_argument(
            '--node',
            dest='node_uuid',
            metavar='<uuid>',
            help=_('Set UUID of the node that this port belongs to')
        )
        parser.add_argument(
            "--address",
            metavar="<address>",
            dest='address',
            help=_("Set MAC address for this port")
        )
        parser.add_argument(
            "--extra",
            metavar="<key=value>",
            action='append',
            help=_('Extra to set on this baremetal port '
                   '(repeat option to set multiple extras)')
        )
        parser.add_argument(
            "--port-group",
            metavar="<uuid>",
            dest='portgroup_uuid',
            help=_('Set UUID of the port group that this port belongs to.'))
        parser.add_argument(
            "--local-link-connection",
            metavar="<key=value>",
            action='append',
            help=_("Key/value metadata describing local link connection "
                   "information. Valid keys are 'switch_info', 'switch_id', "
                   "and 'port_id'. The keys 'switch_id' and 'port_id' are "
                   "required. Can be specified multiple times.")
        )
        pxe_enabled_group = parser.add_mutually_exclusive_group(required=False)
        pxe_enabled_group.add_argument(
            "--pxe-enabled",
            dest='pxe_enabled',
            default=None,
            action='store_true',
            help=_("Indicates that this port should be used when "
                   "PXE booting this node (default)")
        )
        pxe_enabled_group.add_argument(
            "--pxe-disabled",
            dest='pxe_enabled',
            default=None,
            action='store_false',
            help=_("Indicates that this port should not be used when "
                   "PXE booting this node")
        )
        parser.add_argument(
            '--physical-network',
            metavar='<physical network>',
            dest='physical_network',
            help=_("Set the name of the physical network to which this port "
                   "is connected."))

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        properties = []
        if parsed_args.node_uuid:
            node_uuid = ["node_uuid=%s" % parsed_args.node_uuid]
            properties.extend(utils.args_array_to_patch(
                'add', node_uuid))
        if parsed_args.address:
            address = ["address=%s" % parsed_args.address]
            properties.extend(utils.args_array_to_patch('add', address))
        if parsed_args.extra:
            properties.extend(utils.args_array_to_patch(
                'add', ['extra/' + x for x in parsed_args.extra]))
        if parsed_args.portgroup_uuid:
            portgroup_uuid = ["portgroup_uuid=%s" % parsed_args.portgroup_uuid]
            properties.extend(utils.args_array_to_patch('add', portgroup_uuid))
        if parsed_args.local_link_connection:
            properties.extend(utils.args_array_to_patch(
                'add', ['local_link_connection/' + x for x in
                        parsed_args.local_link_connection]))
        if parsed_args.pxe_enabled is not None:
            properties.extend(utils.args_array_to_patch(
                'add', ['pxe_enabled=%s' % parsed_args.pxe_enabled]))
        if parsed_args.physical_network:
            physical_network = ["physical_network=%s" %
                                parsed_args.physical_network]
            properties.extend(utils.args_array_to_patch('add',
                                                        physical_network))

        if properties:
            baremetal_client.port.update(parsed_args.port, properties)
        else:
            self.log.warning("Please specify what to set.")


class DeleteBaremetalPort(command.Command):
    """Delete port(s)."""

    log = logging.getLogger(__name__ + ".DeleteBaremetalPort")

    def get_parser(self, prog_name):
        parser = super(DeleteBaremetalPort, self).get_parser(prog_name)
        parser.add_argument(
            "ports",
            metavar="<port>",
            nargs="+",
            help=_("UUID(s) of the port(s) to delete.")
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        failures = []
        for port in parsed_args.ports:
            try:
                baremetal_client.port.delete(port)
                print(_('Deleted port %s') % port)
            except exc.ClientException as e:
                failures.append(_("Failed to delete port %(port)s: %(error)s")
                                % {'port': port, 'error': e})

        if failures:
            raise exc.ClientException("\n".join(failures))


class ListBaremetalPort(command.Lister):
    """List baremetal ports."""

    log = logging.getLogger(__name__ + ".ListBaremetalPort")

    def get_parser(self, prog_name):
        parser = super(ListBaremetalPort, self).get_parser(prog_name)
        parser.add_argument(
            '--address',
            dest='address',
            metavar='<mac-address>',
            help=_("Only show information for the port with this MAC address.")
        )
        parser.add_argument(
            '--node',
            dest='node',
            metavar='<node>',
            help=_("Only list ports of this node (name or UUID).")
        )
        parser.add_argument(
            "--port-group",
            metavar="<port group>",
            dest='portgroup',
            help=_('Only list ports of this port group (name or UUID).'))
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            type=int,
            help=_('Maximum number of ports to return per request, '
                   '0 for no limit. Default is the maximum number used '
                   'by the Ironic API Service.')
        )
        parser.add_argument(
            '--marker',
            metavar='<port>',
            help=_('Port UUID (for example, of the last port in the list '
                   'from a previous request). Returns the list of ports '
                   'after this UUID.')
        )
        parser.add_argument(
            '--sort',
            metavar="<key>[:<direction>]",
            help=_('Sort output by specified port fields and directions '
                   '(asc or desc) (default: asc). Multiple fields and '
                   'directions can be specified, separated by comma.')
        )
        display_group = parser.add_mutually_exclusive_group()
        display_group.add_argument(
            '--long',
            dest='detail',
            action='store_true',
            default=False,
            help=_("Show detailed information about ports.")
        )
        display_group.add_argument(
            '--fields',
            nargs='+',
            dest='fields',
            metavar='<field>',
            action='append',
            default=[],
            choices=res_fields.PORT_DETAILED_RESOURCE.fields,
            help=_("One or more port fields. Only these fields will be "
                   "fetched from the server. Can not be used when "
                   "'--long' is specified.")
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.baremetal

        columns = res_fields.PORT_RESOURCE.fields
        labels = res_fields.PORT_RESOURCE.labels

        params = {}
        if parsed_args.limit is not None and parsed_args.limit < 0:
            raise exc.CommandError(
                _('Expected non-negative --limit, got %s') %
                parsed_args.limit)
        params['limit'] = parsed_args.limit
        params['marker'] = parsed_args.marker

        if parsed_args.address is not None:
            params['address'] = parsed_args.address
        if parsed_args.node is not None:
            params['node'] = parsed_args.node
        if parsed_args.portgroup is not None:
            params['portgroup'] = parsed_args.portgroup

        if parsed_args.detail:
            params['detail'] = parsed_args.detail
            columns = res_fields.PORT_DETAILED_RESOURCE.fields
            labels = res_fields.PORT_DETAILED_RESOURCE.labels

        elif parsed_args.fields:
            params['detail'] = False
            fields = itertools.chain.from_iterable(parsed_args.fields)
            resource = res_fields.Resource(list(fields))
            columns = resource.fields
            labels = resource.labels
            params['fields'] = columns

        self.log.debug("params(%s)", params)
        data = client.port.list(**params)

        data = oscutils.sort_items(data, parsed_args.sort)

        return (labels,
                (oscutils.get_item_properties(s, columns, formatters={
                    'extra': oscutils.format_dict},) for s in data))
