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

import logging

from ironicclient.common import filecache
from ironicclient.common import http
from ironicclient.common.http import DEFAULT_VER
from ironicclient.v1 import allocation
from ironicclient.v1 import chassis
from ironicclient.v1 import conductor
from ironicclient.v1 import deploy_template
from ironicclient.v1 import driver
from ironicclient.v1 import events
from ironicclient.v1 import inspection_rule
from ironicclient.v1 import node
from ironicclient.v1 import port
from ironicclient.v1 import portgroup
from ironicclient.v1 import runbook
from ironicclient.v1 import shard
from ironicclient.v1 import volume_connector
from ironicclient.v1 import volume_target

LOG = logging.getLogger(__name__)


class Client(object):
    """Client for the Ironic v1 API.

    :param string endpoint_override: A user-supplied endpoint URL for the
                                     ironic service.
    :param session: A keystoneauth Session object (must be provided as
        a keyword argument).
    """

    def __init__(self, endpoint_override=None, *args, **kwargs):
        """Initialize a new client for the Ironic v1 API."""
        if not args and not kwargs.get('session'):
            raise TypeError("A session is required for creating a client, "
                            "use ironicclient.client.get_client to create "
                            "it automatically")

        allow_downgrade = kwargs.pop('allow_api_version_downgrade', False)
        if kwargs.get('os_ironic_api_version'):
            # TODO(TheJulia): We should sanity check os_ironic_api_version
            # against our maximum supported version, so the client fails
            # immediately upon an unsupported version being provided.
            # This logic should also likely live in common/http.py
            if allow_downgrade:
                if kwargs['os_ironic_api_version'] == 'latest':
                    raise ValueError(
                        "Invalid configuration defined. "
                        "The os_ironic_api_version can not be set "
                        "to 'latest' while allow_api_version_downgrade "
                        "is set.")
                # NOTE(dtantsur): here we allow the HTTP client to negotiate a
                # lower version if the requested is too high
                kwargs['api_version_select_state'] = "default"
            else:
                kwargs['api_version_select_state'] = "user"
        else:
            if endpoint_override:
                # If the user didn't specify a version, use a cached version if
                # one has been stored
                host, netport = http.get_server(endpoint_override)
                saved_version = filecache.retrieve_data(host=host,
                                                        port=netport)
                if saved_version:
                    kwargs['api_version_select_state'] = "cached"
                    kwargs['os_ironic_api_version'] = saved_version
                else:
                    kwargs['api_version_select_state'] = "default"
                    kwargs['os_ironic_api_version'] = DEFAULT_VER
            else:
                LOG.debug('Cannot use cached API version since endpoint '
                          'override is not provided. Will negotiate again.')
                kwargs['api_version_select_state'] = "default"
                kwargs['os_ironic_api_version'] = DEFAULT_VER

        if endpoint_override:
            kwargs['endpoint_override'] = endpoint_override
        self.http_client = http._construct_http_client(*args, **kwargs)

        self.chassis = chassis.ChassisManager(self.http_client)
        self.node = node.NodeManager(self.http_client)
        self.port = port.PortManager(self.http_client)
        self.volume_connector = volume_connector.VolumeConnectorManager(
            self.http_client)
        self.volume_target = volume_target.VolumeTargetManager(
            self.http_client)
        self.driver = driver.DriverManager(self.http_client)
        self.runbook = runbook.RunbookManager(self.http_client)
        self.portgroup = portgroup.PortgroupManager(self.http_client)
        self.conductor = conductor.ConductorManager(self.http_client)
        self.events = events.EventManager(self.http_client)
        self.allocation = allocation.AllocationManager(self.http_client)
        self.deploy_template = deploy_template.DeployTemplateManager(
            self.http_client)
        self.shard = shard.ShardManager(self.http_client)
        self.inspection_rule = inspection_rule.InspectionRuleManager(
            self.http_client)

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
        """Returns True if microversion negotiation has occurred."""
        return self.http_client.api_version_select_state == 'negotiated'

    def negotiate_api_version(self):
        """Triggers negotiation with the remote API endpoint.

        :returns: the negotiated API version.
        """
        return self.http_client.negotiate_version(
            self.http_client.session, None)
