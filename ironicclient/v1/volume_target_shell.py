# Copyright 2017 Hitachi, Ltd.
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

from ironicclient.common.apiclient import exceptions
from ironicclient.common import cliutils
from ironicclient.common.i18n import _
from ironicclient.common import utils
from ironicclient.v1 import resource_fields as res_fields


def _print_volume_target_show(volume_target, fields=None, json=False):
    if fields is None:
        fields = res_fields.VOLUME_TARGET_DETAILED_RESOURCE.fields

    data = dict([(f, getattr(volume_target, f, '')) for f in fields])
    cliutils.print_dict(data, wrap=72, json_flag=json)


@cliutils.arg(
    'volume_target',
    metavar='<id>',
    help=_("UUID of the volume target."))
@cliutils.arg(
    '--fields',
    nargs='+',
    dest='fields',
    metavar='<field>',
    action='append',
    default=[],
    help=_("One or more volume target fields. Only these fields will be "
           "fetched from the server."))
def do_volume_target_show(cc, args):
    """Show detailed information about a volume target."""
    fields = args.fields[0] if args.fields else None
    utils.check_for_invalid_fields(
        fields, res_fields.VOLUME_TARGET_DETAILED_RESOURCE.fields)
    utils.check_empty_arg(args.volume_target, '<id>')
    volume_target = cc.volume_target.get(args.volume_target, fields=fields)
    _print_volume_target_show(volume_target, fields=fields, json=args.json)


@cliutils.arg(
    '--detail',
    dest='detail',
    action='store_true',
    default=False,
    help=_("Show detailed information about volume targets."))
@cliutils.arg(
    '-n', '--node',
    metavar='<node>',
    help=_('Only list volume targets of this node (name or UUID)'))
@cliutils.arg(
    '--limit',
    metavar='<limit>',
    type=int,
    help=_('Maximum number of volume targets to return per request, '
           '0 for no limit. Default is the maximum number used '
           'by the Baremetal API Service.'))
@cliutils.arg(
    '--marker',
    metavar='<volume target>',
    help=_('Volume target UUID (for example, of the last volume target in '
           'the list from a previous request). Returns the list of volume '
           'targets after this UUID.'))
@cliutils.arg(
    '--sort-key',
    metavar='<field>',
    help=_('Volume target field that will be used for sorting.'))
@cliutils.arg(
    '--sort-dir',
    metavar='<direction>',
    choices=['asc', 'desc'],
    help=_('Sort direction: "asc" (the default) or "desc".'))
@cliutils.arg(
    '--fields',
    nargs='+',
    dest='fields',
    metavar='<field>',
    action='append',
    default=[],
    help=_("One or more volume target fields. Only these fields will be "
           "fetched from the server. Can not be used when '--detail' is "
           "specified."))
def do_volume_target_list(cc, args):
    """List the volume targets."""
    params = {}

    if args.node is not None:
        params['node'] = args.node

    if args.detail:
        fields = res_fields.VOLUME_TARGET_DETAILED_RESOURCE.fields
        field_labels = res_fields.VOLUME_TARGET_DETAILED_RESOURCE.labels
    elif args.fields:
        utils.check_for_invalid_fields(
            args.fields[0],
            res_fields.VOLUME_TARGET_DETAILED_RESOURCE.fields)
        resource = res_fields.Resource(args.fields[0])
        fields = resource.fields
        field_labels = resource.labels
    else:
        fields = res_fields.VOLUME_TARGET_RESOURCE.fields
        field_labels = res_fields.VOLUME_TARGET_RESOURCE.labels

    sort_fields = res_fields.VOLUME_TARGET_DETAILED_RESOURCE.sort_fields
    sort_field_labels = (
        res_fields.VOLUME_TARGET_DETAILED_RESOURCE.sort_labels)

    params.update(utils.common_params_for_list(args,
                                               sort_fields,
                                               sort_field_labels))

    volume_target = cc.volume_target.list(**params)
    cliutils.print_list(volume_target, fields, field_labels=field_labels,
                        sortby_index=None, json_flag=args.json)


@cliutils.arg(
    '-e', '--extra',
    metavar="<key=value>",
    action='append',
    help=_("Record arbitrary key/value metadata. "
           "Can be specified multiple times."))
@cliutils.arg(
    '-n', '--node',
    dest='node_uuid',
    metavar='<node>',
    required=True,
    help=_('UUID of the node that this volume target belongs to.'))
@cliutils.arg(
    '-t', '--type',
    metavar="<volume type>",
    required=True,
    help=_("Type of the volume target, e.g. 'iscsi', 'fibre_channel', 'rbd'."))
@cliutils.arg(
    '-p', '--properties',
    metavar="<key=value>",
    action='append',
    help=_("Key/value property related to the type of this volume "
           "target. Can be specified multiple times."))
@cliutils.arg(
    '-b', '--boot-index',
    metavar="<boot index>",
    required=True,
    help=_("Boot index of the volume target."))
@cliutils.arg(
    '-i', '--volume_id',
    metavar="<volume id>",
    required=True,
    help=_("ID of the volume associated with this target."))
@cliutils.arg(
    '-u', '--uuid',
    metavar='<uuid>',
    help=_("UUID of the volume target."))
def do_volume_target_create(cc, args):
    """Create a new volume target."""
    field_list = ['extra', 'volume_type', 'properties',
                  'boot_index', 'node_uuid', 'volume_id', 'uuid']
    fields = dict((k, v) for (k, v) in vars(args).items()
                  if k in field_list and not (v is None))
    fields = utils.args_array_to_dict(fields, 'properties')
    fields = utils.args_array_to_dict(fields, 'extra')
    volume_target = cc.volume_target.create(**fields)

    data = dict([(f, getattr(volume_target, f, '')) for f in field_list])
    cliutils.print_dict(data, wrap=72, json_flag=args.json)


@cliutils.arg('volume_target', metavar='<volume target>', nargs='+',
              help=_("UUID of the volume target."))
def do_volume_target_delete(cc, args):
    """Delete a volume target."""
    failures = []
    for vt in args.volume_target:
        try:
            cc.volume_target.delete(vt)
            print(_('Deleted volume target %s') % vt)
        except exceptions.ClientException as e:
            failures.append(_("Failed to delete volume target %(vt)s: "
                              "%(error)s")
                            % {'vt': vt, 'error': e})
    if failures:
        raise exceptions.ClientException("\n".join(failures))


@cliutils.arg('volume_target', metavar='<volume target>',
              help=_("UUID of the volume target."))
@cliutils.arg(
    'op',
    metavar='<op>',
    choices=['add', 'replace', 'remove'],
    help=_("Operation: 'add', 'replace', or 'remove'."))
@cliutils.arg(
    'attributes',
    metavar='<path=value>',
    nargs='+',
    action='append',
    default=[],
    help=_("Attribute to add, replace, or remove. Can be specified multiple "
           "times. For 'remove', only <path> is necessary."))
def do_volume_target_update(cc, args):
    """Update information about a volume target."""
    patch = utils.args_array_to_patch(args.op, args.attributes[0])
    volume_target = cc.volume_target.update(args.volume_target, patch)
    _print_volume_target_show(volume_target, json=args.json)
