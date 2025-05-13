# Copyright 2017 FUJITSU LIMITED
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import itertools
import logging

from osc_lib.command import command
from osc_lib import utils as oscutils

from ironicclient.common.i18n import _
from ironicclient.common import utils
from ironicclient import exc
from ironicclient.v1 import resource_fields as res_fields


class CreateBaremetalVolumeTarget(command.ShowOne):
    """Create a new baremetal volume target."""

    log = logging.getLogger(__name__ + ".CreateBaremetalVolumeTarget")

    def get_parser(self, prog_name):
        parser = super(CreateBaremetalVolumeTarget, self).get_parser(prog_name)

        parser.add_argument(
            '--node',
            dest='node_uuid',
            metavar='<uuid>',
            required=True,
            help=_('UUID of the node that this volume target belongs to.'))
        parser.add_argument(
            '--type',
            dest='volume_type',
            metavar="<volume type>",
            required=True,
            help=_("Type of the volume target, e.g. 'iscsi', "
                   "'fibre_channel'."))
        parser.add_argument(
            '--property',
            dest='properties',
            metavar="<key=value>",
            action='append',
            help=_("Key/value property related to the type of this volume "
                   "target. Can be specified multiple times."
                   ))
        parser.add_argument(
            '--boot-index',
            dest='boot_index',
            metavar="<boot index>",
            type=int,
            required=True,
            help=_("Boot index of the volume target."))
        parser.add_argument(
            '--volume-id',
            dest='volume_id',
            metavar="<volume id>",
            required=True,
            help=_("ID of the volume associated with this target."))
        parser.add_argument(
            '--uuid',
            dest='uuid',
            metavar='<uuid>',
            help=_("UUID of the volume target."))
        parser.add_argument(
            '--extra',
            dest='extra',
            metavar="<key=value>",
            action='append',
            help=_("Record arbitrary key/value metadata. "
                   "Can be specified multiple times."))

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)" % parsed_args)
        baremetal_client = self.app.client_manager.baremetal

        if parsed_args.boot_index < 0:
            raise exc.CommandError(
                _('Expected non-negative --boot-index, got %s') %
                parsed_args.boot_index)

        field_list = ['extra', 'volume_type', 'properties',
                      'boot_index', 'node_uuid', 'volume_id', 'uuid']
        fields = dict((k, v) for (k, v) in vars(parsed_args).items()
                      if k in field_list and v is not None)
        fields = utils.args_array_to_dict(fields, 'properties')
        fields = utils.args_array_to_dict(fields, 'extra')
        volume_target = baremetal_client.volume_target.create(**fields)

        data = dict([(f, getattr(volume_target, f, '')) for f in
                     res_fields.VOLUME_TARGET_DETAILED_RESOURCE.fields])
        return self.dict2columns(data)


class ShowBaremetalVolumeTarget(command.ShowOne):
    """Show baremetal volume target details."""

    log = logging.getLogger(__name__ + ".ShowBaremetalVolumeTarget")

    def get_parser(self, prog_name):
        parser = super(ShowBaremetalVolumeTarget, self).get_parser(prog_name)

        parser.add_argument(
            'volume_target',
            metavar='<id>',
            help=_("UUID of the volume target."))
        parser.add_argument(
            '--fields',
            nargs='+',
            dest='fields',
            metavar='<field>',
            action='append',
            default=[],
            choices=res_fields.VOLUME_TARGET_DETAILED_RESOURCE.fields,
            help=_("One or more volume target fields. Only these fields will "
                   "be fetched from the server."))
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal
        fields = list(itertools.chain.from_iterable(parsed_args.fields))
        fields = fields if fields else None

        volume_target = baremetal_client.volume_target.get(
            parsed_args.volume_target, fields=fields)._info

        volume_target.pop("links", None)
        return zip(*sorted(volume_target.items()))


