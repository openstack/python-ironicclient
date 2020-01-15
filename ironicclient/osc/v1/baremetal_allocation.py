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


class CreateBaremetalAllocation(command.ShowOne):
    """Create a new baremetal allocation."""

    log = logging.getLogger(__name__ + ".CreateBaremetalAllocation")

    def get_parser(self, prog_name):
        parser = super(CreateBaremetalAllocation, self).get_parser(prog_name)

        parser.add_argument(
            '--resource-class',
            dest='resource_class',
            help=_('Resource class to request.'))
        parser.add_argument(
            '--trait',
            action='append',
            dest='traits',
            help=_('A trait to request. Can be specified multiple times.'))
        parser.add_argument(
            '--candidate-node',
            action='append',
            dest='candidate_nodes',
            help=_('A candidate node for this allocation. Can be specified '
                   'multiple times. If at least one is specified, only the '
                   'provided candidate nodes are considered for the '
                   'allocation.'))
        parser.add_argument(
            '--name',
            dest='name',
            help=_('Unique name of the allocation.'))
        parser.add_argument(
            '--uuid',
            dest='uuid',
            help=_('UUID of the allocation.'))
        parser.add_argument(
            '--owner',
            dest='owner',
            help=_('Owner of the allocation.'))
        parser.add_argument(
            '--extra',
            metavar="<key=value>",
            action='append',
            help=_("Record arbitrary key/value metadata. "
                   "Can be specified multiple times."))
        parser.add_argument(
            '--wait',
            type=int,
            dest='wait_timeout',
            default=None,
            metavar='<time-out>',
            const=0,
            nargs='?',
            help=_("Wait for the new allocation to become active. An error "
                   "is returned if allocation fails and --wait is used. "
                   "Optionally takes a timeout value (in seconds). The "
                   "default value is 0, meaning it will wait indefinitely."))
        parser.add_argument(
            '--node',
            help=_("Backfill this allocation from the provided node that has "
                   "already been deployed. Bypasses the normal allocation "
                   "process."))

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        baremetal_client = self.app.client_manager.baremetal

        if not parsed_args.node and not parsed_args.resource_class:
            raise exc.ClientException(
                _('--resource-class is required except when --node is used'))

        field_list = ['name', 'uuid', 'extra', 'resource_class', 'traits',
                      'candidate_nodes', 'node', 'owner']
        fields = dict((k, v) for (k, v) in vars(parsed_args).items()
                      if k in field_list and v is not None)

        fields = utils.args_array_to_dict(fields, 'extra')
        allocation = baremetal_client.allocation.create(**fields)
        if parsed_args.wait_timeout is not None:
            allocation = baremetal_client.allocation.wait(
                allocation.uuid, timeout=parsed_args.wait_timeout)

        data = dict([(f, getattr(allocation, f, '')) for f in
                     res_fields.ALLOCATION_DETAILED_RESOURCE.fields])

        return self.dict2columns(data)


class ShowBaremetalAllocation(command.ShowOne):
    """Show baremetal allocation details."""

    log = logging.getLogger(__name__ + ".ShowBaremetalAllocation")

    def get_parser(self, prog_name):
        parser = super(ShowBaremetalAllocation, self).get_parser(prog_name)
        parser.add_argument(
            "allocation",
            metavar="<id>",
            help=_("UUID or name of the allocation"))
        parser.add_argument(
            '--fields',
            nargs='+',
            dest='fields',
            metavar='<field>',
            action='append',
            choices=res_fields.ALLOCATION_DETAILED_RESOURCE.fields,
            default=[],
            help=_("One or more allocation fields. Only these fields will be "
                   "fetched from the server."))
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal
        fields = list(itertools.chain.from_iterable(parsed_args.fields))
        fields = fields if fields else None

        allocation = baremetal_client.allocation.get(
            parsed_args.allocation, fields=fields)._info

        allocation.pop("links", None)
        return zip(*sorted(allocation.items()))


