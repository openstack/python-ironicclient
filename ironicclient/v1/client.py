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

from ironicclient.common import http
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
        self.http_client = http.HTTPClient(*args, **kwargs)
        self.chassis = chassis.ChassisManager(self.http_client)
        self.node = node.NodeManager(self.http_client)
        self.port = port.PortManager(self.http_client)
        self.driver = driver.DriverManager(self.http_client)
