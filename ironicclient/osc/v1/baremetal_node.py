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

import argparse
import itertools
import logging

from osc_lib.command import command
from osc_lib import utils as oscutils

from ironicclient.common.i18n import _
from ironicclient.common import utils
from ironicclient import exc
from ironicclient.v1 import resource_fields as res_fields
from ironicclient.v1 import utils as v1_utils


class ProvisionStateBaremetalNode(command.Command):
    """Base provision state class"""

    log = logging.getLogger(__name__ + ".ProvisionStateBaremetalNode")

    def get_parser(self, prog_name):
        parser = super(ProvisionStateBaremetalNode, self).get_parser(prog_name)

        parser.add_argument(
            'node',
            metavar='<node>',
            help="Name or UUID of the node."
        )
        parser.add_argument(
            '--provision-state',
            default=self.PROVISION_STATE,
            required=False,
            choices=[self.PROVISION_STATE],
            help=argparse.SUPPRESS)
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        clean_steps = getattr(parsed_args, 'clean_steps', None)
        if clean_steps == '-':
            clean_steps = utils.get_from_stdin('clean steps')
        if clean_steps:
            clean_steps = utils.handle_json_or_file_arg(clean_steps)

        config_drive = getattr(parsed_args, 'config_drive', None)

        baremetal_client.node.set_provision_state(
            parsed_args.node,
            parsed_args.provision_state,
            configdrive=config_drive,
            cleansteps=clean_steps)


class AbortBaremetalNode(ProvisionStateBaremetalNode):
    """Set provision state of baremetal node to 'abort'"""

    log = logging.getLogger(__name__ + ".AbortBaremetalNode")
    PROVISION_STATE = 'abort'


class AdoptBaremetalNode(ProvisionStateBaremetalNode):
    """Set provision state of baremetal node to 'adopt'"""

    log = logging.getLogger(__name__ + ".AdoptBaremetalNode")
    PROVISION_STATE = 'adopt'


