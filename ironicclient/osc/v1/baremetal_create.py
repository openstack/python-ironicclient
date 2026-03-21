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

from __future__ import annotations

import argparse
import logging

from ironicclient.common.i18n import _
from ironicclient.osc import command
from ironicclient.v1 import create_resources


class CreateBaremetal(command.Command):
    """Create resources from files"""

    log: logging.Logger = logging.getLogger(
        __name__ + ".CreateBaremetal")

    def get_parser(  # type: ignore[override]
        self, prog_name: str,
    ) -> argparse.ArgumentParser:
        parser: argparse.ArgumentParser = super().get_parser(prog_name)

        parser.add_argument(
            "resource_files", metavar="<file>", nargs="+",
            help=_("File (.yaml or .json) containing descriptions of the "
                   "resources to create. Can be specified multiple times."))
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        create_resources.create_resources(
            self.app.client_manager.baremetal,
            parsed_args.resource_files)