class ListBaremetalVolumeTarget(command.Lister):
    """List baremetal volume targets."""

    log = logging.getLogger(__name__ + ".ListBaremetalVolumeTarget")

    def get_parser(self, prog_name):
        parser = super(ListBaremetalVolumeTarget, self).get_parser(prog_name)

        parser.add_argument(
            '--node',
            dest='node',
            metavar='<node>',
            help=_("Only list volume targets of this node (name or UUID)."))
        parser.add_argument(
            '--limit',
            dest='limit',
            metavar='<limit>',
            type=int,
            help=_('Maximum number of volume targets to return per request, '
                   '0 for no limit. Default is the maximum number used '
                   'by the Baremetal API Service.'))
        parser.add_argument(
            '--marker',
            dest='marker',
            metavar='<volume target>',
            help=_('Volume target UUID (for example, of the last '
                   'volume target in the list from a previous request). '
                   'Returns the list of volume targets after this UUID.'))
        parser.add_argument(
            '--sort',
            dest='sort',
            metavar='<key>[:<direction>]',
            help=_('Sort output by specified volume target fields and '
                   'directions (asc or desc) (default:asc). Multiple fields '
                   'and directions can be specified, separated by comma.'))

        display_group = parser.add_mutually_exclusive_group(required=False)
        display_group.add_argument(
            '--long',
            dest='detail',
            action='store_true',
            default=False,
            help=_("Show detailed information about volume targets."))
        display_group.add_argument(
            '--fields',
            nargs='+',
            dest='fields',
            metavar='<field>',
            action='append',
            default=[],
            choices=res_fields.VOLUME_TARGET_DETAILED_RESOURCE.fields,
            help=_("One or more volume target fields. Only these fields will "
                   "be fetched from the server. Can not be used when "
                   "'--long' is specified."))
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)" % parsed_args)
        client = self.app.client_manager.baremetal

        columns = res_fields.VOLUME_TARGET_RESOURCE.fields
        labels = res_fields.VOLUME_TARGET_RESOURCE.labels

        params = {}
        if parsed_args.limit is not None and parsed_args.limit < 0:
            raise exc.CommandError(
                _('Expected non-negative --limit, got %s') %
                parsed_args.limit)
        params['limit'] = parsed_args.limit
        params['marker'] = parsed_args.marker
        if parsed_args.node is not None:
            params['node'] = parsed_args.node

        if parsed_args.detail:
            params['detail'] = parsed_args.detail
            columns = res_fields.VOLUME_TARGET_DETAILED_RESOURCE.fields
            labels = res_fields.VOLUME_TARGET_DETAILED_RESOURCE.labels
        elif parsed_args.fields:
            params['detail'] = False
            fields = itertools.chain.from_iterable(parsed_args.fields)
            resource = res_fields.Resource(list(fields))
            columns = resource.fields
            labels = resource.labels
            params['fields'] = columns

        self.log.debug("params(%s)" % params)
        data = client.volume_target.list(**params)

        data = oscutils.sort_items(data, parsed_args.sort)

        return (labels,
                (oscutils.get_item_properties(s, columns, formatters={
                    'Properties': utils.HashColumn},) for s in data))


class DeleteBaremetalVolumeTarget(command.Command):
    """Unregister baremetal volume target(s)."""

    log = logging.getLogger(__name__ + ".DeleteBaremetalVolumeTarget")

    def get_parser(self, prog_name):
        parser = (
            super(DeleteBaremetalVolumeTarget, self).get_parser(prog_name))
        parser.add_argument(
            'volume_targets',
            metavar='<volume target>',
            nargs='+',
            help=_("UUID(s) of the volume target(s) to delete."))

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        failures = []
        for volume_target in parsed_args.volume_targets:
            try:
                baremetal_client.volume_target.delete(volume_target)
                print(_('Deleted volume target %s') % volume_target)
            except exc.ClientException as e:
                failures.append(_("Failed to delete volume target "
                                  "%(volume_target)s: %(error)s")
                                % {'volume_target': volume_target,
                                   'error': e})

        if failures:
            raise exc.ClientException("\n".join(failures))


