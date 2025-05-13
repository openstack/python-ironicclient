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


class CreateBaremetalVolumeConnector(command.ShowOne):
    """Create a new baremetal volume connector."""

    log = logging.getLogger(__name__ + ".CreateBaremetalVolumeConnector")

    def get_parser(self, prog_name):
        parser = (
            super(CreateBaremetalVolumeConnector, self).get_parser(prog_name))

        parser.add_argument(
            '--node',
            dest='node_uuid',
            metavar='<uuid>',
            required=True,
            help=_('UUID of the node that this volume connector belongs to.'))
        parser.add_argument(
            '--type',
            dest='type',
            metavar="<type>",
            required=True,
            choices=('iqn', 'ip', 'mac', 'wwnn', 'wwpn', 'port', 'portgroup'),
            help=_("Type of the volume connector. Can be 'iqn', 'ip', 'mac', "
                   "'wwnn', 'wwpn', 'port', 'portgroup'."))
        parser.add_argument(
            '--connector-id',
            dest='connector_id',
            required=True,
            metavar="<connector id>",
            help=_("ID of the volume connector in the specified type. For "
                   "example, the iSCSI initiator IQN for the node if the type "
                   "is 'iqn'."))
        parser.add_argument(
            '--uuid',
            dest='uuid',
            metavar='<uuid>',
            help=_("UUID of the volume connector."))
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

        field_list = ['extra', 'type', 'connector_id', 'node_uuid', 'uuid']
        fields = dict((k, v) for (k, v) in vars(parsed_args).items()
                      if k in field_list and v is not None)
        fields = utils.args_array_to_dict(fields, 'extra')
        volume_connector = baremetal_client.volume_connector.create(**fields)

        data = dict([(f, getattr(volume_connector, f, '')) for f in
                     res_fields.VOLUME_CONNECTOR_DETAILED_RESOURCE.fields])
        return self.dict2columns(data)


class ShowBaremetalVolumeConnector(command.ShowOne):
    """Show baremetal volume connector details."""

    log = logging.getLogger(__name__ + ".ShowBaremetalVolumeConnector")

    def get_parser(self, prog_name):
        parser = (
            super(ShowBaremetalVolumeConnector, self).get_parser(prog_name))

        parser.add_argument(
            'volume_connector',
            metavar='<id>',
            help=_("UUID of the volume connector."))
        parser.add_argument(
            '--fields',
            nargs='+',
            dest='fields',
            metavar='<field>',
            action='append',
            choices=res_fields.VOLUME_CONNECTOR_DETAILED_RESOURCE.fields,
            default=[],
            help=_("One or more volume connector fields. Only these fields "
                   "will be fetched from the server."))
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal
        fields = list(itertools.chain.from_iterable(parsed_args.fields))
        fields = fields if fields else None

        volume_connector = baremetal_client.volume_connector.get(
            parsed_args.volume_connector, fields=fields)._info

        volume_connector.pop("links", None)
        return zip(*sorted(volume_connector.items()))


class ListBaremetalVolumeConnector(command.Lister):
    """List baremetal volume connectors."""

    log = logging.getLogger(__name__ + ".ListBaremetalVolumeConnector")

    def get_parser(self, prog_name):
        parser = (
            super(ListBaremetalVolumeConnector, self).get_parser(prog_name))

        parser.add_argument(
            '--node',
            dest='node',
            metavar='<node>',
            help=_("Only list volume connectors of this node (name or UUID)."))
        parser.add_argument(
            '--limit',
            dest='limit',
            metavar='<limit>',
            type=int,
            help=_('Maximum number of volume connectors to return per '
                   'request, 0 for no limit. Default is the maximum number '
                   'used by the Baremetal API Service.'))
        parser.add_argument(
            '--marker',
            dest='marker',
            metavar='<volume connector>',
            help=_('Volume connector UUID (for example, of the last volume '
                   'connector in the list from a previous request). Returns '
                   'the list of volume connectors after this UUID.'))
        parser.add_argument(
            '--sort',
            dest='sort',
            metavar='<key>[:<direction>]',
            help=_('Sort output by specified volume connector fields and '
                   'directions (asc or desc) (default:asc). Multiple fields '
                   'and directions can be specified, separated by comma.'))

        display_group = parser.add_mutually_exclusive_group(required=False)
        display_group.add_argument(
            '--long',
            dest='detail',
            action='store_true',
            default=False,
            help=_("Show detailed information about volume connectors."))
        display_group.add_argument(
            '--fields',
            nargs='+',
            dest='fields',
            metavar='<field>',
            action='append',
            default=[],
            choices=res_fields.VOLUME_CONNECTOR_DETAILED_RESOURCE.fields,
            help=_("One or more volume connector fields. Only these fields "
                   "will be fetched from the server. Can not be used when "
                   "'--long' is specified."))
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)" % parsed_args)
        client = self.app.client_manager.baremetal

        columns = res_fields.VOLUME_CONNECTOR_RESOURCE.fields
        labels = res_fields.VOLUME_CONNECTOR_RESOURCE.labels

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
            columns = res_fields.VOLUME_CONNECTOR_DETAILED_RESOURCE.fields
            labels = res_fields.VOLUME_CONNECTOR_DETAILED_RESOURCE.labels
        elif parsed_args.fields:
            params['detail'] = False
            fields = itertools.chain.from_iterable(parsed_args.fields)
            resource = res_fields.Resource(list(fields))
            columns = resource.fields
            labels = resource.labels
            params['fields'] = columns

        self.log.debug("params(%s)" % params)
        data = client.volume_connector.list(**params)

        data = oscutils.sort_items(data, parsed_args.sort)

        return (labels,
                (oscutils.get_item_properties(s, columns, formatters={
                    'Properties': utils.HashColumn},) for s in data))


