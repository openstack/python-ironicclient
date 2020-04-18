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

import copy
from unittest import mock

from osc_lib.tests import utils as osctestutils

from ironicclient import exc
from ironicclient.osc.v1 import baremetal_allocation
from ironicclient.tests.unit.osc.v1 import fakes as baremetal_fakes


class TestBaremetalAllocation(baremetal_fakes.TestBaremetal):

    def setUp(self):
        super(TestBaremetalAllocation, self).setUp()

        self.baremetal_mock = self.app.client_manager.baremetal
        self.baremetal_mock.reset_mock()


class TestCreateBaremetalAllocation(TestBaremetalAllocation):

    def setUp(self):
        super(TestCreateBaremetalAllocation, self).setUp()

        self.baremetal_mock.allocation.create.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.ALLOCATION),
                loaded=True,
            ))

        self.baremetal_mock.allocation.wait.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.ALLOCATION),
                loaded=True,
            ))

        # Get the command object to test
        self.cmd = baremetal_allocation.CreateBaremetalAllocation(self.app,
                                                                  None)

    def test_baremetal_allocation_create(self):
        arglist = [
            '--resource-class', baremetal_fakes.baremetal_resource_class,
        ]

        verifylist = [
            ('resource_class', baremetal_fakes.baremetal_resource_class),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        args = {
            'resource_class': baremetal_fakes.baremetal_resource_class,
        }

        self.baremetal_mock.allocation.create.assert_called_once_with(**args)

    def test_baremetal_allocation_create_wait(self):
        arglist = [
            '--resource-class', baremetal_fakes.baremetal_resource_class,
            '--wait',
        ]

        verifylist = [
            ('resource_class', baremetal_fakes.baremetal_resource_class),
            ('wait_timeout', 0),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        args = {
            'resource_class': baremetal_fakes.baremetal_resource_class,
        }

        self.baremetal_mock.allocation.create.assert_called_once_with(**args)
        self.baremetal_mock.allocation.wait.assert_called_once_with(
            baremetal_fakes.ALLOCATION['uuid'], timeout=0)

    def test_baremetal_allocation_create_wait_with_timeout(self):
        arglist = [
            '--resource-class', baremetal_fakes.baremetal_resource_class,
            '--wait', '3600',
        ]

        verifylist = [
            ('resource_class', baremetal_fakes.baremetal_resource_class),
            ('wait_timeout', 3600),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        args = {
            'resource_class': baremetal_fakes.baremetal_resource_class,
        }

        self.baremetal_mock.allocation.create.assert_called_once_with(**args)
        self.baremetal_mock.allocation.wait.assert_called_once_with(
            baremetal_fakes.ALLOCATION['uuid'], timeout=3600)

    def test_baremetal_allocation_create_name_extras(self):
        arglist = [
            '--resource-class', baremetal_fakes.baremetal_resource_class,
            '--uuid', baremetal_fakes.baremetal_uuid,
            '--name', baremetal_fakes.baremetal_name,
            '--extra', 'key1=value1',
            '--extra', 'key2=value2'
        ]

        verifylist = [
            ('resource_class', baremetal_fakes.baremetal_resource_class),
            ('uuid', baremetal_fakes.baremetal_uuid),
            ('name', baremetal_fakes.baremetal_name),
            ('extra', ['key1=value1', 'key2=value2'])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        args = {
            'resource_class': baremetal_fakes.baremetal_resource_class,
            'uuid': baremetal_fakes.baremetal_uuid,
            'name': baremetal_fakes.baremetal_name,
            'extra': {'key1': 'value1', 'key2': 'value2'}
        }

        self.baremetal_mock.allocation.create.assert_called_once_with(**args)

    def test_baremetal_allocation_create_nodes_and_traits(self):
        arglist = [
            '--resource-class', baremetal_fakes.baremetal_resource_class,
            '--candidate-node', 'node1',
            '--trait', 'CUSTOM_1',
            '--candidate-node', 'node2',
            '--trait', 'CUSTOM_2',
        ]

        verifylist = [
            ('resource_class', baremetal_fakes.baremetal_resource_class),
            ('candidate_nodes', ['node1', 'node2']),
            ('traits', ['CUSTOM_1', 'CUSTOM_2']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        args = {
            'resource_class': baremetal_fakes.baremetal_resource_class,
            'candidate_nodes': ['node1', 'node2'],
            'traits': ['CUSTOM_1', 'CUSTOM_2'],
        }

        self.baremetal_mock.allocation.create.assert_called_once_with(**args)

    def test_baremetal_allocation_create_owner(self):
        arglist = [
            '--resource-class', baremetal_fakes.baremetal_resource_class,
            '--owner', baremetal_fakes.baremetal_owner,
        ]

        verifylist = [
            ('resource_class', baremetal_fakes.baremetal_resource_class),
            ('owner', baremetal_fakes.baremetal_owner),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        args = {
            'resource_class': baremetal_fakes.baremetal_resource_class,
            'owner': baremetal_fakes.baremetal_owner,
        }

        self.baremetal_mock.allocation.create.assert_called_once_with(**args)

    def test_baremetal_allocation_create_no_options(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exc.ClientException,
                          self.cmd.take_action,
                          parsed_args)

    def test_baremetal_allocation_backfill(self):
        arglist = [
            '--node', baremetal_fakes.baremetal_uuid,
        ]

        verifylist = [
            ('node', baremetal_fakes.baremetal_uuid),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        args = {
            'node': baremetal_fakes.baremetal_uuid,
        }

        self.baremetal_mock.allocation.create.assert_called_once_with(**args)


class TestShowBaremetalAllocation(TestBaremetalAllocation):

    def setUp(self):
        super(TestShowBaremetalAllocation, self).setUp()

        self.baremetal_mock.allocation.get.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.ALLOCATION),
                loaded=True))

        self.cmd = baremetal_allocation.ShowBaremetalAllocation(self.app, None)

    def test_baremetal_allocation_show(self):
        arglist = [baremetal_fakes.baremetal_uuid]
        verifylist = [('allocation', baremetal_fakes.baremetal_uuid)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.baremetal_mock.allocation.get.assert_called_once_with(
            baremetal_fakes.baremetal_uuid, fields=None)

        collist = ('name', 'node_uuid', 'resource_class', 'state', 'uuid')
        self.assertEqual(collist, columns)

        datalist = (
            baremetal_fakes.baremetal_name,
            baremetal_fakes.baremetal_uuid,
            baremetal_fakes.baremetal_resource_class,
            baremetal_fakes.baremetal_allocation_state,
            baremetal_fakes.baremetal_uuid,
        )

        self.assertEqual(datalist, tuple(data))

    def test_baremetal_allocation_show_no_options(self):
        arglist = []
        verifylist = []
        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestBaremetalAllocationList(TestBaremetalAllocation):
    def setUp(self):
        super(TestBaremetalAllocationList, self).setUp()

        self.baremetal_mock.allocation.list.return_value = [
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.ALLOCATION),
                loaded=True)
        ]
        self.cmd = baremetal_allocation.ListBaremetalAllocation(self.app, None)

    def test_baremetal_allocation_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'marker': None,
            'limit': None}
        self.baremetal_mock.allocation.list.assert_called_with(**kwargs)

        collist = (
            "UUID",
            "Name",
            "Resource Class",
            "State",
            "Node UUID")
        self.assertEqual(collist, columns)

        datalist = ((baremetal_fakes.baremetal_uuid,
                     baremetal_fakes.baremetal_name,
                     baremetal_fakes.baremetal_resource_class,
                     baremetal_fakes.baremetal_allocation_state,
                     baremetal_fakes.baremetal_uuid),)
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_allocation_list_node(self):
        arglist = ['--node', baremetal_fakes.baremetal_uuid]
        verifylist = [('node', baremetal_fakes.baremetal_uuid)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'node': baremetal_fakes.baremetal_uuid,
            'marker': None,
            'limit': None}
        self.baremetal_mock.allocation.list.assert_called_once_with(**kwargs)

        collist = (
            "UUID",
            "Name",
            "Resource Class",
            "State",
            "Node UUID")
        self.assertEqual(collist, columns)

        datalist = ((baremetal_fakes.baremetal_uuid,
                     baremetal_fakes.baremetal_name,
                     baremetal_fakes.baremetal_resource_class,
                     baremetal_fakes.baremetal_allocation_state,
                     baremetal_fakes.baremetal_uuid),)
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_allocation_list_resource_class(self):
        arglist = ['--resource-class',
                   baremetal_fakes.baremetal_resource_class]
        verifylist = [('resource_class',
                       baremetal_fakes.baremetal_resource_class)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'resource_class': baremetal_fakes.baremetal_resource_class,
            'marker': None,
            'limit': None}
        self.baremetal_mock.allocation.list.assert_called_once_with(**kwargs)

        collist = (
            "UUID",
            "Name",
            "Resource Class",
            "State",
            "Node UUID")
        self.assertEqual(collist, columns)

        datalist = ((baremetal_fakes.baremetal_uuid,
                     baremetal_fakes.baremetal_name,
                     baremetal_fakes.baremetal_resource_class,
                     baremetal_fakes.baremetal_allocation_state,
                     baremetal_fakes.baremetal_uuid),)
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_allocation_list_owner(self):
        arglist = ['--owner',
                   baremetal_fakes.baremetal_owner]
        verifylist = [('owner',
                       baremetal_fakes.baremetal_owner)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'owner': baremetal_fakes.baremetal_owner,
            'marker': None,
            'limit': None}
        self.baremetal_mock.allocation.list.assert_called_once_with(**kwargs)

        collist = (
            "UUID",
            "Name",
            "Resource Class",
            "State",
            "Node UUID")
        self.assertEqual(collist, columns)

        datalist = ((baremetal_fakes.baremetal_uuid,
                     baremetal_fakes.baremetal_name,
                     baremetal_fakes.baremetal_resource_class,
                     baremetal_fakes.baremetal_allocation_state,
                     baremetal_fakes.baremetal_uuid),)
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_allocation_list_state(self):
        arglist = ['--state', baremetal_fakes.baremetal_allocation_state]
        verifylist = [('state', baremetal_fakes.baremetal_allocation_state)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'state': baremetal_fakes.baremetal_allocation_state,
            'marker': None,
            'limit': None}
        self.baremetal_mock.allocation.list.assert_called_once_with(**kwargs)

        collist = (
            "UUID",
            "Name",
            "Resource Class",
            "State",
            "Node UUID")
        self.assertEqual(collist, columns)

        datalist = ((baremetal_fakes.baremetal_uuid,
                     baremetal_fakes.baremetal_name,
                     baremetal_fakes.baremetal_resource_class,
                     baremetal_fakes.baremetal_allocation_state,
                     baremetal_fakes.baremetal_uuid),)
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_allocation_list_long(self):
        arglist = ['--long']
        verifylist = [('long', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'marker': None,
            'limit': None,
        }
        self.baremetal_mock.allocation.list.assert_called_once_with(**kwargs)

        collist = ('UUID',
                   'Name',
                   'State',
                   'Owner',
                   'Node UUID',
                   'Last Error',
                   'Resource Class',
                   'Traits',
                   'Candidate Nodes',
                   'Extra',
                   'Created At',
                   'Updated At')
        self.assertEqual(collist, columns)

        datalist = ((baremetal_fakes.baremetal_uuid,
                     baremetal_fakes.baremetal_name,
                     baremetal_fakes.baremetal_allocation_state,
                     '',
                     baremetal_fakes.baremetal_uuid,
                     '',
                     baremetal_fakes.baremetal_resource_class,
                     '',
                     '',
                     '',
                     '',
                     ''),)
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_allocation_list_fields(self):
        arglist = ['--fields', 'uuid', 'node_uuid']
        verifylist = [('fields', [['uuid', 'node_uuid']])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        kwargs = {
            'marker': None,
            'limit': None,
            'fields': ('uuid', 'node_uuid')
        }
        self.baremetal_mock.allocation.list.assert_called_once_with(**kwargs)

    def test_baremetal_allocation_list_fields_multiple(self):
        arglist = ['--fields', 'uuid', 'node_uuid', '--fields', 'extra']
        verifylist = [('fields', [['uuid', 'node_uuid'], ['extra']])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        kwargs = {
            'marker': None,
            'limit': None,
            'fields': ('uuid', 'node_uuid', 'extra')
        }
        self.baremetal_mock.allocation.list.assert_called_once_with(**kwargs)

    def test_baremetal_allocation_list_invalid_fields(self):
        arglist = ['--fields', 'uuid', 'invalid']
        verifylist = [('fields', [['uuid', 'invalid']])]
        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestBaremetalAllocationDelete(TestBaremetalAllocation):

    def setUp(self):
        super(TestBaremetalAllocationDelete, self).setUp()

        self.baremetal_mock.allocation.get.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.ALLOCATION),
                loaded=True))

        self.cmd = baremetal_allocation.DeleteBaremetalAllocation(self.app,
                                                                  None)

    def test_baremetal_allocation_delete(self):
        arglist = [baremetal_fakes.baremetal_uuid]
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.baremetal_mock.allocation.delete.assert_called_once_with(
            baremetal_fakes.baremetal_uuid)

    def test_baremetal_allocation_delete_multiple(self):
        arglist = [baremetal_fakes.baremetal_uuid,
                   baremetal_fakes.baremetal_name]
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.baremetal_mock.allocation.delete.assert_has_calls(
            [mock.call(x) for x in arglist]
        )
        self.assertEqual(2, self.baremetal_mock.allocation.delete.call_count)

    def test_baremetal_allocation_delete_no_options(self):
        arglist = []
        verifylist = []
        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestBaremetalAllocationSet(TestBaremetalAllocation):
    def setUp(self):
        super(TestBaremetalAllocationSet, self).setUp()

        self.baremetal_mock.allocation.update.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.ALLOCATION),
                loaded=True))

        self.cmd = baremetal_allocation.SetBaremetalAllocation(
            self.app, None)

    def test_baremetal_allocation_set_name(self):
        new_name = 'foo'
        arglist = [
            baremetal_fakes.baremetal_uuid,
            '--name', new_name]
        verifylist = [
            ('allocation', baremetal_fakes.baremetal_uuid),
            ('name', new_name)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.allocation.update.assert_called_once_with(
            baremetal_fakes.baremetal_uuid,
            [{'path': '/name', 'value': new_name, 'op': 'add'}])

    def test_baremetal_allocation_set_extra(self):
        extra_value = 'foo=bar'
        arglist = [
            baremetal_fakes.baremetal_uuid,
            '--extra', extra_value]
        verifylist = [
            ('allocation', baremetal_fakes.baremetal_uuid),
            ('extra', [extra_value])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.allocation.update.assert_called_once_with(
            baremetal_fakes.baremetal_uuid,
            [{'path': '/extra/foo', 'value': 'bar', 'op': 'add'}])

    def test_baremetal_allocation_set_no_options(self):
        arglist = []
        verifylist = []
        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestBaremetalAllocationUnset(TestBaremetalAllocation):
    def setUp(self):
        super(TestBaremetalAllocationUnset, self).setUp()

        self.baremetal_mock.allocation.update.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.ALLOCATION),
                loaded=True))

        self.cmd = baremetal_allocation.UnsetBaremetalAllocation(
            self.app, None)

    def test_baremetal_allocation_unset_name(self):
        arglist = [
            baremetal_fakes.baremetal_uuid, '--name']
        verifylist = [('allocation',
                       baremetal_fakes.baremetal_uuid),
                      ('name', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.allocation.update.assert_called_once_with(
            baremetal_fakes.baremetal_uuid,
            [{'path': '/name', 'op': 'remove'}])

    def test_baremetal_allocation_unset_extra(self):
        arglist = [
            baremetal_fakes.baremetal_uuid, '--extra', 'key1']
        verifylist = [('allocation',
                       baremetal_fakes.baremetal_uuid),
                      ('extra', ['key1'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.allocation.update.assert_called_once_with(
            baremetal_fakes.baremetal_uuid,
            [{'path': '/extra/key1', 'op': 'remove'}])

    def test_baremetal_allocation_unset_multiple_extras(self):
        arglist = [
            baremetal_fakes.baremetal_uuid,
            '--extra', 'key1', '--extra', 'key2']
        verifylist = [('allocation',
                       baremetal_fakes.baremetal_uuid),
                      ('extra', ['key1', 'key2'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.allocation.update.assert_called_once_with(
            baremetal_fakes.baremetal_uuid,
            [{'path': '/extra/key1', 'op': 'remove'},
             {'path': '/extra/key2', 'op': 'remove'}])

    def test_baremetal_allocation_unset_no_options(self):
        arglist = []
        verifylist = []
        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_allocation_unset_no_property(self):
        uuid = baremetal_fakes.baremetal_uuid
        arglist = [uuid]
        verifylist = [('allocation', uuid)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.assertFalse(self.baremetal_mock.allocation.update.called)