class SetBaremetalVolumeTarget(command.Command):
    """Set baremetal volume target properties."""

    log = logging.getLogger(__name__ + ".SetBaremetalVolumeTarget")

    def get_parser(self, prog_name):
        parser = (
            super(SetBaremetalVolumeTarget, self).get_parser(prog_name))

        parser.add_argument(
            'volume_target',
            metavar='<volume target>',
            help=_("UUID of the volume target."))
        parser.add_argument(
            '--node',
            dest='node_uuid',
            metavar='<uuid>',
            help=_('UUID of the node that this volume target belongs to.'))
        parser.add_argument(
            '--type',
            dest='volume_type',
            metavar="<volume type>",
            help=_("Type of the volume target, e.g. 'iscsi', "
                   "'fibre_channel'."))
        parser.add_argument(
            '--property',
            dest='properties',
            metavar="<key=value>",
            action='append',
            help=_("Key/value property related to the type of this volume "
                   "target. Can be specified multiple times."))
        parser.add_argument(
            '--boot-index',
            dest='boot_index',
            metavar="<boot index>",
            type=int,
            help=_("Boot index of the volume target."))
        parser.add_argument(
            '--volume-id',
            dest='volume_id',
            metavar="<volume id>",
            help=_("ID of the volume associated with this target."))
        parser.add_argument(
            '--extra',
            dest='extra',
            metavar="<key=value>",
            action='append',
            help=_("Record arbitrary key/value metadata. "
                   "Can be specified multiple times."))

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        if parsed_args.boot_index is not None and parsed_args.boot_index < 0:
            raise exc.CommandError(
                _('Expected non-negative --boot-index, got %s') %
                parsed_args.boot_index)

        properties = []
        if parsed_args.node_uuid:
            properties.extend(utils.args_array_to_patch(
                'add', ["node_uuid=%s" % parsed_args.node_uuid]))
        if parsed_args.volume_type:
            properties.extend(utils.args_array_to_patch(
                'add', ["volume_type=%s" % parsed_args.volume_type]))
        if parsed_args.boot_index:
            properties.extend(utils.args_array_to_patch(
                'add', ["boot_index=%s" % parsed_args.boot_index]))
        if parsed_args.volume_id:
            properties.extend(utils.args_array_to_patch(
                'add', ["volume_id=%s" % parsed_args.volume_id]))

        if parsed_args.properties:
            properties.extend(utils.args_array_to_patch(
                'add', ["properties/" + x for x in parsed_args.properties]))
        if parsed_args.extra:
            properties.extend(utils.args_array_to_patch(
                'add', ["extra/" + x for x in parsed_args.extra]))

        if properties:
            baremetal_client.volume_target.update(
                parsed_args.volume_target, properties)
        else:
            self.log.warning("Please specify what to set.")


class UnsetBaremetalVolumeTarget(command.Command):
    """Unset baremetal volume target properties."""
    log = logging.getLogger(__name__ + "UnsetBaremetalVolumeTarget")

    def get_parser(self, prog_name):
        parser = (
            super(UnsetBaremetalVolumeTarget, self).get_parser(prog_name))

        parser.add_argument(
            'volume_target',
            metavar='<volume target>',
            help=_("UUID of the volume target."))
        parser.add_argument(
            '--extra',
            dest='extra',
            metavar="<key>",
            action='append',
            help=_('Extra to unset (repeat option to unset multiple extras)'))
        parser.add_argument(
            "--property",
            dest='properties',
            metavar="<key>",
            action='append',
            help='Property to unset on this baremetal volume target '
                 '(repeat option to unset multiple properties).',
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        properties = []
        if parsed_args.extra:
            properties.extend(utils.args_array_to_patch('remove',
                              ['extra/' + x for x in parsed_args.extra]))
        if parsed_args.properties:
            properties.extend(utils.args_array_to_patch(
                'remove', ['properties/' + x for x in parsed_args.properties]))

        if properties:
            baremetal_client.volume_target.update(
                parsed_args.volume_target, properties)
        else:
            self.log.warning("Please specify what to unset.")
