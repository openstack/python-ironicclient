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
import six

from ironicclient.common.apiclient import exceptions
from ironicclient.common import cliutils
from ironicclient.common.i18n import _
from ironicclient.common import utils
from ironicclient import exc
from ironicclient.v1 import resource_fields as res_fields
from ironicclient.v1 import utils as v1_utils


def _print_node_show(node, fields=None, json=False):
    if fields is None:
        fields = res_fields.NODE_DETAILED_RESOURCE.fields

    data = dict(
        [(f, getattr(node, f, '')) for f in fields])
    cliutils.print_dict(data, wrap=72, json_flag=json)


@cliutils.arg(
    'node',
    metavar='<id>',
    help="Name or UUID of the node "
         "(or instance UUID if --instance is specified).")
@cliutils.arg(
    '--instance',
    dest='instance_uuid',
    action='store_true',
    default=False,
    help='<id> is an instance UUID.')
@cliutils.arg(
    '--fields',
    nargs='+',
    dest='fields',
    metavar='<field>',
    action='append',
    default=[],
    help="One or more node fields. Only these fields will be fetched from "
         "the server.")
def do_node_show(cc, args):
    """Show detailed information about a node."""
    fields = args.fields[0] if args.fields else None
    utils.check_empty_arg(args.node, '<id>')
    utils.check_for_invalid_fields(
        fields, res_fields.NODE_DETAILED_RESOURCE.fields)
    if args.instance_uuid:
        node = cc.node.get_by_instance_uuid(args.node, fields=fields)
    else:
        node = cc.node.get(args.node, fields=fields)
    _print_node_show(node, fields=fields, json=args.json)


@cliutils.arg(
    '--limit',
    metavar='<limit>',
    type=int,
    help='Maximum number of nodes to return per request, '
         '0 for no limit. Default is the maximum number used '
         'by the Ironic API Service.')
@cliutils.arg(
    '--marker',
    metavar='<node>',
    help='Node UUID (for example, of the last node in the list from '
         'a previous request). Returns the list of nodes after this UUID.')
@cliutils.arg(
    '--sort-key',
    metavar='<field>',
    help='Node field that will be used for sorting.')
@cliutils.arg(
    '--sort-dir',
    metavar='<direction>',
    choices=['asc', 'desc'],
    help='Sort direction: "asc" (the default) or "desc".')
@cliutils.arg(
    '--maintenance',
    metavar='<boolean>',
    help="List nodes in maintenance mode: 'true' or 'false'.")
@cliutils.arg(
    '--associated',
    metavar='<boolean>',
    help="List nodes by instance association: 'true' or 'false'.")
@cliutils.arg(
    '--provision-state',
    metavar='<provision-state>',
    help="List nodes in specified provision state.")
@cliutils.arg(
    '--driver',
    metavar='<driver>',
    help="List nodes using specified driver.")
@cliutils.arg(
    '--detail',
    dest='detail',
    action='store_true',
    default=False,
    help="Show detailed information about the nodes.")
@cliutils.arg(
    '--fields',
    nargs='+',
    dest='fields',
    metavar='<field>',
    action='append',
    default=[],
    help="One or more node fields. Only these fields will be fetched from "
         "the server. Can not be used when '--detail' is specified.")
@cliutils.arg(
    '--resource-class',
    dest='resource_class',
    metavar='<resource class>',
    help="List nodes using specified resource class.")
def do_node_list(cc, args):
    """List the nodes which are registered with the Ironic service."""
    params = {}
    if args.associated is not None:
        params['associated'] = utils.bool_argument_value("--associated",
                                                         args.associated)
    if args.maintenance is not None:
        params['maintenance'] = utils.bool_argument_value("--maintenance",
                                                          args.maintenance)
    if args.provision_state is not None:
        params['provision_state'] = args.provision_state

    if args.driver is not None:
        params['driver'] = args.driver

    if args.resource_class is not None:
        params['resource_class'] = args.resource_class

    if args.detail:
        fields = res_fields.NODE_DETAILED_RESOURCE.fields
        field_labels = res_fields.NODE_DETAILED_RESOURCE.labels
    elif args.fields:
        utils.check_for_invalid_fields(
            args.fields[0], res_fields.NODE_DETAILED_RESOURCE.fields)
        resource = res_fields.Resource(args.fields[0])
        fields = resource.fields
        field_labels = resource.labels
    else:
        fields = res_fields.NODE_RESOURCE.fields
        field_labels = res_fields.NODE_RESOURCE.labels

    sort_fields = res_fields.NODE_DETAILED_RESOURCE.sort_fields
    sort_field_labels = res_fields.NODE_DETAILED_RESOURCE.sort_labels

    params.update(utils.common_params_for_list(args,
                                               sort_fields,
                                               sort_field_labels))
    nodes = cc.node.list(**params)
    cliutils.print_list(nodes, fields,
                        field_labels=field_labels,
                        sortby_index=None,
                        json_flag=args.json)


