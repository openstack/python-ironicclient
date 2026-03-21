#
#   Copyright 2015 Red Hat, Inc.
#
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

"""OpenStackClient plugin for Bare Metal service."""

from __future__ import annotations

import argparse
import logging

from osc_lib import clientmanager
from osc_lib import utils

from ironicclient.common import http
from ironicclient.v1 import client as v1_client

LOG: logging.Logger = logging.getLogger(__name__)

CLIENT_CLASS: str = 'ironicclient.v1.client.Client'
API_VERSION_OPTION: str = 'os_baremetal_api_version'
API_NAME: str = 'baremetal'
# NOTE(TheJulia) Latest known version tracking has been moved
# to the ironicclient/common/http.py file as the OSC commitment
# is latest known, and we should only store it in one location.
LAST_KNOWN_API_VERSION: int = http.LAST_KNOWN_API_VERSION
LATEST_VERSION: str = http.LATEST_VERSION


API_VERSIONS: dict[str, str] = {
    '1.%d' % i: CLIENT_CLASS
    for i in range(1, LAST_KNOWN_API_VERSION + 1)
}
API_VERSIONS['1'] = CLIENT_CLASS
# NOTE(dtantsur): flag to indicate that the requested version was "latest".
# Due to how OSC works we cannot just add "latest" to the list of supported
# versions - it breaks the major version detection.
OS_BAREMETAL_API_LATEST: bool = True


def make_client(
    instance: clientmanager.ClientManager,
) -> v1_client.Client:
    """Returns a baremetal service client."""
    requested_api_version: str = instance._api_version[API_NAME]

    baremetal_client_class: type[v1_client.Client] = (
        utils.get_client_class(
            API_NAME,
            requested_api_version,
            API_VERSIONS))
    LOG.debug('Instantiating baremetal client: %s', baremetal_client_class)
    LOG.debug('Baremetal API version: %s',
              requested_api_version if not OS_BAREMETAL_API_LATEST
              else "latest")

    if requested_api_version == '1':
        # NOTE(dtantsur): '1' means 'the latest v1 API version'. Since we don't
        # have other major versions, it's identical to 'latest'.
        requested_api_version = LATEST_VERSION
        allow_api_version_downgrade: bool = True
    else:
        allow_api_version_downgrade = OS_BAREMETAL_API_LATEST

    result: v1_client.Client = baremetal_client_class(
        os_ironic_api_version=requested_api_version,
        # NOTE(dtantsur): enable re-negotiation of the latest version, if CLI
        # latest is too high for the server we're talking to.
        allow_api_version_downgrade=allow_api_version_downgrade,
        session=instance.session,
        # TODO(karan): _region_name is a private attr on ClientManager;
        # osc-lib should expose this publicly. See also:
        # https://bugs.launchpad.net/python-ironicclient/+bug/2146739
        region_name=instance._region_name,  # type: ignore[attr-defined]
        # NOTE(vdrok): This will be set as endpoint_override, and the Client
        # class will be able to do the version stripping if needed
        endpoint_override=instance.get_endpoint_for_service_type(
            API_NAME, interface=instance.interface,
            # TODO(karan): same _region_name private attr access as above
            region_name=instance._region_name  # type: ignore[attr-defined]
        )
    )
    return result


def build_option_parser(
    parser: argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    """Hook to add global options."""
    parser.add_argument(
        '--os-baremetal-api-version',
        metavar='<baremetal-api-version>',
        default=_get_environment_version("latest"),
        choices=sorted(
            API_VERSIONS,
            key=lambda k: [int(x) for x in k.split('.')]) + ['latest'],
        action=ReplaceLatestVersion,
        help='Bare metal API version, default="latest" (the maximum version '
             'supported by both the client and the server). '
             '(Env: OS_BAREMETAL_API_VERSION)',
    )
    return parser


def _get_environment_version(default: str) -> str:
    global OS_BAREMETAL_API_LATEST
    env_value: str | None = utils.env('OS_BAREMETAL_API_VERSION')
    if not env_value:
        env_value = default
    if env_value == 'latest':
        env_value = LATEST_VERSION
    else:
        OS_BAREMETAL_API_LATEST = False
    return env_value


class ReplaceLatestVersion(argparse.Action):
    """Replaces `latest` keyword by last known version.

    OSC cannot accept the literal "latest" as a supported API version as it
    breaks the major version detection (OSC tries to load configuration options
    from setuptools entrypoint openstack.baremetal.vlatest). This action
    replaces "latest" with the latest known version, and sets the global
    OS_BAREMETAL_API_LATEST flag appropriately.
    """
    # base Action.__call__ accepts str | Sequence[Any] | None; narrowed here
    def __call__(  # type: ignore[override]
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str,
        option_string: str | None = None,
    ) -> None:
        global OS_BAREMETAL_API_LATEST
        if values == 'latest':
            values = LATEST_VERSION
            # The default value of "True" may have been overridden due to
            # non-empty OS_BAREMETAL_API_VERSION env variable. If a user
            # explicitly requests "latest", we need to correct it.
            OS_BAREMETAL_API_LATEST = True
        else:
            OS_BAREMETAL_API_LATEST = False
        setattr(namespace, self.dest, values)
