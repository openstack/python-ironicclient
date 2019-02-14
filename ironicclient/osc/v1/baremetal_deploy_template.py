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


_DEPLOY_STEPS_HELP = _(
    "The deploy steps in JSON format. May be the path to a file containing "
    "the deploy steps; OR '-', with the deploy steps being read from standard "
    "input; OR a string. The value should be a list of deploy-step "
    "dictionaries; each dictionary should have keys 'interface', 'step', "
    "'args' and 'priority'.")


class CreateBaremetalDeployTemplate(command.ShowOne):
    """Create a new deploy template"""

    log = logging.getLogger(__name__ + ".CreateBaremetalDeployTemplate")

    def get_parser(self, prog_name):
        parser = super(CreateBaremetalDeployTemplate, self).get_parser(
            prog_name)

        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('Unique name for this deploy template. Must be a valid '
                   'trait name')
        )
        parser.add_argument(
            '--uuid',
            dest='uuid',
            metavar='<uuid>',
            help=_('UUID of the deploy template.'))
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
            help=_DEPLOY_STEPS_HELP
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        baremetal_client = self.app.client_manager.baremetal

        steps = utils.handle_json_arg(parsed_args.steps, 'deploy steps')

        field_list = ['name', 'uuid', 'extra']
        fields = dict((k, v) for (k, v) in vars(parsed_args).items()
                      if k in field_list and v is not None)
        fields = utils.args_array_to_dict(fields, 'extra')
        template = baremetal_client.deploy_template.create(steps=steps,
                                                           **fields)

        data = dict([(f, getattr(template, f, '')) for f in
                     res_fields.DEPLOY_TEMPLATE_DETAILED_RESOURCE.fields])

        return self.dict2columns(data)


