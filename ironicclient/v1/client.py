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
from ironicclient.v1 import chassis
from ironicclient.v1 import driver
from ironicclient.v1 import node
from ironicclient.v1 import port


class Client(object):
    """Client for the Ironic v1 API.

    :param string endpoint: A user-supplied endpoint URL for the ironic
                            service.
    :param function token: Provides token for authentication.
    :param integer timeout: Allows customization of the timeout for client
                            http requests. (optional)
    """

    def __init__(self, *args, **kwargs):
        """Initialize a new client for the Ironic v1 API."""
        if kwargs.get('os_ironic_api_version'):
            kwargs['api_version_select_state'] = "user"
        else:
            # If the user didn't specify a version, use a cached version if
            # one has been stored
            host, netport = http.get_server(args[0])
            saved_version = filecache.retrieve_data(host=host, port=netport)
            if saved_version:
                kwargs['api_version_select_state'] = "cached"
                kwargs['os_ironic_api_version'] = saved_version
            else:
                kwargs['api_version_select_state'] = "default"
                kwargs['os_ironic_api_version'] = DEFAULT_VER

        self.http_client = http._construct_http_client(*args, **kwargs)

        self.chassis = chassis.ChassisManager(self.http_client)
        self.node = node.NodeManager(self.http_client)
        self.port = port.PortManager(self.http_client)
        self.driver = driver.DriverManager(self.http_client)
