#    Copyright (c) 2015 Intel Corporation
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

import testtools

from ironicclient.v1 import resource_fields


class ResourceTest(testtools.TestCase):
    def setUp(self):
        super(ResourceTest, self).setUp()
        self._saved_ids = resource_fields.Resource.FIELDS
        resource_fields.Resource.FIELDS = {
            'item1': 'ITEM1',
            '2nd_item': 'A second item',
            'item_3': 'Third item',
        }

    def tearDown(self):
        super(ResourceTest, self).tearDown()
        resource_fields.Resource.FIELDS = self._saved_ids

    def test_fields_single_value(self):
        # Make sure single value is what we expect
        foo = resource_fields.Resource(['item1'])
        self.assertEqual(('item1',), foo.fields)
        self.assertEqual(('ITEM1',), foo.labels)
        self.assertEqual(('item1',), foo.sort_fields)
        self.assertEqual(('ITEM1',), foo.sort_labels)

    def test_fields_multiple_value_order(self):
        # Make sure order is maintained
        foo = resource_fields.Resource(['2nd_item', 'item1'])
        self.assertEqual(('2nd_item', 'item1'), foo.fields)
        self.assertEqual(('A second item', 'ITEM1'), foo.labels)
        self.assertEqual(('2nd_item', 'item1'), foo.sort_fields)
        self.assertEqual(('A second item', 'ITEM1'), foo.sort_labels)

    def test_sort_excluded(self):
        # Test excluding of fields for sort purposes
        foo = resource_fields.Resource(['item_3', 'item1', '2nd_item'],
                                       sort_excluded=['item1'])
        self.assertEqual(('item_3', '2nd_item'), foo.sort_fields)
        self.assertEqual(('Third item', 'A second item'), foo.sort_labels)

    def test_sort_excluded_unknown(self):
        # Test sort_excluded value not in the field_ids
        self.assertRaises(
            ValueError,
            resource_fields.Resource,
            ['item_3', 'item1', '2nd_item'],
            sort_excluded=['item1', 'foo'])

    def test_unknown_field_id(self):
        self.assertRaises(
            KeyError,
            resource_fields.Resource,
            ['item1', 'unknown_id'])
