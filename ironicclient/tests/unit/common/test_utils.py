# Copyright 2013 OpenStack LLC.
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

import builtins
import json
import os
import subprocess
import sys
import tempfile
from unittest import mock


from ironicclient.common import utils
from ironicclient import exc
from ironicclient.tests.unit import utils as test_utils


class UtilsTest(test_utils.BaseTestCase):

    def test_key_value_pairs_to_dict(self):
        kv_list = ['str=foo', 'int=1', 'bool=true',
                   'list=[1, 2, 3]', 'dict={"foo": "bar"}']

        d = utils.key_value_pairs_to_dict(kv_list)
        self.assertEqual(
            {'str': 'foo', 'int': 1, 'bool': True,
             'list': [1, 2, 3], 'dict': {'foo': 'bar'}},
            d)

    def test_key_value_pairs_to_dict_nothing(self):
        self.assertEqual({}, utils.key_value_pairs_to_dict(None))
        self.assertEqual({}, utils.key_value_pairs_to_dict([]))

    def test_args_array_to_dict(self):
        my_args = {
            'matching_metadata': ['str=foo', 'int=1', 'bool=true',
                                  'list=[1, 2, 3]', 'dict={"foo": "bar"}'],
            'other': 'value'
        }
        cleaned_dict = utils.args_array_to_dict(my_args,
                                                "matching_metadata")
        self.assertEqual({
            'matching_metadata': {'str': 'foo', 'int': 1, 'bool': True,
                                  'list': [1, 2, 3], 'dict': {'foo': 'bar'}},
            'other': 'value'
        }, cleaned_dict)

    def test_args_array_to_patch(self):
        my_args = {
            'attributes': ['str=foo', 'int=1', 'bool=true',
                           'list=[1, 2, 3]', 'dict={"foo": "bar"}'],
            'op': 'add',
        }
        patch = utils.args_array_to_patch(my_args['op'],
                                          my_args['attributes'])
        self.assertEqual([{'op': 'add', 'value': 'foo', 'path': '/str'},
                          {'op': 'add', 'value': 1, 'path': '/int'},
                          {'op': 'add', 'value': True, 'path': '/bool'},
                          {'op': 'add', 'value': [1, 2, 3], 'path': '/list'},
                          {'op': 'add', 'value': {"foo": "bar"},
                           'path': '/dict'}], patch)

    def test_args_array_to_patch_format_error(self):
        my_args = {
            'attributes': ['foobar'],
            'op': 'add',
        }
        self.assertRaises(exc.CommandError, utils.args_array_to_patch,
                          my_args['op'], my_args['attributes'])

    def test_args_array_to_patch_remove(self):
        my_args = {
            'attributes': ['/foo', 'extra/bar'],
            'op': 'remove',
        }
        patch = utils.args_array_to_patch(my_args['op'],
                                          my_args['attributes'])
        self.assertEqual([{'op': 'remove', 'path': '/foo'},
                          {'op': 'remove', 'path': '/extra/bar'}], patch)

    def test_split_and_deserialize(self):
        ret = utils.split_and_deserialize('str=foo')
        self.assertEqual(('str', 'foo'), ret)

        ret = utils.split_and_deserialize('int=1')
        self.assertEqual(('int', 1), ret)

        ret = utils.split_and_deserialize('bool=false')
        self.assertEqual(('bool', False), ret)

        ret = utils.split_and_deserialize('list=[1, "foo", 2]')
        self.assertEqual(('list', [1, "foo", 2]), ret)

        ret = utils.split_and_deserialize('dict={"foo": 1}')
        self.assertEqual(('dict', {"foo": 1}), ret)

        ret = utils.split_and_deserialize('str_int="1"')
        self.assertEqual(('str_int', "1"), ret)

    def test_split_and_deserialize_fail(self):
        self.assertRaises(exc.CommandError,
                          utils.split_and_deserialize, 'foo:bar')

    def test_bool_arg_value(self):
        self.assertTrue(utils.bool_argument_value('arg', 'y', strict=True))
        self.assertTrue(utils.bool_argument_value('arg', 'TrUe', strict=True))
        self.assertTrue(utils.bool_argument_value('arg', '1', strict=True))
        self.assertTrue(utils.bool_argument_value('arg', 1, strict=True))

        self.assertFalse(utils.bool_argument_value('arg', '0', strict=True))
        self.assertFalse(utils.bool_argument_value('arg', 'No', strict=True))

        self.assertRaises(exc.CommandError,
                          utils.bool_argument_value, 'arg', 'ee', strict=True)

        self.assertFalse(utils.bool_argument_value('arg', 'ee', strict=False))
        self.assertTrue(utils.bool_argument_value('arg', 'ee', strict=False,
                                                  default=True))
        # No check that default is a Boolean...
        self.assertEqual('foo', utils.bool_argument_value('arg', 'ee',
                         strict=False, default='foo'))

    def test_check_for_invalid_fields(self):
        self.assertIsNone(utils.check_for_invalid_fields(
                          ['a', 'b'], ['a', 'b', 'c']))
        # 'd' is not a valid field
        self.assertRaises(exc.CommandError, utils.check_for_invalid_fields,
                          ['a', 'd'], ['a', 'b', 'c'])

    def test_convert_list_props_to_comma_separated_strings(self):
        data = {'prop1': 'val1',
                'prop2': ['item1', 'item2', 'item3']}
        result = utils.convert_list_props_to_comma_separated(data)
        self.assertEqual('val1', result['prop1'])
        self.assertEqual('item1, item2, item3', result['prop2'])

    def test_convert_list_props_to_comma_separated_mix(self):
        data = {'prop1': 'val1',
                'prop2': [1, 2.5, 'item3']}
        result = utils.convert_list_props_to_comma_separated(data)
        self.assertEqual('val1', result['prop1'])
        self.assertEqual('1, 2.5, item3', result['prop2'])

    def test_convert_list_props_to_comma_separated_partial(self):
        data = {'prop1': [1, 2, 3],
                'prop2': [1, 2.5, 'item3']}
        result = utils.convert_list_props_to_comma_separated(
            data, props=['prop2'])
        self.assertEqual([1, 2, 3], result['prop1'])
        self.assertEqual('1, 2.5, item3', result['prop2'])