class ShowBaremetalDeployTemplate(command.ShowOne):
    """Show baremetal deploy template details."""

    log = logging.getLogger(__name__ + ".ShowBaremetalDeployTemplate")

    def get_parser(self, prog_name):
        parser = super(ShowBaremetalDeployTemplate, self).get_parser(prog_name)
        parser.add_argument(
            "template",
            metavar="<template>",
            help=_("Name or UUID of the deploy template.")
        )
        parser.add_argument(
            '--fields',
            nargs='+',
            dest='fields',
            metavar='<field>',
            action='append',
            choices=res_fields.DEPLOY_TEMPLATE_DETAILED_RESOURCE.fields,
            default=[],
            help=_("One or more deploy template fields. Only these fields "
                   "will be fetched from the server.")
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal
        fields = list(itertools.chain.from_iterable(parsed_args.fields))
        fields = fields if fields else None

        template = baremetal_client.deploy_template.get(
            parsed_args.template, fields=fields)._info

        template.pop("links", None)
        return zip(*sorted(template.items()))


class SetBaremetalDeployTemplate(command.Command):
    """Set baremetal deploy template properties."""

    log = logging.getLogger(__name__ + ".SetBaremetalDeployTemplate")

    def get_parser(self, prog_name):
        parser = super(SetBaremetalDeployTemplate, self).get_parser(prog_name)

        parser.add_argument(
            'template',
            metavar='<template>',
            help=_("Name or UUID of the deploy template")
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Set unique name of the deploy template. Must be a valid '
                   'trait name.')
        )
        parser.add_argument(
            '--steps',
            metavar="<steps>",
            help=_DEPLOY_STEPS_HELP
        )
        parser.add_argument(
            "--extra",
            metavar="<key=value>",
            action='append',
            help=_('Extra to set on this baremetal deploy template '
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
        if parsed_args.steps:
            steps = utils.handle_json_arg(parsed_args.steps, 'deploy steps')
            steps = ["steps=%s" % json.dumps(steps)]
            properties.extend(utils.args_array_to_patch('add', steps))
        if parsed_args.extra:
            properties.extend(utils.args_array_to_patch(
                'add', ['extra/' + x for x in parsed_args.extra]))

        if properties:
            baremetal_client.deploy_template.update(parsed_args.template,
                                                    properties)
        else:
            self.log.warning("Please specify what to set.")


class UnsetBaremetalDeployTemplate(command.Command):
    """Unset baremetal deploy template properties."""
    log = logging.getLogger(__name__ + ".UnsetBaremetalDeployTemplate")

    def get_parser(self, prog_name):
        parser = super(UnsetBaremetalDeployTemplate, self).get_parser(
            prog_name)

        parser.add_argument(
            'template',
            metavar='<template>',
            help=_("Name or UUID of the deploy template")
        )
        parser.add_argument(
            "--extra",
            metavar="<key>",
            action='append',
            help=_('Extra to unset on this baremetal deploy template '
                   '(repeat option to unset multiple extras).'),
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        properties = []
        if parsed_args.extra:
            properties.extend(utils.args_array_to_patch('remove',
                              ['extra/' + x for x in parsed_args.extra]))

        if properties:
            baremetal_client.deploy_template.update(parsed_args.template,
                                                    properties)
        else:
            self.log.warning("Please specify what to unset.")


class DeleteBaremetalDeployTemplate(command.Command):
    """Delete deploy template(s)."""

    log = logging.getLogger(__name__ + ".DeleteBaremetalDeployTemplate")

    def get_parser(self, prog_name):
        parser = super(DeleteBaremetalDeployTemplate, self).get_parser(
            prog_name)
        parser.add_argument(
            "templates",
            metavar="<template>",
            nargs="+",
            help=_("Name(s) or UUID(s) of the deploy template(s) to delete.")
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        failures = []
        for template in parsed_args.templates:
            try:
                baremetal_client.deploy_template.delete(template)
                print(_('Deleted deploy template %s') % template)
            except exc.ClientException as e:
                failures.append(_("Failed to delete deploy template "
                                  "%(template)s: %(error)s")
                                % {'template': template, 'error': e})

        if failures:
            raise exc.ClientException("\n".join(failures))


class ListBaremetalDeployTemplate(command.Lister):
    """List baremetal deploy templates."""

    log = logging.getLogger(__name__ + ".ListBaremetalDeployTemplate")

    def get_parser(self, prog_name):
        parser = super(ListBaremetalDeployTemplate, self).get_parser(prog_name)
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            type=int,
            help=_('Maximum number of deploy templates to return per request, '
                   '0 for no limit. Default is the maximum number used '
                   'by the Baremetal API Service.')
        )
        parser.add_argument(
            '--marker',
            metavar='<template>',
            help=_('DeployTemplate UUID (for example, of the last deploy '
                   'template in the list from a previous request). Returns '
                   'the list of deploy templates after this UUID.')
        )
        parser.add_argument(
            '--sort',
            metavar="<key>[:<direction>]",
            help=_('Sort output by specified deploy template fields and '
                   'directions (asc or desc) (default: asc). Multiple fields '
                   'and directions can be specified, separated by comma.')
        )
        display_group = parser.add_mutually_exclusive_group()
        display_group.add_argument(
            '--long',
            dest='detail',
            action='store_true',
            default=False,
            help=_("Show detailed information about deploy templates.")
        )
        display_group.add_argument(
            '--fields',
            nargs='+',
            dest='fields',
            metavar='<field>',
            action='append',
            default=[],
            choices=res_fields.DEPLOY_TEMPLATE_DETAILED_RESOURCE.fields,
            help=_("One or more deploy template fields. Only these fields "
                   "will be fetched from the server. Can not be used when "
                   "'--long' is specified.")
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.baremetal

        columns = res_fields.DEPLOY_TEMPLATE_RESOURCE.fields
        labels = res_fields.DEPLOY_TEMPLATE_RESOURCE.labels

        params = {}
        if parsed_args.limit is not None and parsed_args.limit < 0:
            raise exc.CommandError(
                _('Expected non-negative --limit, got %s') %
                parsed_args.limit)
        params['limit'] = parsed_args.limit
        params['marker'] = parsed_args.marker

        if parsed_args.detail:
            params['detail'] = parsed_args.detail
            columns = res_fields.DEPLOY_TEMPLATE_DETAILED_RESOURCE.fields
            labels = res_fields.DEPLOY_TEMPLATE_DETAILED_RESOURCE.labels

        elif parsed_args.fields:
            params['detail'] = False
            fields = itertools.chain.from_iterable(parsed_args.fields)
            resource = res_fields.Resource(list(fields))
            columns = resource.fields
            labels = resource.labels
            params['fields'] = columns

        self.log.debug("params(%s)", params)
        data = client.deploy_template.list(**params)

        data = oscutils.sort_items(data, parsed_args.sort)

        return (labels,
                (oscutils.get_item_properties(s, columns) for s in data))
