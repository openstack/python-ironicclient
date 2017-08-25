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

import argparse
import logging

from ironicclient.common import http
from osc_lib import utils

LOG = logging.getLogger(__name__)

API_VERSION_OPTION = 'os_baremetal_api_version'
API_NAME = 'baremetal'
LAST_KNOWN_API_VERSION = 34
LATEST_VERSION = "1.{}".format(LAST_KNOWN_API_VERSION)
API_VERSIONS = {
    '1.%d' % i: 'ironicclient.v1.client.Client'
    for i in range(1, LAST_KNOWN_API_VERSION + 1)
}
API_VERSIONS['1'] = API_VERSIONS[http.DEFAULT_VER]
OS_BAREMETAL_API_VERSION_SPECIFIED = False
MISSING_VERSION_WARNING = (
    "You are using the default API version of the OpenStack CLI baremetal "
    "(ironic) plugin. This is currently API version %s. In the future, "
    "the default will be the latest API version understood by both API "
    "and CLI. You can preserve the current behavior by passing the "
    "--os-baremetal-api-version argument with the desired version or using "
    "the OS_BAREMETAL_API_VERSION environment variable."
)


def make_client(instance):
    """Returns a baremetal service client."""
    if (not OS_BAREMETAL_API_VERSION_SPECIFIED and not
            utils.env('OS_BAREMETAL_API_VERSION')):
        LOG.warning(MISSING_VERSION_WARNING, http.DEFAULT_VER)

    baremetal_client_class = utils.get_client_class(
        API_NAME,
        instance._api_version[API_NAME],
        API_VERSIONS)
    LOG.debug('Instantiating baremetal client: %s', baremetal_client_class)
    LOG.debug('Baremetal API version: %s', http.DEFAULT_VER)

    client = baremetal_client_class(
        os_ironic_api_version=instance._api_version[API_NAME],
        session=instance.session,
        region_name=instance._region_name,
        # NOTE(vdrok): This will be set as endpoint_override, and the Client
        # class will be able to do the version stripping if needed
        endpoint=instance.get_endpoint_for_service_type(
            API_NAME, interface=instance.interface,
            region_name=instance._region_name
        )
    )
    return client


def build_option_parser(parser):
    """Hook to add global options."""
    parser.add_argument(
        '--os-baremetal-api-version',
        metavar='<baremetal-api-version>',
        default=_get_environment_version(http.DEFAULT_VER),
        choices=sorted(
            API_VERSIONS,
            key=lambda k: [int(x) for x in k.split('.')]) + ['latest'],
        action=ReplaceLatestVersion,
        help='Baremetal API version, default=' +
             http.DEFAULT_VER +
             ' (Env: OS_BAREMETAL_API_VERSION). '
             'Use "latest" for the latest known API version. '
             'The default value will change to "latest" in the Queens '
             'release.',
    )
    return parser


def _get_environment_version(default):
    env_value = utils.env('OS_BAREMETAL_API_VERSION')
    if not env_value:
        return default
    if env_value == 'latest':
        env_value = LATEST_VERSION
    return env_value


class ReplaceLatestVersion(argparse.Action):
    """Replaces `latest` keyword by last known version."""
    def __call__(self, parser, namespace, values, option_string=None):
        global OS_BAREMETAL_API_VERSION_SPECIFIED
        OS_BAREMETAL_API_VERSION_SPECIFIED = True
        if values == 'latest':
            values = LATEST_VERSION
        setattr(namespace, self.dest, values)
