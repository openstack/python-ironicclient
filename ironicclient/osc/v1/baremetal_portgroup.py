#
#   Copyright 2016 Mirantis, Inc.
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


class CreateBaremetalPortGroup(command.ShowOne):
    """Create a new baremetal port group."""

    log = logging.getLogger(__name__ + ".CreateBaremetalPortGroup")

    def get_parser(self, prog_name):
        parser = super(CreateBaremetalPortGroup, self).get_parser(prog_name)

        parser.add_argument(
            '--node',
            dest='node_uuid',
            metavar='<uuid>',
            required=True,
            help=_('UUID of the node that this port group belongs to.'))
        parser.add_argument(
            '--address',
            metavar='<mac-address>',
            help=_('MAC address for this port group.'))
        parser.add_argument(
            '--name',
            dest='name',
            help=_('Name of the port group.'))
        parser.add_argument(
            '--uuid',
            dest='uuid',
            help=_('UUID of the port group.'))
        parser.add_argument(
            '--extra',
            metavar="<key=value>",
            action='append',
            help=_("Record arbitrary key/value metadata. "
                   "Can be specified multiple times."))
        parser.add_argument(
            '--mode',
            help=_('Mode of the port group. For possible values, refer to '
                   'https://www.kernel.org/doc/Documentation/networking'
                   '/bonding.txt.'))
        parser.add_argument(
            '--property',
            dest='properties',
            metavar="<key=value>",
            action='append',
            help=_("Key/value property related to this port group's "
                   "configuration. Can be specified multiple times."))
        standalone_ports_group = parser.add_mutually_exclusive_group()
        standalone_ports_group.add_argument(
            '--support-standalone-ports',
            action='store_true',
            help=_("Ports that are members of this port group "
                   "can be used as stand-alone ports. (default)"))
        standalone_ports_group.add_argument(
            '--unsupport-standalone-ports',
            action='store_true',
            help=_("Ports that are members of this port group "
                   "cannot be used as stand-alone ports."))

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        baremetal_client = self.app.client_manager.baremetal

        field_list = ['node_uuid', 'address', 'name', 'uuid', 'extra', 'mode',
                      'properties']
        fields = dict((k, v) for (k, v) in vars(parsed_args).items()
                      if k in field_list and v is not None)
        if parsed_args.support_standalone_ports:
            fields['standalone_ports_supported'] = True
        if parsed_args.unsupport_standalone_ports:
            fields['standalone_ports_supported'] = False

        fields = utils.args_array_to_dict(fields, 'extra')
        fields = utils.args_array_to_dict(fields, 'properties')
        portgroup = baremetal_client.portgroup.create(**fields)

        data = dict([(f, getattr(portgroup, f, '')) for f in
                     res_fields.PORTGROUP_DETAILED_RESOURCE.fields])

        return self.dict2columns(data)


class ShowBaremetalPortGroup(command.ShowOne):
    """Show baremetal port group details."""

    log = logging.getLogger(__name__ + ".ShowBaremetalPortGroup")

    def get_parser(self, prog_name):
        parser = super(ShowBaremetalPortGroup, self).get_parser(prog_name)
        parser.add_argument(
            "portgroup",
            metavar="<id>",
            help=_("UUID or name of the port group "
                   "(or MAC address if --address is specified)."))
        parser.add_argument(
            '--address',
            dest='address',
            action='store_true',
            default=False,
            help=_('<id> is the MAC address (instead of UUID or name) '
                   'of the port group.'))
        parser.add_argument(
            '--fields',
            nargs='+',
            dest='fields',
            metavar='<field>',
            action='append',
            choices=res_fields.PORTGROUP_DETAILED_RESOURCE.fields,
            default=[],
            help=_("One or more port group fields. Only these fields will be "
                   "fetched from the server."))
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal
        fields = list(itertools.chain.from_iterable(parsed_args.fields))
        fields = fields if fields else None

        if parsed_args.address:
            portgroup = baremetal_client.portgroup.get_by_address(
                parsed_args.portgroup, fields=fields)._info
        else:
            portgroup = baremetal_client.portgroup.get(
                parsed_args.portgroup, fields=fields)._info

        portgroup.pop("links", None)
        portgroup.pop("ports", None)
        return zip(*sorted(portgroup.items()))


