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

from __future__ import annotations

import argparse
from collections.abc import Iterable, Sequence
import itertools
import logging
from typing import Any
from typing import cast

from osc_lib import utils as oscutils

from ironicclient.common.i18n import _
from ironicclient.common import utils
from ironicclient import exc
from ironicclient.osc import command
from ironicclient.v1 import resource_fields as res_fields


class ListBaremetalConductor(command.Lister):
    """List baremetal conductors"""

    log: logging.Logger = logging.getLogger(
        __name__ + ".ListBaremetalConductor")

    def get_parser(  # type: ignore[override]
        self, prog_name: str,
    ) -> argparse.ArgumentParser:
        parser: argparse.ArgumentParser
        parser = super().get_parser(prog_name)
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

    def take_action(
        self, parsed_args: argparse.Namespace,
    ) -> tuple[Sequence[str], Iterable[Any]]:
        self.log.debug("take_action(%s)", parsed_args)
        manager = self.app.client_manager
        client = manager.baremetal

        columns = res_fields.CONDUCTOR_RESOURCE.fields

        params: dict[str, object] = {}
        if parsed_args.limit is not None and parsed_args.limit < 0:
            raise exc.CommandError(
                _('Expected non-negative --limit, got %s') %
                parsed_args.limit)
        params['limit'] = parsed_args.limit
        params['marker'] = parsed_args.marker
        if parsed_args.long:
            params['detail'] = parsed_args.long
            columns = res_fields.CONDUCTOR_DETAILED_RESOURCE.fields
        elif parsed_args.fields:
            params['detail'] = False
            fields = itertools.chain.from_iterable(parsed_args.fields)
            resource = res_fields.Resource(list(fields))
            columns = resource.fields
            params['fields'] = columns

        self.log.debug("params(%s)", params)
        data = client.conductor.list(**params)

        data = oscutils.sort_items(data, parsed_args.sort)

        return (columns,
                (oscutils.get_item_properties(s, columns, formatters={
                    'Properties': utils.HashColumn},) for s in data))


class ShowBaremetalConductor(command.ShowOne):
    """Show baremetal conductor details"""

    log: logging.Logger = logging.getLogger(
        __name__ + ".ShowBaremetalConductor")

    def get_parser(  # type: ignore[override]
        self, prog_name: str,
    ) -> argparse.ArgumentParser:
        parser: argparse.ArgumentParser
        parser = super().get_parser(prog_name)
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

    def take_action(
        self, parsed_args: argparse.Namespace,
    ) -> tuple[Sequence[str], Iterable[Any]]:
        self.log.debug("take_action(%s)", parsed_args)

        manager = self.app.client_manager
        baremetal_client = manager.baremetal
        fields: list[str] | None
        fields = (
            list(itertools.chain.from_iterable(parsed_args.fields))
            or None)
        conductor = baremetal_client.conductor.get(
            parsed_args.conductor, fields=fields)._info
        conductor.pop("links", None)

        return cast(
            tuple[Sequence[str], Iterable[Any]],
            self.dict2columns(conductor),
        )
