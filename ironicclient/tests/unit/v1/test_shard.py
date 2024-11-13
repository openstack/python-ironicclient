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

import unittest
from unittest.mock import patch

from ironicclient.v1.shard import ShardManager


class TestShardManager(unittest.TestCase):

    @patch('ironicclient.common.base.Manager._list')
    def test_list_shards(self, mock_list):
        # Mock response for the list of shards
        mock_response = [
            {'name': 'example_shard1', 'count': 47},
            {'name': 'example_shard2', 'count': 46},
            {'name': None, 'count': 3}  # Nodes with no shard assigned
        ]

        # Configure mock to return the mocked response
        mock_list.return_value = mock_response

        # Initialize the ShardManager
        shard_manager = ShardManager(api=None)  # `api=None` for simplicity

        # Perform the test call
        result = shard_manager.list(os_ironic_api_version="1.82")

        # Assertions
        mock_list.assert_called_once_with(
            shard_manager._path(None),
            "shards",
            os_ironic_api_version="1.82",
            global_request_id=None
        )
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['name'], 'example_shard1')
        self.assertEqual(result[0]['count'], 47)
        self.assertEqual(result[1]['name'], 'example_shard2')
        self.assertEqual(result[1]['count'], 46)
        self.assertIsNone(result[2]['name'])
        self.assertEqual(result[2]['count'], 3)

    @patch('ironicclient.common.base.Manager._list')
    def test_list_shards_empty(self, mock_list):
        # Test when the shards list is empty
        mock_list.return_value = []

        # Initialize the ShardManager
        shard_manager = ShardManager(api=None)

        # Perform the test call
        result = shard_manager.list(os_ironic_api_version="1.82")

        # Assertions
        mock_list.assert_called_once_with(
            shard_manager._path(None),
            "shards",
            os_ironic_api_version="1.82",
            global_request_id=None
        )
        self.assertEqual(result, [])

    @patch('ironicclient.common.base.Manager._list')
    def test_list_shards_with_global_request_id(self, mock_list):
        # Test with global request ID
        mock_response = [
            {'name': 'example_shard1', 'count': 47},
            {'name': 'example_shard2', 'count': 46}
        ]
        mock_list.return_value = mock_response

        # Initialize the ShardManager
        shard_manager = ShardManager(api=None)

        # Perform the test call with global_request_id
        result = shard_manager.list(
            os_ironic_api_version="1.82",
            global_request_id="req-12345"
        )

        # Assertions
        mock_list.assert_called_once_with(
            shard_manager._path(None),
            "shards",
            os_ironic_api_version="1.82",
            global_request_id="req-12345"
        )
        self.assertEqual(result, mock_response)

    @patch('ironicclient.common.base.Manager._list')
    def test_list_shards_api_version_mismatch(self, mock_list):
        # Simulate a 404 error for an unsupported API version
        mock_list.side_effect = ValueError(
            "404 Not Found: The requested version is not supported"
        )

        # Initialize the ShardManager
        shard_manager = ShardManager(api=None)

        # Perform the test call and assert exception is raised
        with self.assertRaises(ValueError) as context:
            shard_manager.list(os_ironic_api_version="1.50")

        self.assertIn("404 Not Found", str(context.exception))
