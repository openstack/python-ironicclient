# Copyright 2013 Red Hat, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import argparse

from ironicclient.common import cliutils
from ironicclient.common import utils
from ironicclient.v1 import resource_fields as res_fields
from ironicclient.v1 import utils as v1_utils


def _print_driver_show(driver, json=False):
    fields = res_fields.DRIVER_DETAILED_RESOURCE.fields
    data = dict([(f, getattr(driver, f, '')) for f in fields])
    cliutils.print_dict(data, wrap=72, json_flag=json)


@cliutils.arg('-t', '--type',
              metavar='<type>',
              choices=["classic", "dynamic"],
              help='Type of driver ("classic" or "dynamic"). '
                   'The default is to list all of them.')
@cliutils.arg('--detail',
              dest='detail',
              action='store_true',
              default=None,
              help="Show detailed information about the drivers.")
def do_driver_list(cc, args):
    """List the enabled drivers."""
    drivers = cc.driver.list(driver_type=args.type, detail=args.detail)
    # NOTE(lucasagomes): For list-type properties, show the values as
    # comma separated strings. It's easier to read.
    data = [utils.convert_list_props_to_comma_separated(d._info)
            for d in drivers]

    if args.detail:
        field_labels = res_fields.DRIVER_DETAILED_RESOURCE.labels
        fields = res_fields.DRIVER_DETAILED_RESOURCE.fields
    else:
        field_labels = res_fields.DRIVER_RESOURCE.labels
        fields = res_fields.DRIVER_RESOURCE.fields

    cliutils.print_list(data, fields, field_labels=field_labels,
                        json_flag=args.json)


@cliutils.arg('driver_name', metavar='<driver>',
              help='Name of the driver.')
def do_driver_show(cc, args):
    """Show information about a driver."""
    driver = cc.driver.get(args.driver_name)
    _print_driver_show(driver, json=args.json)


@cliutils.arg('driver_name', metavar='<driver>',
              help="Name of the driver.")
@cliutils.arg('--wrap', dest='wrap', metavar='<integer>',
              type=int, default=0,
              help=('Wrap the output to a specified length. '
                    'Positive number can realize wrap functionality. '
                    '0 is default for disabled.'))
def do_driver_properties(cc, args):
    """Get properties of a driver."""
    properties = cc.driver.properties(args.driver_name)
    cliutils.print_dict(
        properties,
        wrap=args.wrap,
        dict_value='Description',
        json_flag=args.json)


@cliutils.arg('driver_name', metavar='<driver>',
              help="Name of the driver.")
@cliutils.arg('--wrap', dest='wrap', metavar='<integer>',
              type=int, default=0,
              help=('Wrap the output to a specified length. '
                    'Positive number can realize wrap functionality. '
                    '0 is default for disabled.'))
def do_driver_raid_logical_disk_properties(cc, args):
    """Get RAID logical disk properties for a driver."""
    properties = cc.driver.raid_logical_disk_properties(args.driver_name)
    cliutils.print_dict(
        properties,
        wrap=args.wrap,
        dict_value='Description')


@cliutils.arg('driver_name',
              metavar='<driver>',
              help='Name of the driver.')
@cliutils.arg('method',
              metavar='<method>',
              help="Vendor-passthru method to be called.")
@cliutils.arg('arguments',
              metavar='<arg=value>',
              nargs='*',
              action='append',
              default=[],
              help="Argument to be passed to the vendor-passthru method. "
                   "Can be specified multiple times.")
@cliutils.arg('--http-method',
              metavar='<http-method>',
              choices=v1_utils.HTTP_METHODS,
              help=("The HTTP method to use in the request. Valid HTTP "
                    "methods are: %s. Defaults to 'POST'." %
                    ', '.join(v1_utils.HTTP_METHODS)))
@cliutils.arg('--http_method',
              help=argparse.SUPPRESS)
def do_driver_vendor_passthru(cc, args):
    """Call a vendor-passthru extension for a driver."""
    arguments = utils.key_value_pairs_to_dict(args.arguments[0])

    resp = cc.driver.vendor_passthru(args.driver_name, args.method,
                                     http_method=args.http_method,
                                     args=arguments)
    if resp:
        # Print the raw response we don't know how it should be formated
        print(str(resp.to_dict()))


@cliutils.arg('driver_name',
              metavar='<driver>',
              help='Name of the driver.')
def do_driver_get_vendor_passthru_methods(cc, args):
    """Get the vendor passthru methods for a driver."""
    methods = cc.driver.get_vendor_passthru_methods(args.driver_name)
    data = []
    for method, response in methods.items():
        response['name'] = method
        http_methods = ','.join(response['http_methods'])
        response['http_methods'] = http_methods
        data.append(response)
    fields = res_fields.VENDOR_PASSTHRU_METHOD_RESOURCE.fields
    field_labels = res_fields.VENDOR_PASSTHRU_METHOD_RESOURCE.labels
    cliutils.print_list(data, fields,
                        field_labels=field_labels,
                        sortby_index=None,
                        json_flag=args.json)
