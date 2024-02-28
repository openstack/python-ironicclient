# Copyright 2013 OpenStack Foundation
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

from unittest import mock

from oslotest import base as test_base

from ironicclient.common.apiclient import base


class HumanResource(base.Resource):
    HUMAN_ID = True


class HumanResourceManager(base.ManagerWithFind):
    resource_class = HumanResource

    def list(self):
        return self._list("/human_resources", "human_resources")

    def get(self, human_resource):
        return self._get(
            "/human_resources/%s" % base.getid(human_resource),
            "human_resource")

    def update(self, human_resource, name):
        body = {
            "human_resource": {
                "name": name,
            },
        }
        return self._put(
            "/human_resources/%s" % base.getid(human_resource),
            body,
            "human_resource")


class CrudResource(base.Resource):
    pass


class CrudResourceManager(base.CrudManager):
    """Manager class for manipulating Identity crud_resources."""
    resource_class = CrudResource
    collection_key = 'crud_resources'
    key = 'crud_resource'

    def get(self, crud_resource):
        return super(CrudResourceManager, self).get(
            crud_resource_id=base.getid(crud_resource))


class ResourceTest(test_base.BaseTestCase):
    def test_resource_repr(self):
        r = base.Resource(None, dict(foo="bar", baz="spam"))
        self.assertEqual("<Resource baz=spam, foo=bar>", repr(r))

    def test_getid(self):
        class TmpObject(base.Resource):
            id = "4"
        self.assertEqual("4", base.getid(TmpObject(None, {})))

    def test_human_id(self):
        r = base.Resource(None, {"name": "1"})
        self.assertIsNone(r.human_id)
        r = HumanResource(None, {"name": "1"})
        self.assertEqual("1", r.human_id)
        r = HumanResource(None, {"name": None})
        self.assertIsNone(r.human_id)

    def test_two_resources_with_same_id_are_not_equal(self):
        # Two resources with same ID: never equal if their info is not equal
        r1 = base.Resource(None, {'id': 1, 'name': 'hi'})
        r2 = base.Resource(None, {'id': 1, 'name': 'hello'})
        self.assertNotEqual(r1, r2)

    def test_two_resources_with_same_id_and_info_are_equal(self):
        # Two resources with same ID: equal if their info is equal
        r1 = base.Resource(None, {'id': 1, 'name': 'hello'})
        r2 = base.Resource(None, {'id': 1, 'name': 'hello'})
        self.assertEqual(r1, r2)

    def test_two_resources_with_diff_type_are_not_equal(self):
        # Two resources of different types: never equal
        r1 = base.Resource(None, {'id': 1})
        r2 = HumanResource(None, {'id': 1})
        self.assertNotEqual(r1, r2)

    def test_two_resources_with_no_id_are_equal(self):
        # Two resources with no ID: equal if their info is equal
        r1 = base.Resource(None, {'name': 'joe', 'age': 12})
        r2 = base.Resource(None, {'name': 'joe', 'age': 12})
        self.assertEqual(r1, r2)


class BaseManagerTestCase(test_base.BaseTestCase):

    def setUp(self):
        super(BaseManagerTestCase, self).setUp()

        self.response = mock.MagicMock()
        self.http_client = mock.MagicMock()
        self.http_client.get.return_value = self.response
        self.http_client.post.return_value = self.response

        self.manager = base.BaseManager(self.http_client)
        self.manager.resource_class = HumanResource

    def test_list(self):
        self.response.json.return_value = {'human_resources': [{'id': 42}]}
        expected = [HumanResource(self.manager, {'id': 42}, loaded=True)]
        result = self.manager._list("/human_resources", "human_resources")
        self.assertEqual(expected, result)

    def test_list_no_response_key(self):
        self.response.json.return_value = [{'id': 42}]
        expected = [HumanResource(self.manager, {'id': 42}, loaded=True)]
        result = self.manager._list("/human_resources")
        self.assertEqual(expected, result)

    def test_list_get(self):
        self.manager._list("/human_resources", "human_resources")
        self.manager.client.get.assert_called_with("/human_resources")

    def test_list_post(self):
        self.manager._list("/human_resources", "human_resources",
                           json={'id': 42})
        self.manager.client.post.assert_called_with("/human_resources",
                                                    json={'id': 42})

    def test_get(self):
        self.response.json.return_value = {'human_resources': {'id': 42}}
        expected = HumanResource(self.manager, {'id': 42}, loaded=True)
        result = self.manager._get("/human_resources/42", "human_resources")
        self.manager.client.get.assert_called_with("/human_resources/42")
        self.assertEqual(expected, result)

    def test_get_no_response_key(self):
        self.response.json.return_value = {'id': 42}
        expected = HumanResource(self.manager, {'id': 42}, loaded=True)
        result = self.manager._get("/human_resources/42")
        self.manager.client.get.assert_called_with("/human_resources/42")
        self.assertEqual(expected, result)

    def test_post(self):
        self.response.json.return_value = {'human_resources': {'id': 42}}
        expected = HumanResource(self.manager, {'id': 42}, loaded=True)
        result = self.manager._post("/human_resources",
                                    response_key="human_resources",
                                    json={'id': 42})
        self.manager.client.post.assert_called_with("/human_resources",
                                                    json={'id': 42})
        self.assertEqual(expected, result)

    def test_post_return_raw(self):
        self.response.json.return_value = {'human_resources': {'id': 42}}
        result = self.manager._post("/human_resources",
                                    response_key="human_resources",
                                    json={'id': 42}, return_raw=True)
        self.manager.client.post.assert_called_with("/human_resources",
                                                    json={'id': 42})
        self.assertEqual({'id': 42}, result)

    def test_post_no_response_key(self):
        self.response.json.return_value = {'id': 42}
        expected = HumanResource(self.manager, {'id': 42}, loaded=True)
        result = self.manager._post("/human_resources", json={'id': 42})
        self.manager.client.post.assert_called_with("/human_resources",
                                                    json={'id': 42})
        self.assertEqual(expected, result)