@cliutils.arg(
    '-c', '--chassis',
    dest='chassis_uuid',
    metavar='<chassis>',
    help='UUID of the chassis that this node belongs to.')
@cliutils.arg(
    '--chassis_uuid',
    help=argparse.SUPPRESS)
@cliutils.arg(
    '-d', '--driver',
    metavar='<driver>',
    required=True,
    help='Driver used to control the node.')
@cliutils.arg(
    '-i', '--driver-info',
    metavar='<key=value>',
    action='append',
    help='Key/value pair used by the driver, such as out-of-band management '
         'credentials. Can be specified multiple times.')
@cliutils.arg(
    '--driver_info',
    action='append',
    help=argparse.SUPPRESS)
@cliutils.arg(
    '-p', '--properties',
    metavar='<key=value>',
    action='append',
    help='Key/value pair describing the physical characteristics of the '
         'node. This is exported to Nova and used by the scheduler. '
         'Can be specified multiple times.')
@cliutils.arg(
    '-e', '--extra',
    metavar='<key=value>',
    action='append',
    help="Record arbitrary key/value metadata. "
         "Can be specified multiple times.")
@cliutils.arg(
    '-u', '--uuid',
    metavar='<uuid>',
    help="Unique UUID for the node.")
@cliutils.arg(
    '-n', '--name',
    metavar='<name>',
    help="Unique name for the node.")
@cliutils.arg(
    '--boot-interface',
    metavar='<boot-interface>',
    help='Boot interface used by the node\'s driver. This is '
         'only applicable when the specified --driver is a '
         'hardware type.')
@cliutils.arg(
    '--console-interface',
    metavar='<console-interface>',
    help='Console interface used by the node\'s driver. This is '
         'only applicable when the specified --driver is a '
         'hardware type.')
@cliutils.arg(
    '--deploy-interface',
    metavar='<deploy-interface>',
    help='Deploy interface used by the node\'s driver. This is '
         'only applicable when the specified --driver is a '
         'hardware type.')
@cliutils.arg(
    '--inspect-interface',
    metavar='<inspect-interface>',
    help='Inspect interface used by the node\'s driver. This is '
         'only applicable when the specified --driver is a '
         'hardware type.')
@cliutils.arg(
    '--management-interface',
    metavar='<management-interface>',
    help='Management interface used by the node\'s driver. This is '
         'only applicable when the specified --driver is a '
         'hardware type.')
@cliutils.arg(
    '--network-interface',
    metavar='<network_interface>',
    help='Network interface used for switching node to cleaning/provisioning '
         'networks.')
@cliutils.arg(
    '--power-interface',
    metavar='<power-interface>',
    help='Power interface used by the node\'s driver. This is '
         'only applicable when the specified --driver is a '
         'hardware type.')
@cliutils.arg(
    '--raid-interface',
    metavar='<raid-interface>',
    help='RAID interface used by the node\'s driver. This is '
         'only applicable when the specified --driver is a '
         'hardware type.')
@cliutils.arg(
    '--storage-interface',
    metavar='<storage-interface>',
    help='Storage interface used by the node\'s driver.')
@cliutils.arg(
    '--vendor-interface',
    metavar='<vendor-interface>',
    help='Vendor interface used by the node\'s driver. This is '
         'only applicable when the specified --driver is a '
         'hardware type.')
