# Copyright 2012 OpenStack LLC.
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

from __future__ import annotations

import base64
import contextlib
import gzip
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any
from typing import Callable
from typing import cast
from typing import Generator
from typing import Iterator
from typing import Protocol

from cliff import columns
from oslo_utils import strutils
import yaml  # type: ignore[import-untyped]  # PyYAML has no type stubs

from ironicclient.common.i18n import _
from ironicclient import exc


class ListCommandArgs(Protocol):
    """Protocol for parsed args passed to list commands (marker, limit, etc).

    """

    marker: str | None
    limit: int | None
    sort_key: str | None
    sort_dir: str | None
    detail: bool
    fields: list[list[str]] | None


def split_and_deserialize(string: str) -> tuple[str, Any]:
    """Split and try to JSON deserialize a string.

    Gets a string with the KEY=VALUE format, split it (using '=' as the
    separator) and try to JSON deserialize the VALUE.

    :returns: A tuple of (key, value).
    """
    try:
        key, value = string.split("=", 1)
    except ValueError:
        raise exc.CommandError(_('Attributes must be a list of '
                                 'PATH=VALUE not "%s"') % string)
    try:
        value = json.loads(value)
    except ValueError:
        pass

    return (key, value)


def key_value_pairs_to_dict(
    key_value_pairs: list[str] | None,
) -> dict[str, Any]:
    """Convert a list of key-value pairs to a dictionary.

    :param key_value_pairs: a list of strings, each string is in the form
                            <key>=<value>
    :returns: a dictionary, possibly empty
    """
    if key_value_pairs:
        return dict(split_and_deserialize(v) for v in key_value_pairs)
    return {}


def args_array_to_dict(
    kwargs: dict[str, Any],
    key_to_convert: str,
) -> dict[str, Any]:
    """Convert the value in a dictionary entry to a dictionary.

    From the kwargs dictionary, converts the value of the key_to_convert
    entry from a list of key-value pairs to a dictionary.

    :param kwargs: a dictionary
    :param key_to_convert: the key (in kwargs), whose value is expected to
        be a list of key=value strings. This value will be converted to a
        dictionary.
    :returns: kwargs, the (modified) dictionary
    """
    values_to_convert = kwargs.get(key_to_convert)
    if values_to_convert:
        kwargs[key_to_convert] = key_value_pairs_to_dict(values_to_convert)
    return kwargs


def args_array_to_patch(
    op: str,
    attributes: list[str],
) -> list[dict[str, Any]]:
    patch = []
    for attr in attributes:
        # Sanitize
        if not attr.startswith('/'):
            attr = '/' + attr

        if op in ['add', 'replace']:
            path, value = split_and_deserialize(attr)
            patch.append({'op': op, 'path': path, 'value': value})

        elif op == "remove":
            # For remove only the key is needed
            patch.append({'op': op, 'path': attr})
        else:
            raise exc.CommandError(_('Unknown PATCH operation: %s') % op)
    return patch


def convert_list_props_to_comma_separated(
    data: dict[str, Any],
    props: list[str] | None = None,
) -> dict[str, Any]:
    """Convert the list-type properties to comma-separated strings

    :param data: the input dict object.
    :param props: the properties whose values will be converted.
        Default to None to convert all list-type properties of the input.
    :returns: the result dict instance.
    """
    result = dict(data)

    if props is None:
        props = list(data.keys())

    for prop in props:
        val = data.get(prop, None)
        if isinstance(val, list):
            result[prop] = ', '.join(map(str, val))

    return result


