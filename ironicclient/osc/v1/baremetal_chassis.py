#
#   Copyright 2016 Intel Corporation
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


class CreateBaremetalChassis(command.ShowOne):
    """Create a new chassis."""

    log = logging.getLogger(__name__ + ".CreateBaremetalChassis")

    def get_parser(self, prog_name):
        parser = super(CreateBaremetalChassis, self).get_parser(prog_name)

        parser.add_argument(
            '--description',
            dest='description',
            metavar='<description>',
            help=_('Description for the chassis')
        )
        parser.add_argument(
            '--extra',
            metavar='<key=value>',
            action='append',
            help=_("Record arbitrary key/value metadata. "
                   "Can be specified multiple times.")
        )
        parser.add_argument(
            '--uuid',
            metavar='<uuid>',
            help=_("Unique UUID of the chassis")
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        field_list = ['description', 'extra', 'uuid']
        fields = dict((k, v) for (k, v) in vars(parsed_args).items()
                      if k in field_list and not (v is None))
        fields = utils.args_array_to_dict(fields, 'extra')
        chassis = baremetal_client.chassis.create(**fields)._info

        chassis.pop('links', None)
        chassis.pop('nodes', None)

        return self.dict2columns(chassis)


class DeleteBaremetalChassis(command.Command):
    """Delete a chassis."""

    log = logging.getLogger(__name__ + ".DeleteBaremetalChassis")

    def get_parser(self, prog_name):
        parser = super(DeleteBaremetalChassis, self).get_parser(prog_name)
        parser.add_argument(
            "chassis",
            metavar="<chassis>",
            nargs="+",
            help=_("UUIDs of chassis to delete")
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        failures = []
        for chassis in parsed_args.chassis:
            try:
                baremetal_client.chassis.delete(chassis)
                print(_('Deleted chassis %s') % chassis)
            except exc.ClientException as e:
                failures.append(_("Failed to delete chassis %(chassis)s: "
                                  "%(error)s")
                                % {'chassis': chassis, 'error': e})

        if failures:
            raise exc.ClientException("\n".join(failures))


class ListBaremetalChassis(command.Lister):
    """List the chassis."""

    log = logging.getLogger(__name__ + ".ListBaremetalChassis")

    def get_parser(self, prog_name):
        parser = super(ListBaremetalChassis, self).get_parser(prog_name)
        display_group = parser.add_mutually_exclusive_group(required=False)
        display_group.add_argument(
            '--fields',
            nargs='+',
            dest='fields',
            metavar='<field>',
            action='append',
            default=[],
            choices=res_fields.CHASSIS_DETAILED_RESOURCE.fields,
            help=_("One or more chassis fields. Only these fields will be "
                   "fetched from the server. Cannot be used when '--long' is "
                   "specified.")
        )
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            type=int,
            help=_('Maximum number of chassis to return per request, '
                   '0 for no limit. Default is the maximum number used '
                   'by the Baremetal API Service.')
        )
        display_group.add_argument(
            '--long',
            default=False,
            action='store_true',
            help=_("Show detailed information about the chassis")
        )
        parser.add_argument(
            '--marker',
            metavar='<chassis>',
            help=_('Chassis UUID (for example, of the last chassis in the '
                   'list from a previous request). Returns the list of '
                   'chassis after this UUID.')
        )
        parser.add_argument(
            '--sort',
            metavar="<key>[:<direction>]",
            help=_('Sort output by specified chassis fields and directions '
                   '(asc or desc) (default: asc). Multiple fields and '
                   'directions can be specified, separated by comma.')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.baremetal

        columns = res_fields.CHASSIS_RESOURCE.fields
        labels = res_fields.CHASSIS_RESOURCE.labels

        params = {}
        if parsed_args.limit is not None and parsed_args.limit < 0:
            raise exc.CommandError(
                _('Expected non-negative --limit, got %s') %
                parsed_args.limit)
        params['limit'] = parsed_args.limit
        params['marker'] = parsed_args.marker
        if parsed_args.long:
            params['detail'] = parsed_args.long
            columns = res_fields.CHASSIS_DETAILED_RESOURCE.fields
            labels = res_fields.CHASSIS_DETAILED_RESOURCE.labels
        elif parsed_args.fields:
            params['detail'] = False
            fields = itertools.chain.from_iterable(parsed_args.fields)
            resource = res_fields.Resource(list(fields))
            columns = resource.fields
            labels = resource.labels
            params['fields'] = columns

        self.log.debug("params(%s)", params)
        data = client.chassis.list(**params)

        data = oscutils.sort_items(data, parsed_args.sort)

        return (labels,
                (oscutils.get_item_properties(s, columns, formatters={
                    'Properties': oscutils.format_dict},) for s in data))


class SetBaremetalChassis(command.Command):
    """Set chassis properties."""

    log = logging.getLogger(__name__ + ".SetBaremetalChassis")

    def get_parser(self, prog_name):
        parser = super(SetBaremetalChassis, self).get_parser(prog_name)

        parser.add_argument(
            'chassis',
            metavar='<chassis>',
            help=_("UUID of the chassis")
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help=_("Set the description of the chassis")
        )
        parser.add_argument(
            "--extra",
            metavar="<key=value>",
            action='append',
            help=_('Extra to set on this chassis '
                   '(repeat option to set multiple extras)')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        properties = []
        if parsed_args.description:
            description = ["description=%s" % parsed_args.description]
            properties.extend(utils.args_array_to_patch(
                'add', description))
        if parsed_args.extra:
            properties.extend(utils.args_array_to_patch(
                'add', ['extra/' + x for x in parsed_args.extra]))

        if properties:
            baremetal_client.chassis.update(parsed_args.chassis, properties)
        else:
            self.log.warning("Please specify what to set.")


class ShowBaremetalChassis(command.ShowOne):
    """Show chassis details."""

    log = logging.getLogger(__name__ + ".ShowBaremetalChassis")

    def get_parser(self, prog_name):
        parser = super(ShowBaremetalChassis, self).get_parser(prog_name)
        parser.add_argument(
            "chassis",
            metavar="<chassis>",
            help=_("UUID of the chassis")
        )
        parser.add_argument(
            '--fields',
            nargs='+',
            dest='fields',
            metavar='<field>',
            action='append',
            choices=res_fields.CHASSIS_DETAILED_RESOURCE.fields,
            default=[],
            help=_("One or more chassis fields. Only these fields will be "
                   "fetched from the server.")
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal
        fields = list(itertools.chain.from_iterable(parsed_args.fields))
        fields = fields if fields else None
        chassis = baremetal_client.chassis.get(parsed_args.chassis,
                                               fields=fields)._info
        chassis.pop("links", None)
        chassis.pop("nodes", None)

        return zip(*sorted(chassis.items()))


class UnsetBaremetalChassis(command.Command):
    """Unset chassis properties."""
    log = logging.getLogger(__name__ + ".UnsetBaremetalChassis")

    def get_parser(self, prog_name):
        parser = super(UnsetBaremetalChassis, self).get_parser(prog_name)

        parser.add_argument(
            'chassis',
            metavar='<chassis>',
            help=_("UUID of the chassis")
        )
        parser.add_argument(
            '--description',
            action='store_true',
            default=False,
            help=_('Clear the chassis description')
        )
        parser.add_argument(
            "--extra",
            metavar="<key>",
            action='append',
            help=_('Extra to unset on this chassis '
                   '(repeat option to unset multiple extras)')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        properties = []
        if parsed_args.description:
            properties.extend(utils.args_array_to_patch('remove',
                              ['description']))
        if parsed_args.extra:
            properties.extend(utils.args_array_to_patch('remove',
                              ['extra/' + x for x in parsed_args.extra]))

        if properties:
            baremetal_client.chassis.update(parsed_args.chassis, properties)
        else:
            self.log.warning("Please specify what to unset.")