class ListBaremetalAllocation(command.Lister):
    """List baremetal allocations."""

    log = logging.getLogger(__name__ + ".ListBaremetalAllocation")

    def get_parser(self, prog_name):
        parser = super(ListBaremetalAllocation, self).get_parser(prog_name)
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            type=int,
            help=_('Maximum number of allocations to return per request, '
                   '0 for no limit. Default is the maximum number used '
                   'by the Baremetal API Service.'))
        parser.add_argument(
            '--marker',
            metavar='<allocation>',
            help=_('Allocation UUID (for example, of the last allocation in '
                   'the list from a previous request). Returns the list of '
                   'allocations after this UUID.'))
        parser.add_argument(
            '--sort',
            metavar="<key>[:<direction>]",
            help=_('Sort output by specified allocation fields and directions '
                   '(asc or desc) (default: asc). Multiple fields and '
                   'directions can be specified, separated by comma.'))
        parser.add_argument(
            '--node',
            metavar='<node>',
            help=_("Only list allocations of this node (name or UUID)."))
        parser.add_argument(
            '--resource-class',
            metavar='<resource_class>',
            help=_("Only list allocations with this resource class."))
        parser.add_argument(
            '--state',
            metavar='<state>',
            help=_("Only list allocations in this state."))
        parser.add_argument(
            '--owner',
            metavar='<owner>',
            help=_("Only list allocations with this owner."))

        # NOTE(dtantsur): the allocation API does not expose the 'detail' flag,
        # but some fields are inconvenient to display in a table, so we emulate
        # it on the client side.
        display_group = parser.add_mutually_exclusive_group(required=False)
        display_group.add_argument(
            '--long',
            default=False,
            help=_("Show detailed information about the allocations."),
            action='store_true')
        display_group.add_argument(
            '--fields',
            nargs='+',
            dest='fields',
            metavar='<field>',
            action='append',
            default=[],
            choices=res_fields.ALLOCATION_DETAILED_RESOURCE.fields,
            help=_("One or more allocation fields. Only these fields will be "
                   "fetched from the server. Can not be used when '--long' "
                   "is specified."))
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.baremetal

        params = {}
        if parsed_args.limit is not None and parsed_args.limit < 0:
            raise exc.CommandError(
                _('Expected non-negative --limit, got %s') %
                parsed_args.limit)
        params['limit'] = parsed_args.limit
        params['marker'] = parsed_args.marker
        for field in ('node', 'resource_class', 'state', 'owner'):
            value = getattr(parsed_args, field)
            if value is not None:
                params[field] = value

        if parsed_args.long:
            columns = res_fields.ALLOCATION_DETAILED_RESOURCE.fields
            labels = res_fields.ALLOCATION_DETAILED_RESOURCE.labels
        elif parsed_args.fields:
            fields = itertools.chain.from_iterable(parsed_args.fields)
            resource = res_fields.Resource(list(fields))
            columns = resource.fields
            labels = resource.labels
            params['fields'] = columns
        else:
            columns = res_fields.ALLOCATION_RESOURCE.fields
            labels = res_fields.ALLOCATION_RESOURCE.labels

        self.log.debug("params(%s)", params)
        data = client.allocation.list(**params)

        data = oscutils.sort_items(data, parsed_args.sort)

        return (labels,
                (oscutils.get_item_properties(s, columns) for s in data))


class DeleteBaremetalAllocation(command.Command):
    """Unregister baremetal allocation(s)."""

    log = logging.getLogger(__name__ + ".DeleteBaremetalAllocation")

    def get_parser(self, prog_name):
        parser = super(DeleteBaremetalAllocation, self).get_parser(prog_name)
        parser.add_argument(
            "allocations",
            metavar="<allocation>",
            nargs="+",
            help=_("Allocations(s) to delete (name or UUID)."))

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        failures = []
        for allocation in parsed_args.allocations:
            try:
                baremetal_client.allocation.delete(allocation)
                print(_('Deleted allocation %s') % allocation)
            except exc.ClientException as e:
                failures.append(_("Failed to delete allocation "
                                  "%(allocation)s:  %(error)s")
                                % {'allocation': allocation, 'error': e})

        if failures:
            raise exc.ClientException("\n".join(failures))


class SetBaremetalAllocation(command.Command):
    """Set baremetal allocation properties."""

    log = logging.getLogger(__name__ + ".SetBaremetalAllocation")

    def get_parser(self, prog_name):
        parser = super(SetBaremetalAllocation, self).get_parser(prog_name)

        parser.add_argument(
            "allocation",
            metavar="<allocation>",
            help=_("Name or UUID of the allocation")
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            help=_("Set the name of the allocation")
        )
        parser.add_argument(
            "--extra",
            metavar="<key=value>",
            action="append",
            help=_("Extra property to set on this allocation "
                   "(repeat option to set multiple extra properties)")
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        properties = []
        if parsed_args.name:
            properties.extend(utils.args_array_to_patch(
                'add', ["name=%s" % parsed_args.name]))
        if parsed_args.extra:
            properties.extend(utils.args_array_to_patch(
                'add', ["extra/" + x for x in parsed_args.extra]))

        if properties:
            baremetal_client.allocation.update(
                parsed_args.allocation, properties)
        else:
            self.log.warning("Please specify what to set.")


class UnsetBaremetalAllocation(command.Command):
    """Unset baremetal allocation properties."""
    log = logging.getLogger(__name__ + ".UnsetBaremetalAllocation")

    def get_parser(self, prog_name):
        parser = super(UnsetBaremetalAllocation, self).get_parser(
            prog_name)

        parser.add_argument(
            "allocation",
            metavar="<allocation>",
            help=_("Name or UUID of the allocation")
        )
        parser.add_argument(
            "--name",
            action="store_true",
            default=False,
            help=_("Unset the name of the allocation")
        )
        parser.add_argument(
            "--extra",
            metavar="<key>",
            action='append',
            help=_('Extra property to unset on this baremetal allocation '
                   '(repeat option to unset multiple extra property).'),
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        properties = []
        if parsed_args.name:
            properties.extend(utils.args_array_to_patch('remove',
                              ['name']))
        if parsed_args.extra:
            properties.extend(utils.args_array_to_patch('remove',
                              ['extra/' + x for x in parsed_args.extra]))

        if properties:
            baremetal_client.allocation.update(parsed_args.allocation,
                                               properties)
        else:
            self.log.warning("Please specify what to unset.")
