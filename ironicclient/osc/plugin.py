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

import logging

from osc_lib import utils

LOG = logging.getLogger(__name__)

DEFAULT_BAREMETAL_API_VERSION = '1.6'
API_VERSION_OPTION = 'os_baremetal_api_version'
API_NAME = 'baremetal'
LAST_KNOWN_API_VERSION = 20
API_VERSIONS = {
    '1.%d' % i: 'ironicclient.v1.client.Client'
    for i in range(1, LAST_KNOWN_API_VERSION + 1)
}
API_VERSIONS['1'] = API_VERSIONS[DEFAULT_BAREMETAL_API_VERSION]


def make_client(instance):
    """Returns a baremetal service client."""
    baremetal_client_class = utils.get_client_class(
        API_NAME,
        instance._api_version[API_NAME],
        API_VERSIONS)
    LOG.debug('Instantiating baremetal client: %s', baremetal_client_class)

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
        default=utils.env(
            'OS_BAREMETAL_API_VERSION',
            default=DEFAULT_BAREMETAL_API_VERSION),
        help='Baremetal API version, default=' +
             DEFAULT_BAREMETAL_API_VERSION +
             ' (Env: OS_BAREMETAL_API_VERSION)')
    return parser