class CommonParamsForListTest(test_utils.BaseTestCase):
    def setUp(self):
        super(CommonParamsForListTest, self).setUp()
        self.args = mock.Mock(marker=None, limit=None, sort_key=None,
                              sort_dir=None, detail=False, fields=None,
                              spec=True)
        self.expected_params = {'detail': False}

    def test_nothing_set(self):
        self.assertEqual(self.expected_params,
                         utils.common_params_for_list(self.args, [], []))

    def test_marker_and_limit(self):
        self.args.marker = 'foo'
        self.args.limit = 42
        self.expected_params.update({'marker': 'foo', 'limit': 42})
        self.assertEqual(self.expected_params,
                         utils.common_params_for_list(self.args, [], []))

    def test_invalid_limit(self):
        self.args.limit = -42
        self.assertRaises(exc.CommandError,
                          utils.common_params_for_list,
                          self.args, [], [])

    def test_sort_key_and_sort_dir(self):
        self.args.sort_key = 'field'
        self.args.sort_dir = 'desc'
        self.expected_params.update({'sort_key': 'field', 'sort_dir': 'desc'})
        self.assertEqual(self.expected_params,
                         utils.common_params_for_list(self.args,
                                                      ['field'],
                                                      []))

    def test_sort_key_allows_label(self):
        self.args.sort_key = 'Label'
        self.expected_params.update({'sort_key': 'field'})
        self.assertEqual(self.expected_params,
                         utils.common_params_for_list(self.args,
                                                      ['field', 'field2'],
                                                      ['Label', 'Label2']))

    def test_sort_key_invalid(self):
        self.args.sort_key = 'something'
        self.assertRaises(exc.CommandError,
                          utils.common_params_for_list,
                          self.args,
                          ['field', 'field2'],
                          [])

    def test_sort_dir_invalid(self):
        self.args.sort_dir = 'something'
        self.assertRaises(exc.CommandError,
                          utils.common_params_for_list,
                          self.args,
                          [],
                          [])

    def test_detail(self):
        self.args.detail = True
        self.expected_params['detail'] = True
        self.assertEqual(self.expected_params,
                         utils.common_params_for_list(self.args, [], []))

    def test_fields(self):
        self.args.fields = [['a', 'b', 'c']]
        self.expected_params.update({'fields': ['a', 'b', 'c']})
        self.assertEqual(self.expected_params,
                         utils.common_params_for_list(self.args, [], []))


