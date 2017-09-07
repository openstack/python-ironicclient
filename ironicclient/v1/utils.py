# Copyright 2016 Intel Corporation
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

HTTP_METHODS = ['POST', 'PUT', 'GET', 'DELETE', 'PATCH']

BOOT_DEVICES = ['pxe', 'disk', 'cdrom', 'bios', 'safe', 'wanboot']

# Polling intervals in seconds.
_LONG_ACTION_POLL_INTERVAL = 10
_SHORT_ACTION_POLL_INTERVAL = 2
# This dict acts as both list of possible provision actions and arguments for
# wait_for_provision_state invocation.
PROVISION_ACTIONS = {
    'active': {'expected_state': 'active',
               'poll_interval': _LONG_ACTION_POLL_INTERVAL},
    'deleted': {'expected_state': 'available',
                'poll_interval': _LONG_ACTION_POLL_INTERVAL},
    'rebuild': {'expected_state': 'active',
                'poll_interval': _LONG_ACTION_POLL_INTERVAL},
    'inspect': {'expected_state': 'manageable',
                # This is suboptimal for in-band inspection, but it's probably
                # not worth making people wait 10 seconds for OOB inspection
                'poll_interval': _SHORT_ACTION_POLL_INTERVAL},
    'provide': {'expected_state': 'available',
                # This assumes cleaning is in place
                'poll_interval': _LONG_ACTION_POLL_INTERVAL},
    'manage': {'expected_state': 'manageable',
               'poll_interval': _SHORT_ACTION_POLL_INTERVAL},
    'clean': {'expected_state': 'manageable',
              'poll_interval': _LONG_ACTION_POLL_INTERVAL},
    'adopt': {'expected_state': 'active',
              'poll_interval': _SHORT_ACTION_POLL_INTERVAL},
    'abort': None,  # no support for --wait in abort
    'rescue': {'expected_state': 'rescue',
               'poll_interval': _LONG_ACTION_POLL_INTERVAL},
    'unrescue': {'expected_state': 'active',
                 'poll_interval': _LONG_ACTION_POLL_INTERVAL},
}

PROVISION_STATES = list(PROVISION_ACTIONS)
