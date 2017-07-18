# Copyright (c) 2015 Mirantis, Inc.
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

from ironicclient.tests.functional import base


class IronicClientHelp(base.FunctionalTestBase):
    """Test for python-ironicclient help messages."""

    def test_ironic_help(self):
        """Check Ironic client main help message contents."""
        caption = ("Command-line interface to the "
                   "OpenStack Bare Metal Provisioning API.")
        subcommands = {
            'bash-completion',
            'chassis-create',
            'chassis-delete',
            'chassis-list',
            'chassis-node-list',
            'chassis-show',
            'chassis-update',
            'driver-list',
            'driver-properties',
            'driver-show',
            'driver-vendor-passthru',
            'help',
            'node-create',
            'node-delete',
            'node-get-boot-device',
            'node-get-console',
            'node-get-supported-boot-devices',
            'node-list',
            'node-port-list',
            'node-set-boot-device',
            'node-set-console-mode',
            'node-set-maintenance',
            'node-set-power-state',
            'node-set-provision-state',
            'node-show',
            'node-show-states',
            'node-update',
            'node-validate',
            'node-vendor-passthru',
            'node-vif-attach',
            'node-vif-detach',
            'node-vif-list',
            'port-create',
            'port-delete',
            'port-list',
            'port-show',
            'port-update'
        }

        output = self._ironic('help', flags='', params='')

        self.assertIn(caption, output)
        for string in subcommands:
            self.assertIn(string, output)

    def test_warning_on_api_version(self):
        result = self._ironic('help', merge_stderr=True)
        self.assertIn('You are using the default API version', result)

        result = self._ironic('help', flags='--ironic-api-version 1.9',
                              merge_stderr=True)
        self.assertNotIn('You are using the default API version', result)
