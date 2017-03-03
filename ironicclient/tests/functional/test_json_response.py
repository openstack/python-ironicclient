# Copyright (c) 2016 Mirantis, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json

import jsonschema
from tempest.lib.common.utils import data_utils

from ironicclient.tests.functional import base


def _is_valid_json(json_response, schema):
    """Verify JSON is valid.

    :param json_response: JSON response from CLI
    :type json_response: string
    :param schema: expected schema of response
    :type json_response: dictionary
    """
    try:
        json_response = json.loads(json_response)
        jsonschema.validate(json_response, schema)
    except jsonschema.ValidationError:
        return False
    return True


class TestNodeJsonResponse(base.FunctionalTestBase):
    """Test JSON responses for node commands."""

    node_schema = {
        "type": "object",
        "properties": {
            "target_power_state": {"type": ["string", "null"]},
            "extra": {"type": "object"},
            "last_error": {"type": ["string", "null"]},
            "updated_at": {"type": ["string", "null"]},
            "maintenance_reason": {"type": ["string", "null"]},
            "provision_state": {"type": "string"},
            "clean_step": {"type": "object"},
            "uuid": {"type": "string"},
            "console_enabled": {"type": "boolean"},
            "target_provision_state": {"type": ["string", "null"]},
            "raid_config": {"type": "string"},
            "provision_updated_at": {"type": ["string", "null"]},
            "maintenance": {"type": "boolean"},
            "target_raid_config": {"type": "string"},
            "inspection_started_at": {"type": ["string", "null"]},
            "inspection_finished_at": {"type": ["string", "null"]},
            "power_state": {"type": ["string", "null"]},
            "driver": {"type": "string"},
            "reservation": {"type": ["string", "null"]},
            "properties": {"type": "object"},
            "instance_uuid": {"type": ["string", "null"]},
            "name": {"type": ["string", "null"]},
            "driver_info": {"type": "object"},
            "created_at": {"type": "string"},
            "driver_internal_info": {"type": "object"},
            "chassis_uuid": {"type": ["string", "null"]},
            "instance_info": {"type": "object"}
            }
        }

    def setUp(self):
        super(TestNodeJsonResponse, self).setUp()
        self.node = self.create_node()

    def test_node_list_json(self):
        """Test JSON response for nodes list."""
        schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "instance_uuid": {"type": ["string", "null"]},
                    "maintenance": {"type": "boolean"},
                    "name": {"type": ["string", "null"]},
                    "power_state": {"type": ["string", "null"]},
                    "provision_state": {"type": "string"},
                    "uuid": {"type": "string"}}}
        }
        response = self.ironic('node-list', flags='--json',
                               params='', parse=False)
        self.assertTrue(_is_valid_json(response, schema))

    def test_node_show_json(self):
        """Test JSON response for node show."""
        response = self.ironic('node-show', flags='--json', params='{0}'
                               .format(self.node['uuid']), parse=False)
        self.assertTrue(_is_valid_json(response, self.node_schema))

    def test_node_validate_json(self):
        """Test JSON response for node validation."""
        schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "interface": {"type": ["string", "null"]},
                    "result": {"type": "boolean"},
                    "reason": {"type": ["string", "null"]}}}
        }
        response = self.ironic('node-validate', flags='--json',
                               params='{0}'.format(self.node['uuid']),
                               parse=False)
        self.assertTrue(_is_valid_json(response, schema))

    def test_node_show_states_json(self):
        """Test JSON response for node show states."""
        schema = {
            "type": "object",
            "properties": {
                "target_power_state": {"type": ["string", "null"]},
                "target_provision_state": {"type": ["string", "null"]},
                "last_error": {"type": ["string", "null"]},
                "console_enabled": {"type": "boolean"},
                "provision_updated_at": {"type": ["string", "null"]},
                "power_state": {"type": ["string", "null"]},
                "provision_state": {"type": "string"}
            }
        }
        response = self.ironic('node-show-states', flags='--json',
                               params='{0}'.format(self.node['uuid']),
                               parse=False)
        self.assertTrue(_is_valid_json(response, schema))

    def test_node_create_json(self):
        """Test JSON response for node creation."""
        schema = {
            "type": "object",
            "properties": {
                "uuid": {"type": "string"},
                "driver_info": {"type": "object"},
                "extra": {"type": "object"},
                "driver": {"type": "string"},
                "chassis_uuid": {"type": ["string", "null"]},
                "properties": {"type": "object"},
                "name": {"type": ["string", "null"]},
            }
        }
        node_name = 'nodejson'
        response = self.ironic('node-create', flags='--json',
                               params='-d fake -n {0}'.format(node_name),
                               parse=False)
        self.addCleanup(self.delete_node, node_name)
        self.assertTrue(_is_valid_json(response, schema))

    def test_node_update_json(self):
        """Test JSON response for node update."""
        node_name = data_utils.rand_name('test')
        response = self.ironic('node-update', flags='--json',
                               params='{0} add name={1}'
                               .format(self.node['uuid'], node_name),
                               parse=False)
        self.assertTrue(_is_valid_json(response, self.node_schema))


