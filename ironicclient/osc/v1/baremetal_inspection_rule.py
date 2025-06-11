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


class CreateBaremetalInspectionRule(command.ShowOne):
    """Create a new rule"""

    log = logging.getLogger(__name__ + ".CreateBaremetalInspectionRule")

    def get_parser(self, prog_name):
        parser = super(CreateBaremetalInspectionRule, self).get_parser(
            prog_name)

        parser.add_argument(
            '--uuid',
            dest='uuid',
            metavar='<uuid>',
            help=_('UUID of the rule.'))
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('A brief explanation about the rule.')
        )
        parser.add_argument(
            '--priority',
            metavar='<priority>',
            help=_("Specifies the rule's precedence level during execution.")
        )
        parser.add_argument(
            '--sensitive',
            metavar='<sensitive>',
            help=_('Indicates whether the rule contains sensitive '
                   'information.')
        )
        parser.add_argument(
            '--phase',
            metavar='<phase>',
            help=_('Specifies the processing phase when the rule should run.')
        )
        parser.add_argument(
            '--conditions',
            metavar="<conditions>",
            help=_('Conditions under which the rule should be triggered.')
        )
        parser.add_argument(
            '--actions',
            metavar="<actions>",
            required=True,
            help=_('Actions to be executed when the rule conditions are met.')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        baremetal_client = self.app.client_manager.baremetal

        actions = utils.handle_json_arg(parsed_args.actions, 'rule actions')
        conditions = utils.handle_json_arg(parsed_args.conditions,
                                           'rule conditions')

        field_list = ['uuid', 'description', 'priority', 'sensitive', 'phase']
        fields = dict((k, v) for (k, v) in vars(parsed_args).items()
                      if k in field_list and v is not None)
        rule = baremetal_client.inspection_rule.create(actions=actions,
                                                       conditions=conditions,
                                                       **fields)

        data = dict([(f, getattr(rule, f, '')) for f in
                     res_fields.INSPECTION_RULE_DETAILED_RESOURCE.fields])

        return self.dict2columns(data)


class ShowBaremetalInspectionRule(command.ShowOne):
    """Show baremetal rule details."""

    log = logging.getLogger(__name__ + ".ShowBaremetalInspectionRule")

    def get_parser(self, prog_name):
        parser = super(ShowBaremetalInspectionRule, self).get_parser(
            prog_name)
        parser.add_argument(
            "rule",
            metavar="<rule>",
            help=_("UUID of the inspection rule.")
        )
        parser.add_argument(
            '--fields',
            nargs='+',
            dest='fields',
            metavar='<field>',
            action='append',
            choices=res_fields.INSPECTION_RULE_DETAILED_RESOURCE.fields,
            default=[],
            help=_("One or more rule fields. Only these fields "
                   "will be fetched from the server.")
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal
        fields = list(itertools.chain.from_iterable(parsed_args.fields))
        fields = fields if fields else None

        rule = baremetal_client.inspection_rule.get(
            parsed_args.rule, fields=fields)._info

        rule.pop("links", None)
        return zip(*sorted(rule.items()))


class SetBaremetalInspectionRule(command.Command):
    """Set baremetal rule properties."""

    log = logging.getLogger(__name__ + ".SetBaremetalInspectionRule")

    def get_parser(self, prog_name):
        parser = super(SetBaremetalInspectionRule, self).get_parser(prog_name)

        parser.add_argument(
            'rule',
            metavar='<rule>',
            help=_("UUID of the inspection rule")
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Set a brief explanation about the rule.')
        )
        parser.add_argument(
            '--priority',
            metavar='<priority>',
            help=_("Specifies the rule's precedence level during execution.")
        )
        parser.add_argument(
            '--phase',
            metavar='<phase>',
            help=_('Specifies the processing phase when the rule should run.')
        )
        parser.add_argument(
            '--conditions',
            metavar="<conditions>",
            help=_('Conditions under which the rule should be triggered.')
        )
        parser.add_argument(
            '--actions',
            metavar="<actions>",
            help=_('Actions to be executed when the rule conditions are met.')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        properties = []
        if parsed_args.description:
            description = ["description=%s" % parsed_args.description]
            properties.extend(utils.args_array_to_patch('add', description))
        if parsed_args.priority:
            priority = ["priority=%s" % parsed_args.priority]
            properties.extend(utils.args_array_to_patch('add', priority))
        if parsed_args.phase:
            phase = ["phase=%s" % parsed_args.phase]
            properties.extend(utils.args_array_to_patch('add', phase))
        if parsed_args.actions:
            actions = utils.handle_json_arg(parsed_args.actions,
                                            'rule actions')
            actions = ["actions=%s" % json.dumps(actions)]
            properties.extend(utils.args_array_to_patch('add', actions))
        if parsed_args.conditions:
            conditions = utils.handle_json_arg(parsed_args.conditions,
                                               'rule conditions')
            conditions = ["conditions=%s" % json.dumps(conditions)]
            properties.extend(utils.args_array_to_patch('add', conditions))

        if properties:
            baremetal_client.inspection_rule.update(parsed_args.rule,
                                                    properties)
        else:
            self.log.warning("Please specify what to set.")


class UnsetBaremetalInspectionRule(command.Command):
    """Unset baremetal rule properties."""
    log = logging.getLogger(__name__ + ".UnsetBaremetalInspectionRule")

    def get_parser(self, prog_name):
        parser = super(UnsetBaremetalInspectionRule, self).get_parser(
            prog_name)

        parser.add_argument(
            'rule',
            metavar='<rule>',
            help=_("UUID of the inspection rule")
        )
        parser.add_argument(
            '--description',
            dest='description',
            action='store_true',
            help=_('Unset a brief explanation about the rule.')
        )
        parser.add_argument(
            '--priority',
            dest='priority',
            action='store_true',
            help=_("Specifies the rule's precedence level during execution.")
        )
        parser.add_argument(
            '--phase',
            dest='phase',
            action='store_true',
            help=_('Specifies the processing phase when the rule should run.')
        )
        parser.add_argument(
            '--condition',
            metavar="<key>",
            action='append',
            help=_('Condition to unset on this baremetal inspection rule '
                   '(repeat option to unset multiple conditions).')
        )
        parser.add_argument(
            '--action',
            metavar="<key>",
            action='append',
            help=_('Action to unset on this baremetal inspection rule '
                   '(repeat option to unset multiple actions).')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        properties = []
        field_list = ['description', 'priority', 'phase']
        for field in field_list:
            if getattr(parsed_args, field):
                properties.extend(utils.args_array_to_patch('remove', [field]))

        if parsed_args.action:
            properties.extend(utils.args_array_to_patch('remove',
                              ['action/' + x for x in parsed_args.action]))
        if parsed_args.condition:
            properties.extend(
                utils.args_array_to_patch(
                    'remove',
                    ['condition/' + x for x in parsed_args.condition]))

        if properties:
            baremetal_client.inspection_rule.update(parsed_args.rule,
                                                    properties)
        else:
            self.log.warning("Please specify what to unset.")


class DeleteBaremetalInspectionRule(command.Command):
    """Delete rule(s)."""

    log = logging.getLogger(__name__ + ".DeleteBaremetalInspectionRule")

    def get_parser(self, prog_name):
        parser = super(DeleteBaremetalInspectionRule, self).get_parser(
            prog_name)
        parser.add_argument(
            "rules",
            metavar="<rule>",
            nargs="+",
            help=_("UUID(s) of the rule(s) to delete."),
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        baremetal_client = self.app.client_manager.baremetal

        failures = []
        if parsed_args.rules == 'all':
            try:
                baremetal_client.inspection_rule.delete()
                print(_('Deleted all rules.'))
            except exc.ClientException as e:
                raise exc.ClientException(
                    _("Failed to delete all rules: %s") % e)
        else:
            for rule in parsed_args.rules:
                try:
                    baremetal_client.inspection_rule.delete(rule)
                    print(_('Deleted rule %s') % rule)
                except exc.ClientException as e:
                    failures.append(_("Failed to delete rule "
                                      "%(rule)s: %(error)s")
                                    % {'rule': rule, 'error': e})

        if failures:
            raise exc.ClientException("\n".join(failures))


class ListBaremetalInspectionRule(command.Lister):
    """List baremetal rules."""

    log = logging.getLogger(__name__ + ".ListBaremetalInspectionRule")

    def get_parser(self, prog_name):
        parser = super(ListBaremetalInspectionRule, self).get_parser(prog_name)
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            type=int,
            help=_('Maximum number of rules to return per request, '
                   '0 for no limit. Default is the maximum number used '
                   'by the Baremetal API Service.')
        )
        parser.add_argument(
            '--marker',
            metavar='<rule>',
            help=_('InspectionRule UUID (for example, of the last rule '
                   'in the list from a previous request). Returns '
                   'the list of rules after this UUID.')
        )
        parser.add_argument(
            '--sort',
            metavar="<key>[:<direction>]",
            help=_('Sort output by specified rule fields and '
                   'directions (asc or desc) (default: asc). Multiple fields '
                   'and directions can be specified, separated by comma.')
        )
        display_group = parser.add_mutually_exclusive_group()
        display_group.add_argument(
            '--long',
            dest='detail',
            action='store_true',
            default=False,
            help=_("Show detailed information about rules.")
        )
        display_group.add_argument(
            '--fields',
            nargs='+',
            dest='fields',
            metavar='<field>',
            action='append',
            default=[],
            choices=res_fields.INSPECTION_RULE_DETAILED_RESOURCE.fields,
            help=_("One or more rule fields. Only these fields "
                   "will be fetched from the server. Can not be used when "
                   "'--long' is specified.")
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.baremetal

        columns = res_fields.INSPECTION_RULE_RESOURCE.fields
        labels = res_fields.INSPECTION_RULE_RESOURCE.labels

        params = {}
        if parsed_args.limit is not None and parsed_args.limit < 0:
            raise exc.CommandError(
                _('Expected non-negative --limit, got %s') %
                parsed_args.limit)
        params['limit'] = parsed_args.limit
        params['marker'] = parsed_args.marker

        if parsed_args.detail:
            params['detail'] = parsed_args.detail
            columns = res_fields.INSPECTION_RULE_DETAILED_RESOURCE.fields
            labels = res_fields.INSPECTION_RULE_DETAILED_RESOURCE.labels

        elif parsed_args.fields:
            params['detail'] = False
            fields = itertools.chain.from_iterable(parsed_args.fields)
            resource = res_fields.Resource(list(fields))
            columns = resource.fields
            labels = resource.labels
            params['fields'] = columns

        self.log.debug("params(%s)", params)
        data = client.inspection_rule.list(**params)

        data = oscutils.sort_items(data, parsed_args.sort)

        return (labels,
                (oscutils.get_item_properties(s, columns) for s in data))