@cliutils.arg(
    '--resource-class',
    metavar='<resource_class>',
    help='Resource class for classifying or grouping nodes. Used, for '
         'example, to classify nodes in Nova\'s placement engine.')
def do_node_create(cc, args):
    """Register a new node with the Ironic service."""
    field_list = ['chassis_uuid', 'driver', 'driver_info',
                  'properties', 'extra', 'uuid', 'name',
                  'boot_interface', 'console_interface',
                  'deploy_interface', 'inspect_interface',
                  'management_interface', 'network_interface',
                  'power_interface', 'raid_interface',
                  'storage_interface', 'vendor_interface',
                  'resource_class']
    fields = dict((k, v) for (k, v) in vars(args).items()
                  if k in field_list and not (v is None))
    fields = utils.args_array_to_dict(fields, 'driver_info')
    fields = utils.args_array_to_dict(fields, 'extra')
    fields = utils.args_array_to_dict(fields, 'properties')
    node = cc.node.create(**fields)

    data = dict([(f, getattr(node, f, '')) for f in field_list])
    cliutils.print_dict(data, wrap=72, json_flag=args.json)


@cliutils.arg('node',
              metavar='<node>',
              nargs='+',
              help="Name or UUID of the node.")
def do_node_delete(cc, args):
    """Unregister node(s) from the Ironic service.

    Returns errors for any nodes that could not be unregistered.
    """

    failures = []
    for n in args.node:
        try:
            cc.node.delete(n)
            print(_('Deleted node %s') % n)
        except exceptions.ClientException as e:
            failures.append(_("Failed to delete node %(node)s: %(error)s")
                            % {'node': n, 'error': e})
    if failures:
        raise exceptions.ClientException("\n".join(failures))


@cliutils.arg('node', metavar='<node>', help="Name or UUID of the node.")
@cliutils.arg(
    'op',
    metavar='<op>',
    choices=['add', 'replace', 'remove'],
    help="Operation: 'add', 'replace', or 'remove'.")
@cliutils.arg(
    'attributes',
    metavar='<path=value>',
    nargs='+',
    action='append',
    default=[],
    help="Attribute to add, replace, or remove. Can be specified "
         "multiple times. For 'remove', only <path> is necessary. "
         "For nested attributes, separate the components with slashes, eg "
         "'driver_info/deploy_kernel=uuid'.")
def do_node_update(cc, args):
    """Update information about a registered node."""
    patch = utils.args_array_to_patch(args.op, args.attributes[0])
    node = cc.node.update(args.node, patch)
    _print_node_show(node, json=args.json)


@cliutils.arg('node',
              metavar='<node>',
              help="Name or UUID of the node.")
@cliutils.arg('method',
              metavar='<method>',
              help="Vendor-passthru method to be called.")
@cliutils.arg('arguments',
              metavar='<arg=value>',
              nargs='*',
              action='append',
              default=[],
              help=("Argument to be passed to the vendor-passthru method. Can "
                    "be specified multiple times."))
@cliutils.arg('--http-method',
              metavar='<http-method>',
              choices=v1_utils.HTTP_METHODS,
              help=("The HTTP method to use in the request. Valid HTTP "
                    "methods are: %s. Defaults to 'POST'." %
                    ', '.join(v1_utils.HTTP_METHODS)))
@cliutils.arg('--http_method',
              help=argparse.SUPPRESS)
def do_node_vendor_passthru(cc, args):
    """Call a vendor-passthru extension for a node."""
    arguments = utils.key_value_pairs_to_dict(args.arguments[0])

    resp = cc.node.vendor_passthru(args.node, args.method,
                                   http_method=args.http_method,
                                   args=arguments)
    if resp:
        # Print the raw response we don't know how it should be formated
        print(str(resp.to_dict()))


@cliutils.arg(
    '--detail',
    dest='detail',
    action='store_true',
    default=False,
    help="Show detailed information about the ports.")
@cliutils.arg(
    '--limit',
    metavar='<limit>',
    type=int,
    help='Maximum number of ports to return per request, '
         '0 for no limit. Default is the maximum number used '
         'by the Ironic API Service.')
@cliutils.arg(
    '--marker',
    metavar='<port>',
    help='Port UUID (for example, of the last port in the list from a '
         'previous request). Returns the list of ports after this UUID.')