class CommonFiltersTest(test_utils.BaseTestCase):
    def test_limit(self):
        result = utils.common_filters(limit=42)
        self.assertEqual(['limit=42'], result)

    def test_limit_0(self):
        result = utils.common_filters(limit=0)
        self.assertEqual([], result)

    def test_other(self):
        for key in ('marker', 'sort_key', 'sort_dir'):
            result = utils.common_filters(**{key: 'test'})
            self.assertEqual(['%s=test' % key], result)

    def test_fields(self):
        result = utils.common_filters(fields=['a', 'b', 'c'])
        self.assertEqual(['fields=a,b,c'], result)


@mock.patch.object(subprocess, 'Popen', autospec=True)
class MakeConfigDriveTest(test_utils.BaseTestCase):

    def setUp(self):
        super(MakeConfigDriveTest, self).setUp()
        # expected genisoimage cmd
        self.genisoimage_cmd = ['genisoimage', '-o', mock.ANY,
                                '-ldots', '-allow-lowercase',
                                '-allow-multidot', '-l',
                                '-publisher', 'ironicclient-configdrive 0.1',
                                '-quiet', '-J', '-r', '-V',
                                'config-2', mock.ANY]

        self.mkisofs_cmd = ['mkisofs', '-o', mock.ANY,
                            '-ldots', '-allow-lowercase',
                            '-allow-multidot', '-l',
                            '-publisher', 'ironicclient-configdrive 0.1',
                            '-quiet', '-J', '-r', '-V',
                            'config-2', mock.ANY]

        self.xorrisofs_cmd = ['xorrisofs', '-o', mock.ANY,
                              '-ldots', '-allow-lowercase',
                              '-allow-multidot', '-l',
                              '-publisher', 'ironicclient-configdrive 0.1',
                              '-quiet', '-J', '-r', '-V',
                              'config-2', mock.ANY]

    def test_make_configdrive(self, mock_popen):
        fake_process = mock.Mock(returncode=0)
        fake_process.communicate.return_value = ('', '')
        mock_popen.return_value = fake_process

        with utils.tempdir() as dirname:
            utils.make_configdrive(dirname)

        mock_popen.assert_called_once_with(self.genisoimage_cmd,
                                           stderr=subprocess.PIPE,
                                           stdout=subprocess.PIPE)
        fake_process.communicate.assert_called_once_with()

    def test_make_configdrive_fallsback(self, mock_popen):
        fake_process = mock.Mock(returncode=0)
        fake_process.communicate.return_value = ('', '')
        mock_popen.side_effect = iter([OSError('boom'),
                                       OSError('boom'),
                                       fake_process])
        with utils.tempdir() as dirname:
            utils.make_configdrive(dirname)
        mock_popen.assert_has_calls([
            mock.call(self.genisoimage_cmd, stderr=subprocess.PIPE,
                      stdout=subprocess.PIPE),
            mock.call(self.mkisofs_cmd, stderr=subprocess.PIPE,
                      stdout=subprocess.PIPE),
            mock.call(self.xorrisofs_cmd, stderr=subprocess.PIPE,
                      stdout=subprocess.PIPE)
        ])
        fake_process.communicate.assert_called_once_with()

    @mock.patch.object(os, 'access', autospec=True)
    def test_make_configdrive_non_readable_dir(self, mock_access, mock_popen):
        mock_access.return_value = False
        self.assertRaises(exc.CommandError, utils.make_configdrive, 'fake-dir')
        mock_access.assert_called_once_with('fake-dir', os.R_OK)
        self.assertFalse(mock_popen.called)

    @mock.patch.object(os, 'access', autospec=True)
    def test_make_configdrive_oserror(self, mock_access, mock_popen):
        mock_access.return_value = True
        mock_popen.side_effect = OSError('boom')

        self.assertRaises(exc.CommandError, utils.make_configdrive, 'fake-dir')
        mock_access.assert_called_once_with('fake-dir', os.R_OK)
        mock_popen.assert_has_calls([
            mock.call(self.genisoimage_cmd, stderr=subprocess.PIPE,
                      stdout=subprocess.PIPE),
            mock.call(self.mkisofs_cmd, stderr=subprocess.PIPE,
                      stdout=subprocess.PIPE),
            mock.call(self.xorrisofs_cmd, stderr=subprocess.PIPE,
                      stdout=subprocess.PIPE)
        ])

    @mock.patch.object(os, 'access', autospec=True)
    def test_make_configdrive_non_zero_returncode(self, mock_access,
                                                  mock_popen):
        fake_process = mock.Mock(returncode=123)
        fake_process.communicate.return_value = ('', '')
        mock_popen.return_value = fake_process

        self.assertRaises(exc.CommandError, utils.make_configdrive, 'fake-dir')
        mock_access.assert_called_once_with('fake-dir', os.R_OK)
        mock_popen.assert_called_once_with(self.genisoimage_cmd,
                                           stderr=subprocess.PIPE,
                                           stdout=subprocess.PIPE)
        fake_process.communicate.assert_called_once_with()