class ListBaremetalPortGroup(command.Lister):
    """List baremetal port groups."""

    log = logging.getLogger(__name__ + ".ListBaremetalPortGroup")

    def get_parser(self, prog_name):
        parser = super(ListBaremetalPortGroup, self).get_parser(prog_name)
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            type=int,
            help=_('Maximum number of port groups to return per request, '
                   '0 for no limit. Default is the maximum number used '
                   'by the Baremetal API Service.'))
        parser.add_argument(
            '--marker',
            metavar='<port group>',
            help=_('Port group UUID (for example, of the last port group in '
                   'the list from a previous request). Returns the list of '
                   'port groups after this UUID.'))
        parser.add_argument(
            '--sort',
            metavar="<key>[:<direction>]",
            help=_('Sort output by specified port group fields and directions '
                   '(asc or desc) (default: asc). Multiple fields and '
                   'directions can be specified, separated by comma.'))
        parser.add_argument(
            '--address',
            metavar='<mac-address>',
            help=_("Only show information for the port group with this MAC "
                   "address."))
        parser.add_argument(
            '--node',
            dest='node',
            metavar='<node>',
            help=_("Only list port groups of this node (name or UUID)."))

        display_group = parser.add_mutually_exclusive_group(required=False)
        display_group.add_argument(
            '--long',
            default=False,
            dest='detail',
            help=_("Show detailed information about the port groups."),
            action='store_true')
        display_group.add_argument(
            '--fields',
            nargs='+',
            dest='fields',
            metavar='<field>',
            action='append',
            default=[],
            choices=res_fields.PORTGROUP_DETAILED_RESOURCE.fields,
            help=_("One or more port group fields. Only these fields will be "
                   "fetched from the server. Can not be used when '--long' is "
                   "specified."))
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.baremetal

        columns = res_fields.PORTGROUP_RESOURCE.fields
        labels = res_fields.PORTGROUP_RESOURCE.labels

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

        if parsed_args.detail:
            params['detail'] = parsed_args.detail
            columns = res_fields.PORTGROUP_DETAILED_RESOURCE.fields
            labels = res_fields.PORTGROUP_DETAILED_RESOURCE.labels
        elif parsed_args.fields:
            params['detail'] = False
            fields = itertools.chain.from_iterable(parsed_args.fields)
            resource = res_fields.Resource(list(fields))
            columns = resource.fields
            labels = resource.labels
            params['fields'] = columns

        self.log.debug("params(%s)", params)
        data = client.portgroup.list(**params)

        data = oscutils.sort_items(data, parsed_args.sort)

        return (labels,
                (oscutils.get_item_properties(s, columns, formatters={
                    'Properties': utils.HashColumn},) for s in data))


class DeleteBaremetalPortGroup(command.Command):
    """Unregister baremetal port group(s)."""

    log = logging.getLogger(__name__ + ".DeleteBaremetalPortGroup")

    def get_parser(self, prog_name):
        parser = super(DeleteBaremetalPortGroup, self).get_parser(prog_name)
        parser.add_argument(
            "portgroups",
            metavar="<port group>",
            nargs="+",
            help=_("Port group(s) to delete (name or UUID)."))

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        failures = []
        for portgroup in parsed_args.portgroups:
            try:
                baremetal_client.portgroup.delete(portgroup)
                print(_('Deleted port group %s') % portgroup)
            except exc.ClientException as e:
                failures.append(_("Failed to delete port group %(portgroup)s: "
                                  " %(error)s")
                                % {'portgroup': portgroup, 'error': e})

        if failures:
            raise exc.ClientException("\n".join(failures))