@cliutils.arg(
    '--sort-key',
    metavar='<field>',
    help='Port field that will be used for sorting.')
@cliutils.arg(
    '--sort-dir',
    metavar='<direction>',
    choices=['asc', 'desc'],
    help='Sort direction: "asc" (the default) or "desc".')
@cliutils.arg('node', metavar='<node>', help="Name or UUID of the node.")
@cliutils.arg(
    '--fields',
    nargs='+',
    dest='fields',
    metavar='<field>',
    action='append',
    default=[],
    help="One or more port fields. Only these fields will be fetched from "
         "the server. Can not be used when '--detail' is specified.")
def do_node_port_list(cc, args):
    """List the ports associated with a node."""
    if args.detail:
        fields = res_fields.PORT_DETAILED_RESOURCE.fields
        field_labels = res_fields.PORT_DETAILED_RESOURCE.labels
    elif args.fields:
        utils.check_for_invalid_fields(
            args.fields[0], res_fields.PORT_DETAILED_RESOURCE.fields)
        resource = res_fields.Resource(args.fields[0])
        fields = resource.fields
        field_labels = resource.labels
    else:
        fields = res_fields.PORT_RESOURCE.fields
        field_labels = res_fields.PORT_RESOURCE.labels

    sort_fields = res_fields.PORT_DETAILED_RESOURCE.sort_fields
    sort_field_labels = res_fields.PORT_DETAILED_RESOURCE.sort_labels

    params = utils.common_params_for_list(args, sort_fields,
                                          sort_field_labels)

    ports = cc.node.list_ports(args.node, **params)

    cliutils.print_list(ports, fields,
                        field_labels=field_labels,
                        sortby_index=None,
                        json_flag=args.json)


@cliutils.arg('node', metavar='<node>', help="Name or UUID of the node.")
@cliutils.arg(
    'maintenance_mode',
    metavar='<maintenance-mode>',
    help="'true' or 'false'; 'on' or 'off'.")
@cliutils.arg(
    '--reason',
    metavar='<reason>',
    default=None,
    help=("Reason for setting maintenance mode to 'true' or 'on';"
          " not valid when setting to 'false' or 'off'."))
def do_node_set_maintenance(cc, args):
    """Enable or disable maintenance mode for a node."""
    maintenance_mode = utils.bool_argument_value("<maintenance-mode>",
                                                 args.maintenance_mode)
    if args.reason and not maintenance_mode:
        raise exceptions.CommandError(_('Cannot set "reason" when turning off '
                                        'maintenance mode.'))
    cc.node.set_maintenance(args.node, maintenance_mode,
                            maint_reason=args.reason)


@cliutils.arg('node', metavar='<node>', help="Name or UUID of the node.")
@cliutils.arg(
    'power_state',
    metavar='<power-state>',
    choices=['on', 'off', 'reboot'],
    help="'on', 'off', or 'reboot'.")
@cliutils.arg(
    '--soft',
    dest='soft',
    action='store_true',
    default=False,
    help=("Gracefully change the power state. Only valid for 'off' and "
          "'reboot' power states."))
@cliutils.arg(
    '--power-timeout',
    metavar='<power-timeout>',
    type=int,
    default=None,
    help=("Timeout (in seconds, positive integer) to wait for the target "
          "power state before erroring out."))
def do_node_set_power_state(cc, args):
    """Power a node on or off or reboot."""
    try:
        cc.node.set_power_state(args.node, args.power_state, args.soft,
                                timeout=args.power_timeout)
    except ValueError as e:
        raise exc.CommandError(six.text_type(e))


@cliutils.arg('node', metavar='<node>', help="Name or UUID of the node.")
@cliutils.arg(
    'target_raid_config',
    metavar='<target-raid-config>',
    help=("A file containing JSON data of the desired RAID configuration. "
          "Use '-' to read the contents from standard input. "
          "It also accepts the valid json string as input if "
          "file/standard input are not used for providing input. "
          "The input can be an empty dictionary too which "
          "unsets the node.target_raid_config on the node."))
