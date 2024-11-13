# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from ironicclient.common import base


class Shard(base.Resource):
    def __repr__(self):
        return "<Shard %s>" % self._info


class ShardManager(base.Manager):
    resource_class = Shard
    _resource_name = 'shards'

    def list(self, os_ironic_api_version=None, global_request_id=None):
        """Retrieve a list of shards.

        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.

        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.

        :returns: A list of conductors.

        """
        header_values = {"os_ironic_api_version": os_ironic_api_version,
                         "global_request_id": global_request_id}
        return self._list(self._path(None), "shards", **header_values)