class SetBaremetalPortGroup(command.Command):
    """Set baremetal port group properties."""

    log = logging.getLogger(__name__ + ".SetBaremetalPortGroup")

    def get_parser(self, prog_name):
        parser = super(SetBaremetalPortGroup, self).get_parser(prog_name)

        parser.add_argument(
            'portgroup',
            metavar='<port group>',
            help=_("Name or UUID of the port group."),
        )
        parser.add_argument(
            '--node',
            dest='node_uuid',
            metavar='<uuid>',
            help=_('Update UUID of the node that this port group belongs to.')
        )
        parser.add_argument(
            "--address",
            metavar="<mac-address>",
            help=_("MAC address for this port group."),
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            help=_("Name of the port group."),
        )
        parser.add_argument(
            "--extra",
            metavar="<key=value>",
            action='append',
            help=_('Extra to set on this baremetal port group '
                   '(repeat option to set multiple extras).'),
        )
        parser.add_argument(
            '--mode',
            help=_('Mode of the port group. For possible values, refer to '
                   'https://www.kernel.org/doc/Documentation/networking'
                   '/bonding.txt.'))
        parser.add_argument(
            '--property',
            dest='properties',
            metavar="<key=value>",
            action='append',
            help=_("Key/value property related to this port group's "
                   "configuration (repeat option to set multiple "
                   "properties)."))
        standalone_ports_group = parser.add_mutually_exclusive_group()
        standalone_ports_group.add_argument(
            '--support-standalone-ports',
            action='store_true',
            default=None,
            help=_("Ports that are members of this port group "
                   "can be used as stand-alone ports.")
        )
        standalone_ports_group.add_argument(
            '--unsupport-standalone-ports',
            action='store_true',
            help=_("Ports that are members of this port group "
                   "cannot be used as stand-alone ports.")
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        properties = []
        if parsed_args.node_uuid:
            properties.extend(utils.args_array_to_patch(
                'add', ["node_uuid=%s" % parsed_args.node_uuid]))
        if parsed_args.address:
            properties.extend(utils.args_array_to_patch(
                'add', ["address=%s" % parsed_args.address]))
        if parsed_args.name:
            name = ["name=%s" % parsed_args.name]
            properties.extend(utils.args_array_to_patch(
                'add', name))
        if parsed_args.support_standalone_ports:
            properties.extend(utils.args_array_to_patch(
                'add', ["standalone_ports_supported=True"]))
        if parsed_args.unsupport_standalone_ports:
            properties.extend(utils.args_array_to_patch(
                'add', ["standalone_ports_supported=False"]))
        if parsed_args.mode:
            properties.extend(utils.args_array_to_patch(
                'add', ["mode=\"%s\"" % parsed_args.mode]))

        if parsed_args.extra:
            properties.extend(utils.args_array_to_patch(
                'add', ['extra/' + x for x in parsed_args.extra]))
        if parsed_args.properties:
            properties.extend(utils.args_array_to_patch(
                'add', ['properties/' + x for x in parsed_args.properties]))

        if properties:
            baremetal_client.portgroup.update(parsed_args.portgroup,
                                              properties)
        else:
            self.log.warning("Please specify what to set.")


class UnsetBaremetalPortGroup(command.Command):
    """Unset baremetal port group properties."""
    log = logging.getLogger(__name__ + ".UnsetBaremetalPortGroup")

    def get_parser(self, prog_name):
        parser = super(UnsetBaremetalPortGroup, self).get_parser(prog_name)

        parser.add_argument(
            'portgroup',
            metavar='<port group>',
            help=_("Name or UUID of the port group.")
        )
        parser.add_argument(
            "--name",
            action='store_true',
            help=_("Unset the name of the port group."),
        )
        parser.add_argument(
            "--address",
            action='store_true',
            help=_("Unset the address of the port group."),
        )
        parser.add_argument(
            "--extra",
            metavar="<key>",
            action='append',
            help=_('Extra to unset on this baremetal port group '
                   '(repeat option to unset multiple extras).'),
        )
        parser.add_argument(
            "--property",
            dest='properties',
            metavar="<key>",
            action='append',
            help=_('Property to unset on this baremetal port group '
                   '(repeat option to unset multiple properties).'),
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        properties = []
        if parsed_args.name:
            properties.extend(utils.args_array_to_patch('remove',
                              ['name']))
        if parsed_args.address:
            properties.extend(utils.args_array_to_patch('remove',
                              ['address']))
        if parsed_args.extra:
            properties.extend(utils.args_array_to_patch('remove',
                              ['extra/' + x for x in parsed_args.extra]))
        if parsed_args.properties:
            properties.extend(utils.args_array_to_patch(
                'remove', ['properties/' + x for x in parsed_args.properties]))

        if properties:
            baremetal_client.portgroup.update(parsed_args.portgroup,
                                              properties)
        else:
            self.log.warning("Please specify what to unset.")
