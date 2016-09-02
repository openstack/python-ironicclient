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


import logging

from osc_lib.command import command
from osc_lib import utils as oscutils

from ironicclient.common import utils
from ironicclient.v1 import resource_fields as res_fields


class ListBaremetalDriver(command.Lister):
    """List the enabled drivers."""

    log = logging.getLogger(__name__ + ".ListBaremetalDriver")

    def get_parser(self, prog_name):
        parser = super(ListBaremetalDriver, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)" % parsed_args)
        client = self.app.client_manager.baremetal

        labels = ['Supported driver(s)', 'Active host(s)']
        columns = ['name', 'hosts']

        drivers = client.driver.list()
        drivers = oscutils.sort_items(drivers, 'name')
        for d in drivers:
            d.hosts = ', '.join(d.hosts)

        return (labels,
                (oscutils.get_item_properties(s, columns) for s in drivers))


class PassthruCallBaremetalDriver(command.ShowOne):
    """Call a vendor passthru method for a driver."""

    log = logging.getLogger(__name__ + ".PassthruCallBaremetalDriver")
    http_methods = ['POST', 'PUT', 'GET', 'DELETE', 'PATCH']

    def get_parser(self, prog_name):
        parser = super(PassthruCallBaremetalDriver, self).get_parser(prog_name)
        parser.add_argument(
            'driver',
            metavar='<driver>',
            help='Name of the driver.'
        )
        parser.add_argument(
            'method',
            metavar='<method>',
            help="Vendor passthru method to be called."
        )
        parser.add_argument(
            '--arg',
            metavar='<key=value>',
            action='append',
            help="Argument to pass to the passthru method (repeat option "
                 "to specify multiple arguments)."
        )
        parser.add_argument(
            '--http-method',
            dest='http_method',
            metavar='<http-method>',
            choices=self.http_methods,
            default='POST',
            help="The HTTP method to use in the passthru request. One of "
                 "%s. Defaults to 'POST'." %
                 oscutils.format_list(self.http_methods)
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        baremetal_client = self.app.client_manager.baremetal

        arguments = utils.key_value_pairs_to_dict(parsed_args.arg)
        response = (baremetal_client.driver.
                    vendor_passthru(parsed_args.driver,
                                    parsed_args.method,
                                    http_method=parsed_args.http_method,
                                    args=arguments))

        return self.dict2columns(response)


class PassthruListBaremetalDriver(command.Lister):
    """List available vendor passthru methods for a driver."""

    log = logging.getLogger(__name__ + ".PassthruListBaremetalDriver")

    def get_parser(self, prog_name):
        parser = super(PassthruListBaremetalDriver, self).get_parser(prog_name)
        parser.add_argument(
            'driver',
            metavar='<driver>',
            help='Name of the driver.')
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        baremetal_client = self.app.client_manager.baremetal

        columns = res_fields.VENDOR_PASSTHRU_METHOD_RESOURCE.fields
        labels = res_fields.VENDOR_PASSTHRU_METHOD_RESOURCE.labels

        methods = baremetal_client.driver.get_vendor_passthru_methods(
            parsed_args.driver)

        params = []
        for method, response in methods.items():
            response['name'] = method
            http_methods = ', '.join(response['http_methods'])
            response['http_methods'] = http_methods
            params.append(response)

        return (labels,
                (oscutils.get_dict_properties(s, columns) for s in params))


class ShowBaremetalDriver(command.ShowOne):
    """Show information about a driver."""

    log = logging.getLogger(__name__ + ".ShowBaremetalDriver")

    def get_parser(self, prog_name):
        parser = super(ShowBaremetalDriver, self).get_parser(prog_name)
        parser.add_argument(
            'driver',
            metavar='<driver>',
            help='Name of the driver.')
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        baremetal_client = self.app.client_manager.baremetal

        driver = baremetal_client.driver.get(parsed_args.driver)._info
        driver.pop("links", None)
        driver.pop("properties", None)
        # NOTE(rloo): this will show the hosts as a comma-separated string
        #             whereas 'ironic driver show' displays this as a list
        #             of hosts (eg "host1, host2" vs "[u'host1', u'host2']"
        driver['hosts'] = ', '.join(driver.get('hosts', ()))
        return zip(*sorted(driver.items()))
