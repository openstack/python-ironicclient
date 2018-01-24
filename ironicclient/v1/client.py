# Copyright 2012 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from ironicclient.common import filecache
from ironicclient.common import http
from ironicclient.common.http import DEFAULT_VER
from ironicclient.common.i18n import _
from ironicclient import exc
from ironicclient.v1 import chassis
from ironicclient.v1 import driver
from ironicclient.v1 import node
from ironicclient.v1 import port
from ironicclient.v1 import portgroup
from ironicclient.v1 import volume_connector
from ironicclient.v1 import volume_target


class Client(object):
    """Client for the Ironic v1 API.

    :param string endpoint: A user-supplied endpoint URL for the ironic
                            service.
    :param function token: Provides token for authentication.
    :param integer timeout: Allows customization of the timeout for client
                            http requests. (optional)
    """

    def __init__(self, endpoint=None, *args, **kwargs):
        """Initialize a new client for the Ironic v1 API."""
        allow_downgrade = kwargs.pop('allow_api_version_downgrade', False)
        if kwargs.get('os_ironic_api_version'):
            # TODO(TheJulia): We should sanity check os_ironic_api_version
            # against our maximum suported version, so the client fails
            # immediately upon an unsupported version being provided.
            # This logic should also likely live in common/http.py
            if allow_downgrade:
                if kwargs['os_ironic_api_version'] == 'latest':
                    raise ValueError(
                        "Invalid configuration defined. "
                        "The os_ironic_api_versioncan not be set "
                        "to 'latest' while allow_api_version_downgrade "
                        "is set.")
                # NOTE(dtantsur): here we allow the HTTP client to negotiate a
                # lower version if the requested is too high
                kwargs['api_version_select_state'] = "default"
            else:
                kwargs['api_version_select_state'] = "user"
        else:
            if not endpoint:
                raise exc.EndpointException(
                    _("Must provide 'endpoint' if os_ironic_api_version "
                      "isn't specified"))

            # If the user didn't specify a version, use a cached version if
            # one has been stored
            host, netport = http.get_server(endpoint)
            saved_version = filecache.retrieve_data(host=host, port=netport)
            if saved_version:
                kwargs['api_version_select_state'] = "cached"
                kwargs['os_ironic_api_version'] = saved_version
            else:
                kwargs['api_version_select_state'] = "default"
                kwargs['os_ironic_api_version'] = DEFAULT_VER

        self.http_client = http._construct_http_client(
            endpoint, *args, **kwargs)

        self.chassis = chassis.ChassisManager(self.http_client)
        self.node = node.NodeManager(self.http_client)
        self.port = port.PortManager(self.http_client)
        self.volume_connector = volume_connector.VolumeConnectorManager(
            self.http_client)
        self.volume_target = volume_target.VolumeTargetManager(
            self.http_client)
        self.driver = driver.DriverManager(self.http_client)
        self.portgroup = portgroup.PortgroupManager(self.http_client)

    @property
    def current_api_version(self):
        """Return the current API version in use.

        This returns the version of the REST API that the API client
        is presently set to request. This value may change as a result
        of API version negotiation.
        """
        return self.http_client.os_ironic_api_version

    @property
    def is_api_version_negotiated(self):
        """Returns True if microversion negotiation has occured."""
        return self.http_client.api_version_select_state == 'negotiated'

    def negotiate_api_version(self):
        """Triggers negotiation with the remote API endpoint.

        :returns: the negotiated API version.
        """
        return self.http_client.negotiate_version(
            self.http_client.session, None)
