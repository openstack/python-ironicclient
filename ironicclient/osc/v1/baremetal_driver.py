#  Copyright (c) 2016 Mirantis, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
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
from ironicclient.osc import command
from ironicclient.v1 import resource_fields as res_fields
from ironicclient.v1 import utils as v1_utils


class ListBaremetalDriver(command.Lister):
    """List the enabled drivers."""

    log: logging.Logger = logging.getLogger(
        __name__ + ".ListBaremetalDriver")

    def get_parser(  # type: ignore[override]
        self, prog_name: str,
    ) -> argparse.ArgumentParser:
        parser: argparse.ArgumentParser
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--type',
            metavar='<type>',
            choices=["classic", "dynamic"],
            help='Type of driver ("classic" or "dynamic"). '
                 'The default is to list all of them.'
        )
        display_group = parser.add_mutually_exclusive_group()
        display_group.add_argument(
            '--long',
            action='store_true',
            default=None,
            help="Show detailed information about the drivers.")
        display_group.add_argument(
            '--fields',
            nargs='+',
            dest='fields',
            metavar='<field>',
            action='append',
            default=[],
            choices=res_fields.DRIVER_DETAILED_RESOURCE.fields,
            help=_("One or more node fields. Only these fields will be "
                   "fetched from the server. Can not be used when '--long' "
                   "is specified."))
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace,
    ) -> tuple[Sequence[str], Iterable[Any]]:
        self.log.debug("take_action(%s)", parsed_args)
        manager = self.app.client_manager
        client = manager.baremetal

        params: dict[str, object] = {
            'driver_type': parsed_args.type,
            'detail': parsed_args.long,
        }
        if parsed_args.long:
            columns = res_fields.DRIVER_DETAILED_RESOURCE.fields
        elif parsed_args.fields:
            fields = itertools.chain.from_iterable(parsed_args.fields)
            resource = res_fields.Resource(list(fields))
            columns = resource.fields
            params['fields'] = columns
        else:
            columns = res_fields.DRIVER_RESOURCE.fields

        drivers = client.driver.list(**params)
        drivers = oscutils.sort_items(drivers, 'name')

        # For list-type properties, show the values as comma separated
        # strings. It's easier to read.
        data = [utils.convert_list_props_to_comma_separated(d._info)
                for d in drivers]

        return (columns,
                (oscutils.get_dict_properties(s, columns) for s in data))


class ListBaremetalDriverProperty(command.Lister):
    """List the driver properties."""

    log: logging.Logger = logging.getLogger(
        __name__ + ".ListBaremetalDriverProperty")

    def get_parser(  # type: ignore[override]
        self, prog_name: str,
    ) -> argparse.ArgumentParser:
        parser: argparse.ArgumentParser
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'driver',
            metavar='<driver>',
            help='Name of the driver.')
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace,
    ) -> tuple[Sequence[str], Iterable[Any]]:
        self.log.debug("take_action(%s)", parsed_args)
        manager = self.app.client_manager
        baremetal_client = manager.baremetal

        driver_properties = baremetal_client.driver.properties(
            parsed_args.driver)
        columns = ['property', 'description']
        return columns, sorted(driver_properties.items())


class ListBaremetalDriverRaidProperty(command.Lister):
    """List a driver's RAID logical disk properties."""

    log: logging.Logger = logging.getLogger(
        __name__ + ".ListBaremetalDriverRaidProperty")

    def get_parser(  # type: ignore[override]
        self, prog_name: str,
    ) -> argparse.ArgumentParser:
        parser: argparse.ArgumentParser
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'driver',
            metavar='<driver>',
            help='Name of the driver.')
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace,
    ) -> tuple[Sequence[str], Iterable[Any]]:
        self.log.debug("take_action(%s)", parsed_args)
        manager = self.app.client_manager
        baremetal_client = manager.baremetal

        raid_props = baremetal_client.driver.raid_logical_disk_properties(
            parsed_args.driver)
        columns = ['property', 'description']
        return columns, sorted(raid_props.items())


