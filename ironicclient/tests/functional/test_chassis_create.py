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

import six
from tempest.lib.common.utils import data_utils
from tempest.lib import exceptions

from ironicclient.tests.functional import base


class NegativeChassisCreateTestsIronicClient(base.FunctionalTestBase):
    """Negative tests for testing chassis-create command.

    Negative tests for the Ironic CLI commands which check actions with
    chassis-create command like create chassis without arguments or with
    incorrect arguments and check that correct error message raised.
    """

    error_msg = r'ironic chassis-create: error:'
    expected_msg = r'expected one argument'

    def test_description_no_value(self):
        """Test steps:

        1) create chassis using -d argument without the value
        2) create chassis using --description argument without the value
        3) check that command using -d argument triggers an exception
        4) check that command with --description arg triggers an exception
        """
        ex_text = (r'{0} argument -d/--description: {1}'
                   .format(self.error_msg, self.expected_msg))
        six.assertRaisesRegex(self, exceptions.CommandFailed, ex_text,
                              self.create_chassis, '-d')
        six.assertRaisesRegex(self, exceptions.CommandFailed, ex_text,
                              self.create_chassis, '--description')

    def test_metadata_extra_no_value(self):
        """Test steps:

        1) create chassis using -e argument without the value
        2) create chassis using --extra argument without the value
        3) check that command using -e argument triggers an exception
        4) check that command with --extra argument triggers an exception
        """
        ex_text = (r'{0} argument -e/--extra: {1}'
                   .format(self.error_msg, self.expected_msg))
        six.assertRaisesRegex(self, exceptions.CommandFailed, ex_text,
                              self.create_chassis, '-e')
        six.assertRaisesRegex(self, exceptions.CommandFailed, ex_text,
                              self.create_chassis, '--extra')

    def test_specific_uuid_no_value(self):
        """Test steps:

        1) create chassis using -u argument without the value
        2) create chassis using --uuid argument without the value
        3) check that command using -u argument triggers an exception
        4) check that command with --uuid argument triggers an exception
        """
        ex_text = (r'{0} argument -u/--uuid: {1}'
                   .format(self.error_msg, self.expected_msg))
        six.assertRaisesRegex(self, exceptions.CommandFailed, ex_text,
                              self.create_chassis, '-u')
        six.assertRaisesRegex(self, exceptions.CommandFailed, ex_text,
                              self.create_chassis, '--uuid')

    def test_invalid_description(self):
        """Test steps:

        1) create chassis with invalid description using -d argument
        2) create chassis with invalid description using --description arg
        3) check that command using -d argument triggers an exception
        4) check that command using --uuid argument triggers an exception
        """
        description = '--'
        ex_text = (r'{0} argument -d/--description: {1}'
                   .format(self.error_msg, self.expected_msg))
        six.assertRaisesRegex(self, exceptions.CommandFailed, ex_text,
                              self.create_chassis,
                              params='-d {0}'.format(description))
        six.assertRaisesRegex(self, exceptions.CommandFailed, ex_text,
                              self.create_chassis,
                              params='--description {0}'.format(description))

    def test_invalid_metadata_extra(self):
        """Test steps:

        1) create chassis with invalid metadata using -e argument
        2) create chassis with invalid metadata using --extra argument
        3) check that command using -e argument triggers an exception
        4) check that command using --extra argument triggers an exception
        """
        extra = "HelloWorld"
        ex_text = (r'{0} Attributes must be a list of PATH=VALUE'
                   .format(self.error_msg))
        six.assertRaisesRegex(self, exceptions.CommandFailed, ex_text,
                              self.create_chassis,
                              params='-e {0}'.format(extra))
        six.assertRaisesRegex(self, exceptions.CommandFailed, ex_text,
                              self.create_chassis,
                              params='--extra {0}'.format(extra))

    def test_invalid_specific_uuid(self):
        """Test steps:

        1) create chassis with invalid specific uuid using -u argument
        2) create chassis with invalid specific uuid using --uuid argument
        3) check that command using -u argument triggers an exception
        4) check that command using --uuid argument triggers an exception
        """
        invalid_uuid = data_utils.rand_uuid()[:-1]
        ex_text = r'Expected a UUID but received {0}'.format(invalid_uuid)
        six.assertRaisesRegex(self, exceptions.CommandFailed, ex_text,
                              self.create_chassis,
                              params='-u {0}'.format(invalid_uuid))
        six.assertRaisesRegex(self, exceptions.CommandFailed, ex_text,
                              self.create_chassis,
                              params='--uuid {0}'.format(invalid_uuid))