class GetFromStdinTest(test_utils.BaseTestCase):

    @mock.patch.object(sys, 'stdin', autospec=True)
    def test_get_from_stdin(self, mock_stdin):
        contents = '[{"step": "upgrade", "interface": "deploy"}]'
        mock_stdin.read.return_value = contents
        desc = 'something'

        info = utils.get_from_stdin(desc)
        self.assertEqual(info, contents)
        mock_stdin.read.assert_called_once_with()

    @mock.patch.object(sys, 'stdin', autospec=True)
    def test_get_from_stdin_fail(self, mock_stdin):
        mock_stdin.read.side_effect = IOError
        desc = 'something'

        self.assertRaises(exc.InvalidAttribute, utils.get_from_stdin, desc)
        mock_stdin.read.assert_called_once_with()


class HandleJsonFileTest(test_utils.BaseTestCase):

    def test_handle_json_or_file_arg(self):
        cleansteps = '[{"step": "upgrade", "interface": "deploy"}]'
        steps = utils.handle_json_or_file_arg(cleansteps)
        self.assertEqual(json.loads(cleansteps), steps)

    def test_handle_json_or_file_arg_bad_json(self):
        cleansteps = '{foo invalid: json{'
        self.assertRaisesRegex(exc.InvalidAttribute,
                               'is not a file and cannot be parsed as JSON',
                               utils.handle_json_or_file_arg, cleansteps)

    def test_handle_json_or_file_arg_file(self):
        contents = '[{"step": "upgrade", "interface": "deploy"}]'

        with tempfile.NamedTemporaryFile(mode='w') as f:
            f.write(contents)
            f.flush()
            steps = utils.handle_json_or_file_arg(f.name)

        self.assertEqual(json.loads(contents), steps)

    def test_handle_yaml_or_file_arg_file(self):
        contents = '''---
- step: upgrade
  interface: deploy'''

        with tempfile.NamedTemporaryFile(mode='w') as f:
            f.write(contents)
            f.flush()
            steps = utils.handle_json_or_file_arg(f.name)

        self.assertEqual([{"step": "upgrade", "interface": "deploy"}], steps)

    @mock.patch.object(builtins, 'open', autospec=True)
    def test_handle_json_or_file_arg_file_fail(self, mock_open):
        mock_open.return_value.__enter__.side_effect = IOError

        with tempfile.NamedTemporaryFile(mode='w') as f:
            self.assertRaisesRegex(exc.InvalidAttribute,
                                   "from file",
                                   utils.handle_json_or_file_arg, f.name)
            mock_open.assert_called_once_with(f.name, 'r')


class GetJsonDataTest(test_utils.BaseTestCase):

    def test_success(self):
        result = utils.get_json_data(b'\n{"answer": 42}')
        self.assertEqual({"answer": 42}, result)

    def test_definitely_not_json(self):
        self.assertIsNone(utils.get_json_data(b'0x010x020x03'))

    def test_could_be_json(self):
        self.assertIsNone(utils.get_json_data(b'{"hahaha, just kidding\x00'))