def do_node_set_target_raid_config(cc, args):
    """Set target RAID config on a node."""
    target_raid_config = args.target_raid_config
    if not target_raid_config:
        raise exc.InvalidAttribute(
            _("target RAID configuration not provided"))

    if target_raid_config == '-':
        target_raid_config = utils.get_from_stdin('target_raid_config')
    target_raid_config = utils.handle_json_or_file_arg(target_raid_config)

    cc.node.set_target_raid_config(args.node, target_raid_config)


@cliutils.arg('node', metavar='<node>', help="Name or UUID of the node.")
@cliutils.arg(
    'provision_state',
    metavar='<provision-state>',
    choices=v1_utils.PROVISION_STATES,
    help="Supported states: %s." % ', '.join(v1_utils.PROVISION_STATES))
@cliutils.arg(
    '--config-drive',
    metavar='<config-drive>',
    default=None,
    help=("A gzipped, base64-encoded configuration drive string OR the path "
          "to the configuration drive file OR the path to a directory "
          "containing the config drive files. In case it's a directory, a "
          "config drive will be generated from it. This argument is only "
          "valid when setting provision-state to 'active'."))
@cliutils.arg(
    '--clean-steps',
    metavar='<clean-steps>',
    default=None,
    help=("The clean steps in JSON format. May be the path to a file "
          "containing the clean steps; OR '-', with the clean steps being "
          "read from standard input; OR a string. The value should be "
          "a list of clean-step dictionaries; each dictionary should have "
          "keys 'interface' and 'step', and optional key 'args'. "
          "This argument must be specified (and is only valid) when "
          "setting provision-state to 'clean'."))
@cliutils.arg(
    '--wait',
    type=int,
    dest='wait_timeout',
    default=None,
    const=0,
    nargs='?',
    help=("Wait for a node to reach the expected state. Not supported "
          "for 'abort'. Optionally takes a timeout in seconds. "
          "The default value is 0, meaning no timeout. "
          "Fails if the node reaches an unexpected stable state, a failure "
          "state or a state with last_error set."))
def do_node_set_provision_state(cc, args):
    """Initiate a provisioning state change for a node."""
    if args.config_drive and args.provision_state != 'active':
        raise exceptions.CommandError(_('--config-drive is only valid when '
                                        'setting provision state to "active"'))
    elif args.clean_steps and args.provision_state != 'clean':
        raise exceptions.CommandError(_('--clean-steps is only valid when '
                                        'setting provision state to "clean"'))
    elif args.provision_state == 'clean' and not args.clean_steps:
        raise exceptions.CommandError(_('--clean-steps must be specified when '
                                        'setting provision state to "clean"'))

    if args.wait_timeout is not None:
        wait_args = v1_utils.PROVISION_ACTIONS.get(args.provision_state)
        if wait_args is None:
            raise exceptions.CommandError(
                _("--wait is not supported for provision state '%s'")
                % args.provision_state)

    clean_steps = args.clean_steps
    if args.clean_steps == '-':
        clean_steps = utils.get_from_stdin('clean steps')
    if clean_steps:
        clean_steps = utils.handle_json_or_file_arg(clean_steps)
    cc.node.set_provision_state(args.node, args.provision_state,
                                configdrive=args.config_drive,
                                cleansteps=clean_steps)
    if args.wait_timeout is not None:
        print(_('Waiting for provision state %(state)s on node %(node)s') %
              {'state': wait_args['expected_state'], 'node': args.node})
        cc.node.wait_for_provision_state(args.node, timeout=args.wait_timeout,
                                         **wait_args)


@cliutils.arg('node', metavar='<node>', help="Name or UUID of the node.")
def do_node_validate(cc, args):
    """Validate a node's driver interfaces."""
    ifaces = cc.node.validate(args.node)
    obj_list = []
    for key, value in ifaces.to_dict().items():
        data = {'interface': key}
        data.update(value)
        obj_list.append(type('iface', (object,), data))
    field_labels = ['Interface', 'Result', 'Reason']
    fields = ['interface', 'result', 'reason']
    cliutils.print_list(obj_list, fields, field_labels=field_labels,
                        json_flag=args.json)


@cliutils.arg('node', metavar='<node>', help="Name or UUID of the node.")
def do_node_get_console(cc, args):
    """Get the connection information for a node's console, if enabled."""
    info = cc.node.get_console(args.node)
    cliutils.print_dict(info, wrap=72, json_flag=args.json)