def common_params_for_list(
    args: ListCommandArgs,
    fields: list[str],
    field_labels: list[str],
) -> dict[str, Any]:
    """Generate 'params' dict that is common for every 'list' command.

    :param args: arguments from command line.
    :param fields: possible fields for sorting.
    :param field_labels: possible field labels for sorting.
    :returns: a dict with params to pass to the client method.
    """
    params: dict[str, Any] = {}
    if args.marker is not None:
        params['marker'] = args.marker
    if args.limit is not None:
        if args.limit < 0:
            raise exc.CommandError(
                _('Expected non-negative --limit, got %s') % args.limit)
        params['limit'] = args.limit

    if args.sort_key is not None:
        # Support using both heading and field name for sort_key
        fields_map = dict(zip(field_labels, fields))
        fields_map.update(zip(fields, fields))
        try:
            sort_key = fields_map[args.sort_key]
        except KeyError:
            raise exc.CommandError(
                _("%(sort_key)s is an invalid field for sorting, "
                  "valid values for --sort-key are: %(valid)s") %
                {'sort_key': args.sort_key,
                 'valid': list(fields_map)})
        params['sort_key'] = sort_key
    if args.sort_dir is not None:
        if args.sort_dir not in ('asc', 'desc'):
            raise exc.CommandError(
                _("%s is an invalid value for sort direction, "
                  "valid values for --sort-dir are: 'asc', 'desc'") %
                args.sort_dir)
        params['sort_dir'] = args.sort_dir

    params['detail'] = args.detail

    requested_fields = args.fields[0] if args.fields else None
    if requested_fields is not None:
        params['fields'] = requested_fields

    return params


def common_filters(
    marker: str | None = None,
    limit: int | None = None,
    sort_key: str | None = None,
    sort_dir: str | None = None,
    fields: list[str] | None = None,
    detail: bool = False,
    project: str | None = None,
    public: bool | None = None,
) -> list[str]:
    """Generate common filters for any list request.

    :param marker: entity ID from which to start returning entities.
    :param limit: maximum number of entities to return.
    :param sort_key: field to use for sorting.
    :param sort_dir: direction of sorting: 'asc' or 'desc'.
    :param fields: a list with a specified set of fields of the resource
                   to be returned.
    :param detail: Boolean, True to return detailed information. This parameter
                   can be used for resources which accept 'detail' as a URL
                   parameter.
    :returns: list of string filters.
    """
    filters = []
    if isinstance(limit, int) and limit > 0:
        filters.append('limit=%s' % limit)
    if marker is not None:
        filters.append('marker=%s' % marker)
    if sort_key is not None:
        filters.append('sort_key=%s' % sort_key)
    if sort_dir is not None:
        filters.append('sort_dir=%s' % sort_dir)
    if project is not None:
        filters.append('project=%s' % project)
    if public is not None:
        filters.append('public=True')
    if fields is not None:
        filters.append('fields=%s' % ','.join(fields))
    if detail:
        filters.append('detail=True')
    return filters


# NOTE(karan): *args/**kwargs can be narrowed to match tempfile.mkdtemp:
# use keyword-only params (suffix: str | None, prefix: str | None,
# dir: str | None) and call mkdtemp(suffix=..., prefix=..., dir=...) for
# stricter typing.
@contextlib.contextmanager
def tempdir(
    *args: Any,
    **kwargs: Any,
) -> Generator[str, None, None]:
    dirname = tempfile.mkdtemp(*args, **kwargs)
    try:
        yield dirname
    finally:
        shutil.rmtree(dirname)


