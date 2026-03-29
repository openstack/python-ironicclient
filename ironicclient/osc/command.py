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

"""Typed base command classes for ironicclient OSC commands.

These subclass osc-lib's command classes and annotate ``app`` so that
``self.app.client_manager.baremetal`` is statically known to be
:class:`ironicclient.v1.client.Client`, removing the need for
``# type: ignore[attr-defined]`` throughout the command implementations.

See https://review.opendev.org/c/openstack/python-openstackclient/+/970681
for the equivalent pattern in python-openstackclient.
"""

from __future__ import annotations

from typing import Any

from cliff import lister
from cliff import show
from osc_lib import clientmanager
from osc_lib.command import command
from osc_lib import shell


class _ClientManager(clientmanager.ClientManager):
    # NOTE(karan): baremetal is injected dynamically by the plugin
    # system (via setattr in osc-lib's get_plugin_modules). Typed as
    # Any because osc-lib's utility functions (e.g. get_item_properties)
    # have narrow type signatures that don't accept Resource objects.
    # Can be narrowed to v1.client.Client once those callers are
    # updated.
    baremetal: Any


class _App(shell.OpenStackShell):
    client_manager: _ClientManager


class Command(command.Command):
    app: _App


class Lister(Command, lister.Lister):
    pass


class ShowOne(Command, show.ShowOne):
    pass