@cliutils.arg('node', metavar='<node>', help="Name or UUID of the node.")
@cliutils.arg(
    'enabled',
    metavar='<enabled>',
    help="Enable or disable console access for a node: 'true' or 'false'.")
def do_node_set_console_mode(cc, args):
    """Enable or disable serial console access for a node."""
    enable = utils.bool_argument_value("<enabled>", args.enabled)
    cc.node.set_console_mode(args.node, enable)


@cliutils.arg('node', metavar='<node>', help="Name or UUID of the node.")
@cliutils.arg(
    'device',
    metavar='<boot-device>',
    choices=v1_utils.BOOT_DEVICES,
    help="One of %s." % ', '.join(v1_utils.BOOT_DEVICES))
@cliutils.arg(
    '--persistent',
    dest='persistent',
    action='store_true',
    default=False,
    help="Make changes persistent for all future boots.")
def do_node_set_boot_device(cc, args):
    """Set the boot device for a node."""
    cc.node.set_boot_device(args.node, args.device, args.persistent)


@cliutils.arg('node', metavar='<node>', help="Name or UUID of the node.")
def do_node_get_boot_device(cc, args):
    """Get the current boot device for a node."""
    boot_device = cc.node.get_boot_device(args.node)
    cliutils.print_dict(boot_device, wrap=72, json_flag=args.json)


@cliutils.arg('node', metavar='<node>', help="Name or UUID of the node.")
def do_node_inject_nmi(cc, args):
    """Inject NMI to a node."""
    cc.node.inject_nmi(args.node)


@cliutils.arg('node', metavar='<node>', help="Name or UUID of the node.")
def do_node_get_supported_boot_devices(cc, args):
    """Get the supported boot devices for a node."""
    boot_devices = cc.node.get_supported_boot_devices(args.node)
    boot_device_list = boot_devices.get('supported_boot_devices', [])
    boot_devices['supported_boot_devices'] = ', '.join(boot_device_list)
    cliutils.print_dict(boot_devices, wrap=72, json_flag=args.json)


@cliutils.arg('node', metavar='<node>', help="Name or UUID of the node.")
def do_node_show_states(cc, args):
    """Show information about the node's states."""
    states = cc.node.states(args.node)
    cliutils.print_dict(states.to_dict(), wrap=72, json_flag=args.json)


@cliutils.arg('node', metavar='<node>', help="Name or UUID of the node.")
def do_node_get_vendor_passthru_methods(cc, args):
    """Get the vendor passthru methods for a node."""
    methods = cc.node.get_vendor_passthru_methods(args.node)
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


@cliutils.arg('node', metavar='<node>', help="Name or UUID of the node.")
def do_node_vif_list(cc, args):
    """List VIFs for a given node."""
    vifs = cc.node.vif_list(args.node)
    fields = res_fields.VIF_RESOURCE.fields
    field_labels = res_fields.VIF_RESOURCE.labels
    cliutils.print_list(vifs, fields, field_labels=field_labels,
                        sortby_index=None,
                        json_flag=args.json)


@cliutils.arg('node', metavar='<node>', help="Name or UUID of the node.")
@cliutils.arg('vif_id', metavar='<vif-id>',
              help="Name or UUID of the VIF to attach to node.")
@cliutils.arg('--vif-info', metavar='<key=value>',
              action='append',
              help="Record arbitrary key/value metadata. "
                   "Can be specified multiple times. The mandatory 'id' "
                   "parameter cannot be specified as a key.")
def do_node_vif_attach(cc, args):
    """Attach VIF to a given node."""
    fields = utils.key_value_pairs_to_dict(args.vif_info or [])
    cc.node.vif_attach(args.node, args.vif_id, **fields)


@cliutils.arg('node', metavar='<node>', help="Name or UUID of the node.")
@cliutils.arg('vif_id', metavar='<vif-id>',
              help="Name or UUID of the VIF to detach from node.")
def do_node_vif_detach(cc, args):
    """Detach VIF from a given node."""
    cc.node.vif_detach(args.node, args.vif_id)