class BootdeviceSetBaremetalNode(command.Command):
    """Set the boot device for a node"""

    log = logging.getLogger(__name__ + ".BootdeviceSetBaremetalNode")

    def get_parser(self, prog_name):
        parser = super(BootdeviceSetBaremetalNode, self).get_parser(prog_name)

        parser.add_argument(
            'node',
            metavar='<node>',
            help="Name or UUID of the node"
        )
        parser.add_argument(
            'device',
            metavar='<device>',
            choices=v1_utils.BOOT_DEVICES,
            help="One of %s" % (oscutils.format_list(v1_utils.BOOT_DEVICES))
        )
        parser.add_argument(
            '--persistent',
            dest='persistent',
            action='store_true',
            default=False,
            help="Make changes persistent for all future boots"
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal
        baremetal_client.node.set_boot_device(
            parsed_args.node,
            parsed_args.device,
            parsed_args.persistent)


class BootdeviceShowBaremetalNode(command.ShowOne):
    """Show the boot device information for a node"""

    log = logging.getLogger(__name__ + ".BootdeviceShowBaremetalNode")

    def get_parser(self, prog_name):
        parser = super(BootdeviceShowBaremetalNode, self).get_parser(prog_name)

        parser.add_argument(
            'node',
            metavar='<node>',
            help="Name or UUID of the node"
        )
        parser.add_argument(
            '--supported',
            dest='supported',
            action='store_true',
            default=False,
            help="Show the supported boot devices"
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal
        if parsed_args.supported:
            info = baremetal_client.node.get_supported_boot_devices(
                parsed_args.node)
            boot_device_list = info.get('supported_boot_devices', [])
            info['supported_boot_devices'] = ', '.join(boot_device_list)
        else:
            info = baremetal_client.node.get_boot_device(parsed_args.node)
        return zip(*sorted(info.items()))


class CleanBaremetalNode(ProvisionStateBaremetalNode):
    """Set provision state of baremetal node to 'clean'"""

    log = logging.getLogger(__name__ + ".CleanBaremetalNode")
    PROVISION_STATE = 'clean'

    def get_parser(self, prog_name):
        parser = super(CleanBaremetalNode, self).get_parser(prog_name)

        parser.add_argument(
            '--clean-steps',
            metavar='<clean-steps>',
            required=True,
            default=None,
            help=("The clean steps in JSON format. May be the path to a file "
                  "containing the clean steps; OR '-', with the clean steps "
                  "being read from standard input; OR a string. The value "
                  "should be a list of clean-step dictionaries; each "
                  "dictionary should have keys 'interface' and 'step', and "
                  "optional key 'args'."))
        return parser


class ConsoleDisableBaremetalNode(command.Command):
    """Disable console access for a node"""

    log = logging.getLogger(__name__ + ".ConsoleDisableBaremetalNode")

    def get_parser(self, prog_name):
        parser = super(ConsoleDisableBaremetalNode, self).get_parser(prog_name)

        parser.add_argument(
            'node',
            metavar='<node>',
            help="Name or UUID of the node"
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal
        baremetal_client.node.set_console_mode(parsed_args.node, False)


class ConsoleEnableBaremetalNode(command.Command):
    """Enable console access for a node"""

    log = logging.getLogger(__name__ + ".ConsoleEnableBaremetalNode")

    def get_parser(self, prog_name):
        parser = super(ConsoleEnableBaremetalNode, self).get_parser(prog_name)

        parser.add_argument(
            'node',
            metavar='<node>',
            help="Name or UUID of the node"
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal
        baremetal_client.node.set_console_mode(parsed_args.node, True)


class ConsoleShowBaremetalNode(command.ShowOne):
    """Show console information for a node"""

    log = logging.getLogger(__name__ + ".ConsoleShowBaremetalNode")

    def get_parser(self, prog_name):
        parser = super(ConsoleShowBaremetalNode, self).get_parser(prog_name)

        parser.add_argument(
            'node',
            metavar='<node>',
            help="Name or UUID of the node"
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal
        info = baremetal_client.node.get_console(parsed_args.node)
        return zip(*sorted(info.items()))


class CreateBaremetalNode(command.ShowOne):
    """Register a new node with the baremetal service"""

    log = logging.getLogger(__name__ + ".CreateBaremetalNode")

    def get_parser(self, prog_name):
        parser = super(CreateBaremetalNode, self).get_parser(prog_name)

        parser.add_argument(
            '--chassis-uuid',
            dest='chassis_uuid',
            metavar='<chassis>',
            help='UUID of the chassis that this node belongs to.')
        parser.add_argument(
            '--driver',
            metavar='<driver>',
            required=True,
            help='Driver used to control the node [REQUIRED].')
        parser.add_argument(
            '--driver-info',
            metavar='<key=value>',
            action='append',
            help='Key/value pair used by the driver, such as out-of-band '
                 'management credentials. Can be specified multiple times.')
        parser.add_argument(
            '--property',
            dest='properties',
            metavar='<key=value>',
            action='append',
            help='Key/value pair describing the physical characteristics of '
                 'the node. This is exported to Nova and used by the '
                 'scheduler. Can be specified multiple times.')
        parser.add_argument(
            '--extra',
            metavar='<key=value>',
            action='append',
            help="Record arbitrary key/value metadata. "
                 "Can be specified multiple times.")
        parser.add_argument(
            '--uuid',
            metavar='<uuid>',
            help="Unique UUID for the node.")
        parser.add_argument(
            '--name',
            metavar='<name>',
            help="Unique name for the node.")
        parser.add_argument(
            '--network-interface',
            metavar='<network_interface>',
            help='Network interface used for switching node to '
                 'cleaning/provisioning networks.')
        parser.add_argument(
            '--resource-class',
            metavar='<resource_class>',
            help='Resource class for mapping nodes to Nova flavors')

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        field_list = ['chassis_uuid', 'driver', 'driver_info',
                      'properties', 'extra', 'uuid', 'name',
                      'network_interface', 'resource_class']
        fields = dict((k, v) for (k, v) in vars(parsed_args).items()
                      if k in field_list and not (v is None))
        fields = utils.args_array_to_dict(fields, 'driver_info')
        fields = utils.args_array_to_dict(fields, 'extra')
        fields = utils.args_array_to_dict(fields, 'properties')
        node = baremetal_client.node.create(**fields)._info

        node.pop('links', None)
        node.pop('ports', None)

        node.setdefault('chassis_uuid', '')

        return self.dict2columns(node)


class DeleteBaremetalNode(command.Command):
    """Unregister baremetal node(s)"""

    log = logging.getLogger(__name__ + ".DeleteBaremetalNode")

    def get_parser(self, prog_name):
        parser = super(DeleteBaremetalNode, self).get_parser(prog_name)
        parser.add_argument(
            "nodes",
            metavar="<node>",
            nargs="+",
            help="Node(s) to delete (name or UUID)")

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        failures = []
        for node in parsed_args.nodes:
            try:
                baremetal_client.node.delete(node)
                print(_('Deleted node %s') % node)
            except exc.ClientException as e:
                failures.append(_("Failed to delete node %(node)s: %(error)s")
                                % {'node': node, 'error': e})

        if failures:
            raise exc.ClientException("\n".join(failures))


class DeleteBaremetal(DeleteBaremetalNode):
    """Unregister a baremetal node. DEPRECATED"""

    # TODO(thrash): Remove after 11-July-2017 during the 'Queens' cycle.
    log = logging.getLogger(__name__ + ".DeleteBaremetal")

    def take_action(self, parsed_args):
        self.log.warning("This command is deprecated. Instead, use "
                         "'openstack baremetal node delete'.")
        super(DeleteBaremetal, self).take_action(parsed_args)


class DeployBaremetalNode(ProvisionStateBaremetalNode):
    """Set provision state of baremetal node to 'deploy'"""

    log = logging.getLogger(__name__ + ".DeployBaremetalNode")
    PROVISION_STATE = 'active'

    def get_parser(self, prog_name):
        parser = super(DeployBaremetalNode, self).get_parser(prog_name)

        parser.add_argument(
            '--config-drive',
            metavar='<config-drive>',
            default=None,
            help=("A gzipped, base64-encoded configuration drive string OR "
                  "the path to the configuration drive file OR the path to a "
                  "directory containing the config drive files. In case it's "
                  "a directory, a config drive will be generated from it. "))
        return parser


class InspectBaremetalNode(ProvisionStateBaremetalNode):
    """Set provision state of baremetal node to 'inspect'"""

    log = logging.getLogger(__name__ + ".InspectBaremetalNode")
    PROVISION_STATE = 'inspect'


class ListBaremetalNode(command.Lister):
    """List baremetal nodes"""

    log = logging.getLogger(__name__ + ".ListBaremetalNode")

    PROVISION_STATES = ['active', 'deleted', 'rebuild', 'inspect', 'provide',
                        'manage', 'clean', 'adopt', 'abort']

    def get_parser(self, prog_name):
        parser = super(ListBaremetalNode, self).get_parser(prog_name)
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            type=int,
            help='Maximum number of nodes to return per request, '
                 '0 for no limit. Default is the maximum number used '
                 'by the Baremetal API Service.'
        )
        parser.add_argument(
            '--marker',
            metavar='<node>',
            help='Node UUID (for example, of the last node in the list from '
                 'a previous request). Returns the list of nodes after this '
                 'UUID.'
        )
        parser.add_argument(
            '--sort',
            metavar="<key>[:<direction>]",
            help='Sort output by specified node fields and directions '
                 '(asc or desc) (default: asc). Multiple fields and '
                 'directions can be specified, separated by comma.',
        )
        parser.add_argument(
            '--maintenance',
            dest='maintenance',
            action='store_true',
            default=False,
            help="List nodes in maintenance mode.",
        )
        parser.add_argument(
            '--associated',
            dest='associated',
            action='store_true',
            default=False,
            help="List only nodes associated with an instance."
        )
        parser.add_argument(
            '--provision-state',
            dest='provision_state',
            metavar='<provision state>',
            choices=self.PROVISION_STATES,
            help="Limit list to nodes in <provision state>. One of %s." % (
                 ", ".join(self.PROVISION_STATES)))
        parser.add_argument(
            '--resource-class',
            dest='resource_class',
            metavar='<resource class>',
            help="Limit list to nodes with resource class <resource class>")
        parser.add_argument(
            '--chassis',
            dest='chassis',
            metavar='<chassis UUID>',
            help="Limit list to nodes of this chassis")
        display_group = parser.add_mutually_exclusive_group(required=False)
        display_group.add_argument(
            '--long',
            default=False,
            help="Show detailed information about the nodes.",
            action='store_true')
        display_group.add_argument(
            '--fields',
            nargs='+',
            dest='fields',
            metavar='<field>',
            action='append',
            default=[],
            choices=res_fields.NODE_DETAILED_RESOURCE.fields,
            help="One or more node fields. Only these fields will be fetched "
                 "from the server. Can not be used when '--long' is "
                 "specified.")
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.baremetal

        columns = res_fields.NODE_RESOURCE.fields
        labels = res_fields.NODE_RESOURCE.labels

        params = {}
        if parsed_args.limit is not None and parsed_args.limit < 0:
            raise exc.CommandError(
                _('Expected non-negative --limit, got %s') %
                parsed_args.limit)
        params['limit'] = parsed_args.limit
        params['marker'] = parsed_args.marker
        if parsed_args.associated:
            params['associated'] = parsed_args.associated
        if parsed_args.maintenance:
            params['maintenance'] = parsed_args.maintenance
        if parsed_args.provision_state:
            params['provision_state'] = parsed_args.provision_state
        if parsed_args.resource_class:
            params['resource_class'] = parsed_args.resource_class
        if parsed_args.chassis:
            params['chassis'] = parsed_args.chassis
        if parsed_args.long:
            params['detail'] = parsed_args.long
            columns = res_fields.NODE_DETAILED_RESOURCE.fields
            labels = res_fields.NODE_DETAILED_RESOURCE.labels
        elif parsed_args.fields:
            params['detail'] = False
            fields = itertools.chain.from_iterable(parsed_args.fields)
            resource = res_fields.Resource(list(fields))
            columns = resource.fields
            labels = resource.labels
            params['fields'] = columns

        self.log.debug("params(%s)", params)
        data = client.node.list(**params)

        data = oscutils.sort_items(data, parsed_args.sort)

        return (labels,
                (oscutils.get_item_properties(s, columns, formatters={
                    'Properties': oscutils.format_dict},) for s in data))


class ListBaremetal(ListBaremetalNode):
    """List baremetal nodes. DEPRECATED"""

    # TODO(thrash): Remove after 11-July-2017 during the 'Queens' cycle.
    log = logging.getLogger(__name__ + ".ListBaremetal")

    def take_action(self, parsed_args):
        self.log.warning("This command is deprecated. Instead, use "
                         "'openstack baremetal node list'.")
        return super(ListBaremetal, self).take_action(parsed_args)


class MaintenanceSetBaremetalNode(command.Command):
    """Set baremetal node to maintenance mode"""

    log = logging.getLogger(__name__ + ".MaintenanceSetBaremetalNode")

    def get_parser(self, prog_name):
        parser = super(MaintenanceSetBaremetalNode, self).get_parser(prog_name)

        parser.add_argument(
            'node',
            metavar='<node>',
            help="Name or UUID of the node."
        )
        parser.add_argument(
            '--reason',
            metavar='<reason>',
            default=None,
            help="Reason for setting maintenance mode.")

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        baremetal_client.node.set_maintenance(
            parsed_args.node,
            True,
            maint_reason=parsed_args.reason)


class MaintenanceUnsetBaremetalNode(command.Command):
    """Unset baremetal node from maintenance mode"""

    log = logging.getLogger(__name__ + ".MaintenanceUnsetBaremetalNode")

    def get_parser(self, prog_name):
        parser = super(MaintenanceUnsetBaremetalNode,
                       self).get_parser(prog_name)

        parser.add_argument(
            'node',
            metavar='<node>',
            help="Name or UUID of the node."
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        baremetal_client.node.set_maintenance(
            parsed_args.node,
            False)


class ManageBaremetalNode(ProvisionStateBaremetalNode):
    """Set provision state of baremetal node to 'manage'"""

    log = logging.getLogger(__name__ + ".ManageBaremetalNode")
    PROVISION_STATE = 'manage'


class PassthruCallBaremetalNode(command.Command):
    """Call a vendor passthu method for a node"""

    log = logging.getLogger(__name__ + ".PassthuCallBaremetalNode")

    def get_parser(self, prog_name):
        parser = super(PassthruCallBaremetalNode, self).get_parser(
            prog_name)

        parser.add_argument(
            'node',
            metavar='<node>',
            help="Name or UUID of the node"
        )
        parser.add_argument(
            'method',
            metavar='<method>',
            help="Vendor passthru method to be executed"
        )
        parser.add_argument(
            '--arg',
            metavar='<key=value>',
            action='append',
            help="Argument to pass to the passthru method (repeat option "
                 "to specify multiple arguments)"
        )
        parser.add_argument(
            '--http-method',
            metavar='<http-method>',
            choices=v1_utils.HTTP_METHODS,
            default='POST',
            help="The HTTP method to use in the passthru request. One of "
                 "%s. Defaults to POST." %
                 oscutils.format_list(v1_utils.HTTP_METHODS)
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        arguments = utils.key_value_pairs_to_dict(parsed_args.arg)
        resp = baremetal_client.node.vendor_passthru(
            parsed_args.node,
            parsed_args.method,
            http_method=parsed_args.http_method,
            args=arguments)
        if resp:
            # Print the raw response; we don't know how it should be formatted
            print(str(resp.to_dict()))


class PassthruListBaremetalNode(command.Lister):
    """List vendor passthru methods for a node"""

    log = logging.getLogger(__name__ + ".PassthruListBaremetalNode")

    def get_parser(self, prog_name):
        parser = super(PassthruListBaremetalNode, self).get_parser(
            prog_name)

        parser.add_argument(
            'node',
            metavar='<node>',
            help="Name or UUID of the node"
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal
        methods = baremetal_client.node.get_vendor_passthru_methods(
            parsed_args.node)
        data = []
        for method, response in methods.items():
            response['name'] = method
            response['http_methods'] = oscutils.format_list(
                response['http_methods'])
            data.append(response)

        return (
            res_fields.VENDOR_PASSTHRU_METHOD_RESOURCE.labels,
            (oscutils.get_dict_properties(
                s, res_fields.VENDOR_PASSTHRU_METHOD_RESOURCE.fields)
             for s in data))


class PowerBaremetalNode(command.Command):
    """Set power state of baremetal node"""

    log = logging.getLogger(__name__ + ".PowerBaremetalNode")

    def get_parser(self, prog_name):
        parser = super(PowerBaremetalNode, self).get_parser(prog_name)

        parser.add_argument(
            'power_state',
            metavar='<on|off>',
            choices=['on', 'off'],
            help="Power node on or off"
        )
        parser.add_argument(
            'node',
            metavar='<node>',
            help="Name or UUID of the node."
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        baremetal_client.node.set_power_state(
            parsed_args.node, parsed_args.power_state)


class ProvideBaremetalNode(ProvisionStateBaremetalNode):
    """Set provision state of baremetal node to 'provide'"""

    log = logging.getLogger(__name__ + ".ProvideBaremetalNode")
    PROVISION_STATE = 'provide'


class RebootBaremetalNode(command.Command):
    """Reboot baremetal node"""

    log = logging.getLogger(__name__ + ".RebootBaremetalNode")

    def get_parser(self, prog_name):
        parser = super(RebootBaremetalNode, self).get_parser(prog_name)

        parser.add_argument(
            'node',
            metavar='<node>',
            help="Name or UUID of the node.")

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        baremetal_client.node.set_power_state(
            parsed_args.node, 'reboot')


class RebuildBaremetalNode(ProvisionStateBaremetalNode):
    """Set provision state of baremetal node to 'rebuild'"""

    log = logging.getLogger(__name__ + ".RebuildBaremetalNode")
    PROVISION_STATE = 'rebuild'


class SetBaremetalNode(command.Command):
    """Set baremetal properties"""

    log = logging.getLogger(__name__ + ".SetBaremetalNode")

    def get_parser(self, prog_name):
        parser = super(SetBaremetalNode, self).get_parser(prog_name)

        parser.add_argument(
            'node',
            metavar='<node>',
            help="Name or UUID of the node.",
        )
        parser.add_argument(
            "--instance-uuid",
            metavar="<uuid>",
            help="Set instance UUID of node to <uuid>",
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            help="Set the name of the node",
        )
        parser.add_argument(
            "--driver",
            metavar="<driver>",
            help="Set the driver for the node",
        )
        parser.add_argument(
            '--network-interface',
            metavar='<network_interface>',
            help='Set the network interface for the node',
        )
        parser.add_argument(
            '--resource-class',
            metavar='<resource_class>',
            help='Set the resource class for the node',
        )
        parser.add_argument(
            '--target-raid-config',
            metavar='<target_raid_config>',
            help='Set the target RAID configuration (JSON) for the node. This '
                 'can be one of: 1. a file containing JSON data of the RAID '
                 'configuration; 2. "-" to read the contents from standard '
                 'input; or 3. a valid JSON string.',
        )
        parser.add_argument(
            "--property",
            metavar="<key=value>",
            action='append',
            help='Property to set on this baremetal node '
                 '(repeat option to set multiple properties)',
        )
        parser.add_argument(
            "--extra",
            metavar="<key=value>",
            action='append',
            help='Extra to set on this baremetal node '
                 '(repeat option to set multiple extras)',
        )
        parser.add_argument(
            "--driver-info",
            metavar="<key=value>",
            action='append',
            help='Driver information to set on this baremetal node '
                 '(repeat option to set multiple driver infos)',
        )
        parser.add_argument(
            "--instance-info",
            metavar="<key=value>",
            action='append',
            help='Instance information to set on this baremetal node '
                 '(repeat option to set multiple instance infos)',
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        # NOTE(rloo): Do this before updating the rest. Otherwise, it won't
        #             work if parsed_args.node is the name and the name is
        #             also being modified.
        if parsed_args.target_raid_config:
            raid_config = parsed_args.target_raid_config
            if raid_config == '-':
                raid_config = utils.get_from_stdin('target_raid_config')
            raid_config = utils.handle_json_or_file_arg(raid_config)
            baremetal_client.node.set_target_raid_config(parsed_args.node,
                                                         raid_config)

        properties = []
        if parsed_args.instance_uuid:
            instance_uuid = ["instance_uuid=%s" % parsed_args.instance_uuid]
            properties.extend(utils.args_array_to_patch(
                'add', instance_uuid))
        if parsed_args.name:
            name = ["name=%s" % parsed_args.name]
            properties.extend(utils.args_array_to_patch(
                'add', name))
        if parsed_args.driver:
            driver = ["driver=%s" % parsed_args.driver]
            properties.extend(utils.args_array_to_patch(
                'add', driver))
        if parsed_args.network_interface:
            network_interface = [
                "network_interface=%s" % parsed_args.network_interface]
            properties.extend(utils.args_array_to_patch(
                'add', network_interface))
        if parsed_args.resource_class:
            resource_class = [
                "resource_class=%s" % parsed_args.resource_class]
            properties.extend(utils.args_array_to_patch(
                'add', resource_class))
        if parsed_args.property:
            properties.extend(utils.args_array_to_patch(
                'add', ['properties/' + x for x in parsed_args.property]))
        if parsed_args.extra:
            properties.extend(utils.args_array_to_patch(
                'add', ['extra/' + x for x in parsed_args.extra]))
        if parsed_args.driver_info:
            properties.extend(utils.args_array_to_patch(
                'add', ['driver_info/' + x for x in parsed_args.driver_info]))
        if parsed_args.instance_info:
            properties.extend(utils.args_array_to_patch(
                'add', ['instance_info/' + x for x
                        in parsed_args.instance_info]))
        if properties:
            baremetal_client.node.update(parsed_args.node, properties)


class SetBaremetal(SetBaremetalNode):
    """Set baremetal properties. DEPRECATED"""

    # TODO(thrash): Remove after 11-July-2017 during the 'Queens' cycle.
    log = logging.getLogger(__name__ + ".SetBaremetal")

    def take_action(self, parsed_args):
        self.log.warning("This command is deprecated. Instead, use "
                         "'openstack baremetal node set'.")
        return super(SetBaremetal, self).take_action(parsed_args)


class ShowBaremetalNode(command.ShowOne):
    """Show baremetal node details"""

    log = logging.getLogger(__name__ + ".ShowBaremetalNode")

    def get_parser(self, prog_name):
        parser = super(ShowBaremetalNode, self).get_parser(prog_name)
        parser.add_argument(
            "node",
            metavar="<node>",
            help="Name or UUID of the node (or instance UUID if --instance "
                 "is specified)")
        parser.add_argument(
            '--instance',
            dest='instance_uuid',
            action='store_true',
            default=False,
            help='<node> is an instance UUID.')
        parser.add_argument(
            '--fields',
            nargs='+',
            dest='fields',
            metavar='<field>',
            action='append',
            choices=res_fields.NODE_DETAILED_RESOURCE.fields,
            default=[],
            help="One or more node fields. Only these fields will be fetched "
                 "from the server.")
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal
        fields = list(itertools.chain.from_iterable(parsed_args.fields))
        fields = fields if fields else None
        if parsed_args.instance_uuid:
            node = baremetal_client.node.get_by_instance_uuid(
                parsed_args.node, fields=fields)._info
        else:
            node = baremetal_client.node.get(
                parsed_args.node, fields=fields)._info
        node.pop("links", None)
        node.pop("ports", None)

        node.setdefault('chassis_uuid', '')

        return self.dict2columns(node)


class ShowBaremetal(ShowBaremetalNode):
    """Show baremetal node details. DEPRECATED"""

    # TODO(thrash): Remove after 11-July-2017 during the 'Queens' cycle.
    log = logging.getLogger(__name__ + ".ShowBaremetal")

    def take_action(self, parsed_args):
        self.log.warning("This command is deprecated. Instead, use "
                         "'openstack baremetal node show'.")
        return super(ShowBaremetal, self).take_action(parsed_args)


class UndeployBaremetalNode(ProvisionStateBaremetalNode):
    """Set provision state of baremetal node to 'deleted'"""

    log = logging.getLogger(__name__ + ".UndeployBaremetalNode")
    PROVISION_STATE = 'deleted'


class UnsetBaremetalNode(command.Command):
    """Unset baremetal properties"""
    log = logging.getLogger(__name__ + ".UnsetBaremetalNode")

    def get_parser(self, prog_name):
        parser = super(UnsetBaremetalNode, self).get_parser(prog_name)

        parser.add_argument(
            'node',
            metavar='<node>',
            help="Name or UUID of the node."
        )
        parser.add_argument(
            '--instance-uuid',
            action='store_true',
            default=False,
            help='Unset instance UUID on this baremetal node'
        )
        parser.add_argument(
            "--name",
            action='store_true',
            help="Unset the name of the node",
        )
        parser.add_argument(
            "--resource-class",
            dest='resource_class',
            action='store_true',
            help="Unset the resource class of the node",
        )
        parser.add_argument(
            "--target-raid-config",
            action='store_true',
            help="Unset the target RAID configuration of the node",
        )
        parser.add_argument(
            '--property',
            metavar='<key>',
            action='append',
            help='Property to unset on this baremetal node '
                 '(repeat option to unset multiple properties)',
        )
        parser.add_argument(
            "--extra",
            metavar="<key>",
            action='append',
            help='Extra to unset on this baremetal node '
                 '(repeat option to unset multiple extras)',
        )
        parser.add_argument(
            "--driver-info",
            metavar="<key>",
            action='append',
            help='Driver information to unset on this baremetal node '
                 '(repeat option to unset multiple driver informations)',
        )
        parser.add_argument(
            "--instance-info",
            metavar="<key>",
            action='append',
            help='Instance information to unset on this baremetal node '
                 '(repeat option to unset multiple instance informations)',
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        # NOTE(rloo): Do this before removing the rest. Otherwise, it won't
        #             work if parsed_args.node is the name and the name is
        #             also being removed.
        if parsed_args.target_raid_config:
            baremetal_client.node.set_target_raid_config(parsed_args.node, {})

        properties = []
        if parsed_args.instance_uuid:
            properties.extend(utils.args_array_to_patch('remove',
                              ['instance_uuid']))
        if parsed_args.name:
            properties.extend(utils.args_array_to_patch('remove',
                              ['name']))
        if parsed_args.resource_class:
            properties.extend(utils.args_array_to_patch('remove',
                              ['resource_class']))
        if parsed_args.property:
            properties.extend(utils.args_array_to_patch('remove',
                              ['properties/' + x
                               for x in parsed_args.property]))
        if parsed_args.extra:
            properties.extend(utils.args_array_to_patch('remove',
                              ['extra/' + x for x in parsed_args.extra]))
        if parsed_args.driver_info:
            properties.extend(utils.args_array_to_patch('remove',
                              ['driver_info/' + x for x
                               in parsed_args.driver_info]))
        if parsed_args.instance_info:
            properties.extend(utils.args_array_to_patch('remove',
                              ['instance_info/' + x for x
                               in parsed_args.instance_info]))
        if properties:
            baremetal_client.node.update(parsed_args.node, properties)


class UnsetBaremetal(UnsetBaremetalNode):
    """Unset baremetal properties. DEPRECATED"""

    # TODO(thrash): Remove after 11-July-2017 during the 'Queens' cycle.
    log = logging.getLogger(__name__ + ".UnsetBaremetal")

    def take_action(self, parsed_args):
        self.log.warning("This command is deprecated. Instead, use "
                         "'openstack baremetal node unset'.")
        super(UnsetBaremetal, self).take_action(parsed_args)


class ValidateBaremetalNode(command.Lister):
    """Validate a node's driver interfaces"""

    log = logging.getLogger(__name__ + ".ValidateBaremetalNode")

    def get_parser(self, prog_name):
        parser = super(ValidateBaremetalNode, self).get_parser(prog_name)

        parser.add_argument(
            'node',
            metavar='<node>',
            help="Name or UUID of the node")

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        interfaces = baremetal_client.node.validate(parsed_args.node)._info
        data = []
        for key, value in interfaces.items():
            interface = {'interface': key}
            interface.update(value)
            data.append(interface)
        field_labels = ['Interface', 'Result', 'Reason']
        fields = ['interface', 'result', 'reason']
        data = oscutils.sort_items(data, 'interface')
        return (field_labels,
                (oscutils.get_dict_properties(s, fields) for s in data))
