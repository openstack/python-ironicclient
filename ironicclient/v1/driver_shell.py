# -*- coding: utf-8 -*-
#
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

from ironicclient.common import utils
from ironicclient.openstack.common import cliutils


def _print_driver_show(driver):
    fields = ['name', 'hosts']
    data = dict([(f, getattr(driver, f, '')) for f in fields])
    cliutils.print_dict(data, wrap=72)


def do_driver_list(cc, args):
    """List drivers."""
    drivers = cc.driver.list()
    # NOTE(lucasagomes): Separate each host by a comma.
    # It's easier to read.
    for d in drivers:
        d.hosts = ', '.join(d.hosts)
    field_labels = ['Supported driver(s)', 'Active host(s)']
    fields = ['name', 'hosts']
    cliutils.print_list(drivers, fields, field_labels)


@cliutils.arg('driver_name', metavar='<driver_name>',
              help='Name of the driver')
def do_driver_show(cc, args):
    """Show a driver."""
    driver = cc.driver.get(args.driver_name)
    _print_driver_show(driver)


@cliutils.arg('driver_name',
              metavar='<driver_name>',
              help='Name of the driver')
@cliutils.arg('method',
              metavar='<method>',
              help="vendor-passthru method to be called")
@cliutils.arg('arguments',
              metavar='<arg=value>',
              nargs='*',
              action='append',
              default=[],
              help="arguments to be passed to vendor-passthru method")
def do_driver_vendor_passthru(cc, args):
    """Call a vendor-passthru extension for a driver."""
    fields = {}
    fields['driver_name'] = args.driver_name
    fields['method'] = args.method
    fields['args'] = args.arguments[0]
    fields = utils.args_array_to_dict(fields, 'args')

    # If there were no arguments for the method, fields['args'] will still
    # be an empty list. So make it an empty dict.
    if not fields['args']:
        fields['args'] = {}
    cc.driver.vendor_passthru(**fields)
