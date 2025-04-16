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
from ironicclient import exc
from ironicclient.v1 import resource_fields as res_fields


class ListBaremetalConductor(command.Lister):
    """List baremetal conductors"""

    log = logging.getLogger(__name__ + ".ListBaremetalNode")

    def get_parser(self, prog_name):
        parser = super(ListBaremetalConductor, self).get_parser(prog_name)
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            type=int,
            help=_('Maximum number of conductors to return per request, '
                   '0 for no limit. Default is the maximum number used '
                   'by the Baremetal API Service.')
        )
        parser.add_argument(
            '--marker',
            metavar='<conductor>',
            help=_('Hostname of the conductor (for example, of the last '
                   'conductor in the list from a previous request). Returns '
                   'the list of conductors after this conductor.')
        )
        parser.add_argument(
            '--sort',
            metavar="<key>[:<direction>]",
            help=_('Sort output by specified conductor fields and directions '
                   '(asc or desc) (default: asc). Multiple fields and '
                   'directions can be specified, separated by comma.'),
        )
        display_group = parser.add_mutually_exclusive_group(required=False)
        display_group.add_argument(
            '--long',
            default=False,
            help=_("Show detailed information about the conductors."),
            action='store_true')
        display_group.add_argument(
            '--fields',
            nargs='+',
            dest='fields',
            metavar='<field>',
            action='append',
            default=[],
            choices=res_fields.CONDUCTOR_DETAILED_RESOURCE.fields,
            help=_("One or more conductor fields. Only these fields will be "
                   "fetched from the server. Can not be used when '--long' "
                   "is specified."))
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.baremetal

        columns = res_fields.CONDUCTOR_RESOURCE.fields
        labels = res_fields.CONDUCTOR_RESOURCE.labels

        params = {}
        if parsed_args.limit is not None and parsed_args.limit < 0:
            raise exc.CommandError(
                _('Expected non-negative --limit, got %s') %
                parsed_args.limit)
        params['limit'] = parsed_args.limit
        params['marker'] = parsed_args.marker
        if parsed_args.long:
            params['detail'] = parsed_args.long
            columns = res_fields.CONDUCTOR_DETAILED_RESOURCE.fields
            labels = res_fields.CONDUCTOR_DETAILED_RESOURCE.labels
        elif parsed_args.fields:
            params['detail'] = False
            fields = itertools.chain.from_iterable(parsed_args.fields)
            resource = res_fields.Resource(list(fields))
            columns = resource.fields
            labels = resource.labels
            params['fields'] = columns

        self.log.debug("params(%s)", params)
        data = client.conductor.list(**params)

        data = oscutils.sort_items(data, parsed_args.sort)

        return (labels,
                (oscutils.get_item_properties(s, columns, formatters={
                    'Properties': oscutils.format_dict},) for s in data))


class ShowBaremetalConductor(command.ShowOne):
    """Show baremetal conductor details"""

    log = logging.getLogger(__name__ + ".ShowBaremetalConductor")

    def get_parser(self, prog_name):
        parser = super(ShowBaremetalConductor, self).get_parser(prog_name)
        parser.add_argument(
            "conductor",
            metavar="<conductor>",
            help=_("Hostname of the conductor"))
        parser.add_argument(
            '--fields',
            nargs='+',
            dest='fields',
            metavar='<field>',
            action='append',
            choices=res_fields.CONDUCTOR_DETAILED_RESOURCE.fields,
            default=[],
            help=_("One or more conductor fields. Only these fields will be "
                   "fetched from the server."))
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal
        fields = list(itertools.chain.from_iterable(parsed_args.fields))
        fields = fields if fields else None
        conductor = baremetal_client.conductor.get(
            parsed_args.conductor, fields=fields)._info
        conductor.pop("links", None)

        return self.dict2columns(conductor)