class TestDriverJsonResponse(base.FunctionalTestBase):
    """Test JSON responses for driver commands."""

    def test_driver_list_json(self):
        """Test JSON response for drivers list."""
        schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "hosts": {"type": "string"},
                    }}
        }
        response = self.ironic('driver-list', flags='--json', parse=False)
        self.assertTrue(_is_valid_json(response, schema))

    def test_driver_show_json(self):
        """Test JSON response for driver show."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "hosts": {
                    "type": "array",
                    "items": {"type": "string"}}
            }
        }
        drivers_names = self.get_drivers_names()
        for driver in drivers_names:
            response = self.ironic('driver-show', flags='--json',
                                   params='{0}'.format(driver), parse=False)
            self.assertTrue(_is_valid_json(response, schema))

    def test_driver_properties_json(self):
        """Test JSON response for driver properties."""
        schema = {
            "type": "object",
            "additionalProperties": {"type": "string"}
        }
        drivers_names = self.get_drivers_names()
        for driver in drivers_names:
            response = self.ironic('driver-properties', flags='--json',
                                   params='{0}'.format(driver), parse=False)
            self.assertTrue(_is_valid_json(response, schema))


class TestChassisJsonResponse(base.FunctionalTestBase):
    """Test JSON responses for chassis commands."""

    chassis_schema = {
        "type": "object",
        "properties": {
            "uuid": {"type": "string"},
            "updated_at": {"type": ["string", "null"]},
            "created_at": {"type": "string"},
            "description": {"type": ["string", "null"]},
            "extra": {"type": "object"}}
    }

    def setUp(self):
        super(TestChassisJsonResponse, self).setUp()
        self.chassis = self.create_chassis()

    def test_chassis_list_json(self):
        """Test JSON response for chassis list."""
        schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "uuid": {"type": "string"},
                    "description": {"type": ["string", "null"]}}
            }
        }
        response = self.ironic('chassis-list', flags='--json', parse=False)
        self.assertTrue(_is_valid_json(response, schema))

    def test_chassis_show_json(self):
        """Test JSON response for chassis show."""
        response = self.ironic('chassis-show', flags='--json',
                               params='{0}'.format(self.chassis['uuid']),
                               parse=False)
        self.assertTrue(_is_valid_json(response, self.chassis_schema))

    def test_chassis_create_json(self):
        """Test JSON response for chassis create."""
        response = self.ironic('chassis-create', flags='--json', parse=False)
        self.assertTrue(_is_valid_json(response, self.chassis_schema))

    def test_chassis_update_json(self):
        """Test JSON response for chassis update."""
        response = self.ironic(
            'chassis-update', flags='--json', params='{0} {1} {2}'.format(
                self.chassis['uuid'], 'add', 'description=test-chassis'),
            parse=False)
        self.assertTrue(_is_valid_json(response, self.chassis_schema))

    def test_chassis_node_list_json(self):
        """Test JSON response for chassis-node-list command."""
        schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "instance_uuid": {"type": ["string", "null"]},
                    "maintenance": {"type": "boolean"},
                    "name": {"type": ["string", "null"]},
                    "power_state": {"type": ["string", "null"]},
                    "provision_state": {"type": "string"},
                    "uuid": {"type": "string"}}}
        }
        self.node = self.create_node()
        self.update_node(self.node['uuid'], 'add chassis_uuid={0}'
                         .format(self.chassis['uuid']))
        response = self.ironic('chassis-node-list', flags='--json',
                               params='{0}'.format(self.chassis['uuid']),
                               parse=False)
        self.assertTrue(_is_valid_json(response, schema))
