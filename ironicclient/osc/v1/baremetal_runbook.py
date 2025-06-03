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

import itertools
import json
import logging

from osc_lib.command import command
from osc_lib import utils as oscutils

from ironicclient.common.i18n import _
from ironicclient.common import utils
from ironicclient import exc
from ironicclient.v1 import resource_fields as res_fields


_RUNBOOK_STEPS_HELP = _(
    "The runbook steps. May be the path to a YAML file containing the "
    "runbook steps; OR '-', with the runbook steps being read from standard "
    "input; OR a JSON string. The value should be a list of runbook step "
    "dictionaries; each dictionary should have keys 'interface', 'step', "
    "'args' and 'order'.")


class CreateBaremetalRunbook(command.ShowOne):
    """Create a new runbook"""

    log = logging.getLogger(__name__ + ".CreateBaremetalRunbook")

    def get_parser(self, prog_name):
        parser = super(CreateBaremetalRunbook, self).get_parser(
            prog_name)

        parser.add_argument(
            '--name',
            metavar='<name>',
            required=True,
            help=_('Unique name for this runbook. Must be a valid '
                   'trait name')
        )
        parser.add_argument(
            '--uuid',
            dest='uuid',
            metavar='<uuid>',
            help=_('UUID of the runbook.'))
        parser.add_argument(
            '--public',
            dest='public',
            nargs='?',
            const='true',
            metavar='<public>',
            help=_('Whether the runbook will be private or public.')
        )
        parser.add_argument(
            '--owner',
            metavar='<owner>',
            help=_('Owner of the runbook.')
        )
        parser.add_argument(
            '--extra',
            metavar="<key=value>",
            action='append',
            help=_("Record arbitrary key/value metadata. "
                   "Can be specified multiple times."))
        parser.add_argument(
            '--steps',
            metavar="<steps>",
            required=True,
            help=_RUNBOOK_STEPS_HELP
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        baremetal_client = self.app.client_manager.baremetal

        steps = utils.handle_json_arg(parsed_args.steps, 'runbook steps')

        field_list = ['name', 'uuid', 'owner', 'public', 'extra']
        fields = dict((k, v) for (k, v) in vars(parsed_args).items()
                      if k in field_list and v is not None)
        if parsed_args.public is not None:
            fields['public'] = utils.bool_argument_value(
                '--public', parsed_args.public, strict=True)
        fields = utils.args_array_to_dict(fields, 'extra')
        runbook = baremetal_client.runbook.create(steps=steps,
                                                  **fields)

        data = dict([(f, getattr(runbook, f, '')) for f in
                     res_fields.RUNBOOK_DETAILED_RESOURCE.fields])

        return self.dict2columns(data)


class ShowBaremetalRunbook(command.ShowOne):
    """Show baremetal runbook details."""

    log = logging.getLogger(__name__ + ".ShowBaremetalRunbook")

    def get_parser(self, prog_name):
        parser = super(ShowBaremetalRunbook, self).get_parser(prog_name)
        parser.add_argument(
            "runbook",
            metavar="<runbook>",
            help=_("Name or UUID of the runbook.")
        )
        parser.add_argument(
            '--fields',
            nargs='+',
            dest='fields',
            metavar='<field>',
            action='append',
            choices=res_fields.RUNBOOK_DETAILED_RESOURCE.fields,
            default=[],
            help=_("One or more runbook fields. Only these fields "
                   "will be fetched from the server.")
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal
        fields = list(itertools.chain.from_iterable(parsed_args.fields))
        fields = fields if fields else None

        runbook = baremetal_client.runbook.get(
            parsed_args.runbook, fields=fields)._info

        runbook.pop("links", None)
        return zip(*sorted(runbook.items()))


class SetBaremetalRunbook(command.Command):
    """Set baremetal runbook properties."""

    log = logging.getLogger(__name__ + ".SetBaremetalRunbook")

    def get_parser(self, prog_name):
        parser = super(SetBaremetalRunbook, self).get_parser(prog_name)

        parser.add_argument(
            'runbook',
            metavar='<runbook>',
            help=_("Name or UUID of the runbook")
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Set unique name of the runbook. Must be a valid '
                   'trait name.')
        )
        parser.add_argument(
            '--public',
            dest='public',
            nargs='?',
            const='true',
            metavar='<public>',
            help=_('Make a private runbook public.')
        )
        parser.add_argument(
            '--owner',
            metavar='<owner>',
            help=_('Set owner of a runbook.')
        )
        parser.add_argument(
            '--steps',
            metavar="<steps>",
            help=_RUNBOOK_STEPS_HELP
        )
        parser.add_argument(
            "--extra",
            metavar="<key=value>",
            action='append',
            help=_('Extra to set on this baremetal runbook '
                   '(repeat option to set multiple extras).'),
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        properties = []
        if parsed_args.name:
            name = ["name=%s" % parsed_args.name]
            properties.extend(utils.args_array_to_patch('add', name))
        if parsed_args.owner:
            owner = ["owner=%s" % parsed_args.owner]
            properties.extend(utils.args_array_to_patch('add', owner))
        if parsed_args.public is not None:
            to_bool = utils.bool_argument_value(
                '--public', parsed_args.public, strict=True)
            public = ["public=%s" % to_bool]
            properties.extend(utils.args_array_to_patch('add', public))
        if parsed_args.steps:
            steps = utils.handle_json_arg(parsed_args.steps, 'runbook steps')
            steps = ["steps=%s" % json.dumps(steps)]
            properties.extend(utils.args_array_to_patch('add', steps))
        if parsed_args.extra:
            properties.extend(utils.args_array_to_patch(
                'add', ['extra/' + x for x in parsed_args.extra]))

        if properties:
            baremetal_client.runbook.update(parsed_args.runbook,
                                            properties)
        else:
            self.log.warning("Please specify what to set.")


class UnsetBaremetalRunbook(command.Command):
    """Unset baremetal runbook properties."""
    log = logging.getLogger(__name__ + ".UnsetBaremetalRunbook")

    def get_parser(self, prog_name):
        parser = super(UnsetBaremetalRunbook, self).get_parser(
            prog_name)

        parser.add_argument(
            'runbook',
            metavar='<runbook>',
            help=_("Name or UUID of the runbook")
        )
        parser.add_argument(
            '--name',
            action='store_true',
            help=_('Unset the name of the runbook.')
        )
        parser.add_argument(
            '--public',
            dest='public',
            action='store_true',
            help=_('Make a public runbook private.')
        )
        parser.add_argument(
            '--owner',
            dest='owner',
            action='store_true',
            help=_('Unset owner of a runbook.')
        )
        parser.add_argument(
            "--step",
            metavar="<key>",
            action='append',
            help=_('Step to unset on this baremetal runbook '
                   '(repeat option to unset multiple steps).'),
        )
        parser.add_argument(
            "--extra",
            metavar="<key>",
            action='append',
            help=_('Extra to unset on this baremetal runbook '
                   '(repeat option to unset multiple extras).'),
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        properties = []
        for field in ['name', 'owner', 'public']:
            if getattr(parsed_args, field):
                properties.extend(utils.args_array_to_patch('remove', [field]))

        if parsed_args.extra:
            properties.extend(utils.args_array_to_patch('remove',
                              ['extra/' + x for x in parsed_args.extra]))
        if parsed_args.step:
            properties.extend(utils.args_array_to_patch('remove',
                              ['step/' + x for x in parsed_args.step]))

        if properties:
            baremetal_client.runbook.update(parsed_args.runbook,
                                            properties)
        else:
            self.log.warning("Please specify what to unset.")


class DeleteBaremetalRunbook(command.Command):
    """Delete runbook(s)."""

    log = logging.getLogger(__name__ + ".DeleteBaremetalRunbook")

    def get_parser(self, prog_name):
        parser = super(DeleteBaremetalRunbook, self).get_parser(
            prog_name)
        parser.add_argument(
            "runbooks",
            metavar="<runbook>",
            nargs="+",
            help=_("Name(s) or UUID(s) of the runbook(s) to delete.")
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        failures = []
        for runbook in parsed_args.runbooks:
            try:
                baremetal_client.runbook.delete(runbook)
                print(_('Deleted runbook %s') % runbook)
            except exc.ClientException as e:
                failures.append(_("Failed to delete runbook "
                                  "%(runbook)s: %(error)s")
                                % {'runbook': runbook, 'error': e})

        if failures:
            raise exc.ClientException("\n".join(failures))


class ListBaremetalRunbook(command.Lister):
    """List baremetal runbooks."""

    log = logging.getLogger(__name__ + ".ListBaremetalRunbook")

    def get_parser(self, prog_name):
        parser = super(ListBaremetalRunbook, self).get_parser(prog_name)
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            type=int,
            help=_('Maximum number of runbooks to return per request, '
                   '0 for no limit. Default is the maximum number used '
                   'by the Baremetal API Service.')
        )
        parser.add_argument(
            '--marker',
            metavar='<runbook>',
            help=_('Runbook UUID (for example, of the last runbook '
                   'in the list from a previous request). Returns '
                   'the list of runbooks after this UUID.')
        )
        parser.add_argument(
            '--sort',
            metavar="<key>[:<direction>]",
            help=_('Sort output by specified runbook fields and '
                   'directions (asc or desc) (default: asc). Multiple fields '
                   'and directions can be specified, separated by comma.')
        )
        display_group = parser.add_mutually_exclusive_group()
        display_group.add_argument(
            '--long',
            dest='detail',
            action='store_true',
            default=False,
            help=_("Show detailed information about runbooks.")
        )
        display_group.add_argument(
            '--fields',
            nargs='+',
            dest='fields',
            metavar='<field>',
            action='append',
            default=[],
            choices=res_fields.RUNBOOK_DETAILED_RESOURCE.fields,
            help=_("One or more runbook fields. Only these fields "
                   "will be fetched from the server. Can not be used when "
                   "'--long' is specified.")
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.baremetal

        columns = res_fields.RUNBOOK_RESOURCE.fields
        labels = res_fields.RUNBOOK_RESOURCE.labels

        params = {}
        if parsed_args.limit is not None and parsed_args.limit < 0:
            raise exc.CommandError(
                _('Expected non-negative --limit, got %s') %
                parsed_args.limit)
        params['limit'] = parsed_args.limit
        params['marker'] = parsed_args.marker

        if parsed_args.detail:
            params['detail'] = parsed_args.detail
            columns = res_fields.RUNBOOK_DETAILED_RESOURCE.fields
            labels = res_fields.RUNBOOK_DETAILED_RESOURCE.labels

        elif parsed_args.fields:
            params['detail'] = False
            fields = itertools.chain.from_iterable(parsed_args.fields)
            resource = res_fields.Resource(list(fields))
            columns = resource.fields
            labels = resource.labels
            params['fields'] = columns

        self.log.debug("params(%s)", params)
        data = client.runbook.list(**params)

        data = oscutils.sort_items(data, parsed_args.sort)

        return (labels,
                (oscutils.get_item_properties(s, columns) for s in data))