class PassthruCallBaremetalDriver(command.ShowOne):
    """Call a vendor passthru method for a driver."""

    log: logging.Logger = logging.getLogger(
        __name__ + ".PassthruCallBaremetalDriver")

    def get_parser(  # type: ignore[override]
        self, prog_name: str,
    ) -> argparse.ArgumentParser:
        parser: argparse.ArgumentParser
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'driver',
            metavar='<driver>',
            help=_('Name of the driver.')
        )
        parser.add_argument(
            'method',
            metavar='<method>',
            help=_("Vendor passthru method to be called.")
        )
        parser.add_argument(
            '--arg',
            metavar='<key=value>',
            action='append',
            help=_("Argument to pass to the passthru method (repeat option "
                   "to specify multiple arguments).")
        )
        parser.add_argument(
            '--http-method',
            dest='http_method',
            metavar='<http-method>',
            choices=v1_utils.HTTP_METHODS,
            default='POST',
            help=_("The HTTP method to use in the passthru request. One of "
                   "%s. Defaults to 'POST'.") %
                 oscutils.format_list(v1_utils.HTTP_METHODS)
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace,
    ) -> tuple[Sequence[str], Iterable[Any]]:
        self.log.debug("take_action(%s)", parsed_args)
        manager = self.app.client_manager
        baremetal_client = manager.baremetal

        arguments = utils.key_value_pairs_to_dict(parsed_args.arg)
        response = (baremetal_client.driver.
                    vendor_passthru(parsed_args.driver,
                                    parsed_args.method,
                                    http_method=parsed_args.http_method,
                                    args=arguments))

        return cast(
            tuple[Sequence[str], Iterable[Any]],
            self.dict2columns(response),
        )


class PassthruListBaremetalDriver(command.Lister):
    """List available vendor passthru methods for a driver."""

    log: logging.Logger = logging.getLogger(
        __name__ + ".PassthruListBaremetalDriver")

    def get_parser(  # type: ignore[override]
        self, prog_name: str,
    ) -> argparse.ArgumentParser:
        parser: argparse.ArgumentParser
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'driver',
            metavar='<driver>',
            help=_('Name of the driver.'))
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace,
    ) -> tuple[Sequence[str], Iterable[Any]]:
        self.log.debug("take_action(%s)", parsed_args)
        manager = self.app.client_manager
        baremetal_client = manager.baremetal

        columns = res_fields.VENDOR_PASSTHRU_METHOD_RESOURCE.fields

        methods = baremetal_client.driver.get_vendor_passthru_methods(
            parsed_args.driver)

        params: list[dict[str, object]] = []
        for method, response in methods.items():
            response['name'] = method
            http_methods = ', '.join(response['http_methods'])
            response['http_methods'] = http_methods
            params.append(response)

        return (columns,
                (oscutils.get_dict_properties(s, columns) for s in params))


class ShowBaremetalDriver(command.ShowOne):
    """Show information about a driver."""

    log: logging.Logger = logging.getLogger(
        __name__ + ".ShowBaremetalDriver")

    def get_parser(  # type: ignore[override]
        self, prog_name: str,
    ) -> argparse.ArgumentParser:
        parser: argparse.ArgumentParser
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'driver',
            metavar='<driver>',
            help=_('Name of the driver.'))
        parser.add_argument(
            '--fields',
            nargs='+',
            dest='fields',
            metavar='<field>',
            action='append',
            default=[],
            choices=res_fields.DRIVER_DETAILED_RESOURCE.fields,
            help=_("One or more node fields. Only these fields will be "
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
        driver = baremetal_client.driver.get(parsed_args.driver,
                                             fields=fields)._info
        driver.pop("links", None)
        driver.pop("properties", None)
        # For list-type properties, show the values as comma separated
        # strings. It's easier to read.
        driver = utils.convert_list_props_to_comma_separated(driver)
        return cast(
            tuple[Sequence[str], Iterable[Any]],
            zip(*sorted(driver.items())),
        )
