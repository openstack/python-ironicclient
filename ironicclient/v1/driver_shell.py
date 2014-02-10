# coding: utf-8
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