class DeleteBaremetalVolumeConnector(command.Command):
    """Unregister baremetal volume connector(s)."""

    log = logging.getLogger(__name__ + ".DeleteBaremetalVolumeConnector")

    def get_parser(self, prog_name):
        parser = (
            super(DeleteBaremetalVolumeConnector, self).get_parser(prog_name))
        parser.add_argument(
            'volume_connectors',
            metavar='<volume connector>',
            nargs='+',
            help=_("UUID(s) of the volume connector(s) to delete."))

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        failures = []
        for volume_connector in parsed_args.volume_connectors:
            try:
                baremetal_client.volume_connector.delete(volume_connector)
                print(_('Deleted volume connector %s') % volume_connector)
            except exc.ClientException as e:
                failures.append(_("Failed to delete volume connector "
                                  "%(volume_connector)s: %(error)s")
                                % {'volume_connector': volume_connector,
                                   'error': e})

        if failures:
            raise exc.ClientException("\n".join(failures))


class SetBaremetalVolumeConnector(command.Command):
    """Set baremetal volume connector properties."""

    log = logging.getLogger(__name__ + ".SetBaremetalVolumeConnector")

    def get_parser(self, prog_name):
        parser = (
            super(SetBaremetalVolumeConnector, self).get_parser(prog_name))

        parser.add_argument(
            'volume_connector',
            metavar='<volume connector>',
            help=_("UUID of the volume connector."))
        parser.add_argument(
            '--node',
            dest='node_uuid',
            metavar='<uuid>',
            help=_('UUID of the node that this volume connector belongs to.'))
        parser.add_argument(
            '--type',
            dest='type',
            metavar="<type>",
            choices=('iqn', 'ip', 'mac', 'wwnn', 'wwpn', 'port', 'portgroup'),
            help=_("Type of the volume connector. Can be 'iqn', 'ip', 'mac', "
                   "'wwnn', 'wwpn', 'port', 'portgroup'."))
        parser.add_argument(
            '--connector-id',
            dest='connector_id',
            metavar="<connector id>",
            help=_("ID of the volume connector in the specified type."))
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

        properties = []
        if parsed_args.node_uuid:
            properties.extend(utils.args_array_to_patch(
                'add', ["node_uuid=%s" % parsed_args.node_uuid]))
        if parsed_args.type:
            properties.extend(utils.args_array_to_patch(
                'add', ["type=%s" % parsed_args.type]))
        if parsed_args.connector_id:
            properties.extend(utils.args_array_to_patch(
                'add', ["connector_id=%s" % parsed_args.connector_id]))

        if parsed_args.extra:
            properties.extend(utils.args_array_to_patch(
                'add', ["extra/" + x for x in parsed_args.extra]))

        if properties:
            baremetal_client.volume_connector.update(
                parsed_args.volume_connector, properties)
        else:
            self.log.warning("Please specify what to set.")


class UnsetBaremetalVolumeConnector(command.Command):
    """Unset baremetal volume connector properties."""
    log = logging.getLogger(__name__ + "UnsetBaremetalVolumeConnector")

    def get_parser(self, prog_name):
        parser = (
            super(UnsetBaremetalVolumeConnector, self).get_parser(prog_name))

        parser.add_argument(
            'volume_connector',
            metavar='<volume connector>',
            help=_("UUID of the volume connector."))
        parser.add_argument(
            '--extra',
            dest='extra',
            metavar="<key>",
            action='append',
            help=_('Extra to unset (repeat option to unset multiple extras)'))

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        properties = []
        if parsed_args.extra:
            properties.extend(utils.args_array_to_patch('remove',
                              ['extra/' + x for x in parsed_args.extra]))

        if properties:
            baremetal_client.volume_connector.update(
                parsed_args.volume_connector, properties)
        else:
            self.log.warning("Please specify what to unset.")
