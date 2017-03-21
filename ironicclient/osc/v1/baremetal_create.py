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

import argparse
import logging

from ironicclient.common.i18n import _
from ironicclient import exc
from ironicclient.osc.v1 import baremetal_node
from ironicclient.v1 import create_resources


class CreateBaremetal(baremetal_node.CreateBaremetalNode):
    """Create resources from files or Register a new node (DEPRECATED).

    Create resources from files (by only specifying the files) or register
    a new node by specifying one or more optional arguments (DEPRECATED,
    use 'openstack baremetal node create' instead).
    """

    log = logging.getLogger(__name__ + ".CreateBaremetal")

    def get_description(self):
        return _("Create resources from files (by only specifying the files) "
                 "or register a new node by specifying one or more optional "
                 "arguments (DEPRECATED, use 'openstack baremetal node "
                 "create' instead)")

    # TODO(vdrok): Remove support for new node creation after 11-July-2017
    # during the 'Queens' cycle.
    def get_parser(self, prog_name):
        parser = super(CreateBaremetal, self).get_parser(prog_name)
        # NOTE(vdrok): It is a workaround to allow --driver to be optional for
        # openstack create command while creation of nodes via this command is
        # not removed completely
        parser = argparse.ArgumentParser(parents=[parser],
                                         conflict_handler='resolve',
                                         description=self.__doc__)
        parser.add_argument(
            '--driver',
            metavar='<driver>',
            help=_('Specify this and any other optional arguments if you want '
                   'to create a node only. Note that this is deprecated; '
                   'please use "openstack baremetal node create" instead.'))
        parser.add_argument(
            "resource_files", metavar="<file>", default=[], nargs="*",
            help=_("File (.yaml or .json) containing descriptions of the "
                   "resources to create. Can be specified multiple times. If "
                   "you want to create resources, only specify the files. Do "
                   "not specify any of the optional arguments."))
        return parser

    def take_action(self, parsed_args):
        if parsed_args.driver:
            self.log.warning("This command is deprecated. Instead, use "
                             "'openstack baremetal node create'.")
            return super(CreateBaremetal, self).take_action(parsed_args)
        if not parsed_args.resource_files:
            raise exc.ValidationError(_(
                "If --driver is not supplied to openstack create command, "
                "it is considered that it will create ironic resources from "
                "one or more .json or .yaml files, but no files provided."))
        create_resources.create_resources(self.app.client_manager.baremetal,
                                          parsed_args.resource_files)
        # NOTE(vdrok): CreateBaremetal is still inherited from ShowOne class,
        # which requires the return value of the function to be of certain
        # type, leave this workaround until creation of nodes is removed and
        # then change it so that this inherits from command.Command
        return tuple(), tuple()