def make_configdrive(path: str) -> bytes:
    """Make the config drive file.

    :param path: The directory containing the config drive files.
    :returns: A gzipped and base64 encoded configdrive string.

    """
    # Make sure path it's readable
    if not os.access(path, os.R_OK):
        raise exc.CommandError(_('The directory "%s" is not readable') % path)

    with tempfile.NamedTemporaryFile() as tmpfile:
        with tempfile.NamedTemporaryFile() as tmpzipfile:
            publisher = 'ironicclient-configdrive 0.1'
            # NOTE(toabctl): Luckily, genisoimage, mkisofs and xorrisofs
            # understand the same parameters which are currently used.
            cmds = ['genisoimage', 'mkisofs', 'xorrisofs']
            error: OSError | None = None
            p: subprocess.Popen[bytes] | None = None
            for c in cmds:
                try:
                    p = subprocess.Popen([c, '-o', tmpfile.name,
                                          '-ldots', '-allow-lowercase',
                                          '-allow-multidot', '-l',
                                          '-publisher', publisher,
                                          '-quiet', '-J',
                                          '-r', '-V', 'config-2',
                                          path],
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
                except OSError as e:
                    error = e
                else:
                    error = None
                    break
            if error or p is None:
                raise exc.CommandError(
                    _('Error generating the config drive. Make sure the '
                      '"genisoimage", "mkisofs", or "xorriso" tool is '
                      'installed. Error: %s') % error)

            stdout, stderr = p.communicate()
            if p.returncode != 0:
                raise exc.CommandError(
                    _('Error generating the config drive.'
                      'Stdout: "%(stdout)s". Stderr: %(stderr)s') %
                    {'stdout': stdout, 'stderr': stderr})

            # Compress file
            tmpfile.seek(0)
            with gzip.GzipFile(fileobj=tmpzipfile, mode='wb') as gz_file:
                shutil.copyfileobj(tmpfile, gz_file)

            tmpzipfile.seek(0)
            return base64.b64encode(tmpzipfile.read())


def check_empty_arg(arg: str, arg_descriptor: str) -> None:
    if not arg.strip():
        raise exc.CommandError(_('%(arg)s cannot be empty or only have blank'
                                 ' spaces') % {'arg': arg_descriptor})


def bool_argument_value(
    arg_name: str,
    bool_str: str,
    strict: bool = True,
    default: bool = False,
) -> bool:
    """Returns the Boolean represented by bool_str.

    Returns the Boolean value for the argument named arg_name. The value is
    represented by the string bool_str. If the string is an invalid Boolean
    string: if strict is True, a CommandError exception is raised; otherwise
    the default value is returned.

    :param arg_name: The name of the argument
    :param bool_str: The string representing a Boolean value
    :param strict: Used if the string is invalid. If True, raises an exception.
        If False, returns the default value.
    :param default: The default value to return if the string is invalid
        and not strict
    :returns: the Boolean value represented by bool_str or the default value
        if bool_str is invalid and strict is False
    :raises CommandError: if bool_str is an invalid Boolean string

    """
    try:
        val = strutils.bool_from_string(bool_str, strict, default)
    except ValueError as e:
        raise exc.CommandError(_("argument %(arg)s: %(err)s.")
                               % {'arg': arg_name, 'err': e})
    return cast(bool, val)


def check_for_invalid_fields(
    fields: list[str] | None,
    valid_fields: list[str],
) -> None:
    """Check for invalid fields.

    :param fields: A list of fields specified by the user.
    :param valid_fields: A list of valid fields.
    :raises CommandError: If invalid fields were specified by the user.
    """
    if not fields:
        return

    invalid_fields = set(fields) - set(valid_fields)
    if invalid_fields:
        raise exc.CommandError(
            _('Invalid field(s) requested: %(invalid)s. Valid fields '
              'are: %(valid)s.') % {'invalid': ', '.join(invalid_fields),
                                    'valid': ', '.join(valid_fields)})


def get_from_stdin(info_desc: str) -> str:
    """Read information from stdin.

    :param info_desc: A string description of the desired information
    :raises: InvalidAttribute if there was a problem reading from stdin
    :returns: the string that was read from stdin
    """
    try:
        info = sys.stdin.read().strip()
    except Exception as e:
        err = _("Cannot get %(desc)s from standard input. Error: %(err)s")
        raise exc.InvalidAttribute(err % {'desc': info_desc, 'err': e})
    return info


def handle_json_or_file_arg(
    json_arg: str,
) -> list[Any] | dict[str, Any]:
    """Attempts to read JSON argument from file or string.

    :param json_arg: May be a file name containing the YAML or JSON, or
        a JSON string.
    :returns: A list or dictionary parsed from JSON.
    :raises: InvalidAttribute if the argument cannot be parsed.
    """

    if os.path.isfile(json_arg):
        try:
            with open(json_arg, 'r') as f:
                # safe_load returns Any; we treat as list | dict
                return yaml.safe_load(f)  # type: ignore[no-any-return]
        except Exception as e:
            err = _("Cannot get JSON/YAML from file '%(file)s'. "
                    "Error: %(err)s") % {'err': e, 'file': json_arg}
            raise exc.InvalidAttribute(err)
    try:
        result: list[Any] | dict[str, Any] = json.loads(json_arg)
    except ValueError as e:
        err = (_("Value '%(string)s' is not a file and cannot be parsed "
                 "as JSON: '%(err)s'") % {'err': e, 'string': json_arg})
        raise exc.InvalidAttribute(err)

    return result


def poll(
    timeout: int | float,
    poll_interval: int | float,
    poll_delay_function: Callable[[int | float], Any] | None,
    timeout_message: str | Callable[[], str],
) -> Iterator[int]:
    if not isinstance(timeout, (int, float)) or timeout < 0:
        raise ValueError(_('Timeout must be a non-negative number'))

    threshold = time.time() + timeout
    poll_delay_function = (time.sleep if poll_delay_function is None
                           else poll_delay_function)
    if not callable(poll_delay_function):
        raise TypeError(_('poll_delay_function must be callable'))

    count = 0
    while not timeout or time.time() < threshold:
        yield count

        poll_delay_function(poll_interval)
        count += 1

    if callable(timeout_message):
        timeout_message = timeout_message()
    raise exc.StateTransitionTimeout(timeout_message)


def handle_json_arg(
    json_arg: str,
    info_desc: str,
) -> list[Any] | dict[str, Any] | None:
    """Read a JSON argument from stdin, file or string.

    :param json_arg: May be a file name containing the JSON, a JSON string, or
        '-' indicating that the argument should be read from standard input.
    :param info_desc: A string description of the desired information
    :returns: A list or dictionary parsed from JSON, or None if json_arg is
        empty (e.g. after reading from stdin with no input).
    :raises: InvalidAttribute if the argument cannot be parsed.
    """
    if json_arg == '-':
        json_arg = get_from_stdin(info_desc)
    if json_arg:
        return handle_json_or_file_arg(json_arg)
    return None


def get_json_data(
    data: bytes,
) -> dict[str, Any] | list[Any] | None:
    """Check if the binary data is JSON and parse it if so.

    :param data: Raw bytes to parse (e.g. response body).
    :returns: Parsed dict or list if valid JSON, otherwise None.
    """
    # We don't want to simply loads() a potentially large binary. Doing so,
    # in my testing, is orders of magnitude (!!) slower than this process.
    for idx in range(len(data)):
        char = data[idx:idx + 1]
        if char.isspace():
            continue
        if char != b'{' and char != b'[':
            return None  # not JSON, at least not JSON we care about
        break  # maybe JSON

    try:
        # loads returns Any; we treat as dict | list
        return json.loads(data)  # type: ignore[no-any-return]
    except ValueError:
        return None


def format_hash(
    data: dict[str, Any] | None,
    prefix: str = "",
) -> str | None:
    if data is None:
        return None

    output = ""
    for s in sorted(data):
        key_str = prefix + "." + s if prefix else s
        if isinstance(data[s], dict):
            # NOTE(dtroyer): Only append the separator chars here, quoting
            #                is completely handled in the terminal case.
            hashed = format_hash(data[s], prefix=key_str)
            output = output + (hashed or "") + ", "
        elif data[s] is not None:
            output = output + key_str + "='" + str(data[s]) + "', "
        else:
            output = output + key_str + "=, "
    return output[:-2]


class HashColumn(columns.FormattableColumn):
    # base returns Sequence; we return str | None
    def human_readable(self) -> str | None:  # type: ignore[override]
        return format_hash(self._value)
