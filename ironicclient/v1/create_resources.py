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

import functools
import json

import jsonschema
import yaml

from ironicclient import exc

_CREATE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "Schema for ironic resources file",
    "type": "object",
    "properties": {
        "chassis": {
            "type": "array",
            "items": {
                "type": "object"
            }
        },
        "nodes": {
            "type": "array",
            "items": {
                "type": "object"
            }
        }
    },
    "additionalProperties": False
}


def create_resources(client, filenames):
    """Create resources using their JSON or YAML descriptions.

    :param client: an instance of ironic client;
    :param filenames: a list of filenames containing JSON or YAML resources
        definitions.
    :raises: ClientException if any operation during files processing/resource
        creation fails.
    """
    errors = []
    resources = []
    for resource_file in filenames:
        try:
            resource = load_from_file(resource_file)
            jsonschema.validate(resource, _CREATE_SCHEMA)
            resources.append(resource)
        except (exc.ClientException, jsonschema.ValidationError) as e:
            errors.append(e)
    if errors:
        raise exc.ClientException('While validating the resources file(s), the'
                                  ' following error(s) were encountered:\n%s' %
                                  '\n'.join(str(e) for e in errors))
    for r in resources:
        errors.extend(create_chassis(client, r.get('chassis', [])))
        errors.extend(create_nodes(client, r.get('nodes', [])))
    if errors:
        raise exc.ClientException('During resources creation, the following '
                                  'error(s) were encountered:\n%s' %
                                  '\n'.join(str(e) for e in errors))


def load_from_file(filename):
    """Deserialize JSON or YAML from file.

    :param filename: name of the file containing JSON or YAML.
    :returns: a dictionary deserialized from JSON or YAML.
    :raises: ClientException if the file can not be loaded or if its contents
        is not a valid JSON or YAML, or if the file extension is not supported.
    """
    try:
        with open(filename) as f:
            if filename.endswith('.yaml'):
                return yaml.safe_load(f)
            elif filename.endswith('.json'):
                return json.load(f)
            else:
                # The file is neither .json, nor .yaml, raise an exception
                raise exc.ClientException(
                    'Cannot process file "%(file)s" - it must have .json or '
                    '.yaml extension.' % {'file': filename})
    except IOError as e:
        raise exc.ClientException('Cannot read file "%(file)s" due to '
                                  'error: %(err)s' %
                                  {'err': e, 'file': filename})
    except (ValueError, yaml.YAMLError) as e:
        # json.load raises only ValueError
        raise exc.ClientException('File "%(file)s" is invalid due to error: '
                                  '%(err)s' % {'err': e, 'file': filename})


def create_single_handler(resource_type):
    """Catch errors of the creation of a single resource.

    This decorator appends an error (which is an instance of some client
    exception class) to the return value of the create_method, changing the
    return value from just UUID to (UUID, error), and does some exception
    handling.

    :param resource_type: string value, the type of the resource being created,
        e.g. 'node', used purely for exception messages.
    """

    def outer_wrapper(create_method):
        @functools.wraps(create_method)
        def wrapper(client, **params):
            uuid = None
            error = None
            try:
                uuid = create_method(client, **params)
            except exc.InvalidAttribute as e:
                error = exc.InvalidAttribute(
                    'Cannot create the %(resource)s with attributes '
                    '%(params)s. One or more attributes are invalid: %(err)s' %
                    {'params': params, 'resource': resource_type, 'err': e}
                )
            except Exception as e:
                error = exc.ClientException(
                    'Unable to create the %(resource)s with the specified '
                    'attributes: %(params)s. The error is: %(error)s' %
                    {'error': e, 'resource': resource_type, 'params': params})
            return uuid, error
        return wrapper
    return outer_wrapper


@create_single_handler('node')
def create_single_node(client, **params):
    """Call the client to create a node.

    :param client: ironic client instance.
    :param params: dictionary to be POSTed to /nodes endpoint, excluding
        "ports" and "portgroups" keys.
    :returns: UUID of the created node or None in case of exception, and an
        exception, if it appears.
    :raises: InvalidAttribute, if some parameters passed to client's
        create_method are invalid.
    :raises: ClientException, if the creation of the node fails.
    """
    params.pop('ports', None)
    params.pop('portgroups', None)
    traits = params.pop('traits', None)
    ret = client.node.create(**params)
    if traits:
        client.node.set_traits(ret.uuid, traits)
    return ret.uuid


@create_single_handler('port')
def create_single_port(client, **params):
    """Call the client to create a port.

    :param client: ironic client instance.
    :param params: dictionary to be POSTed to /ports endpoint.
    :returns: UUID of the created port or None in case of exception, and an
        exception, if it appears.
    :raises: InvalidAttribute, if some parameters passed to client's
        create_method are invalid.
    :raises: ClientException, if the creation of the port fails.
    """
    ret = client.port.create(**params)
    return ret.uuid


@create_single_handler('port group')
def create_single_portgroup(client, **params):
    """Call the client to create a port group.

    :param client: ironic client instance.
    :param params: dictionary to be POSTed to /portgroups endpoint, excluding
        "ports" key.
    :returns: UUID of the created port group or None in case of exception, and
        an exception, if it appears.
    :raises: InvalidAttribute, if some parameters passed to client's
        create_method are invalid.
    :raises: ClientException, if the creation of the portgroup fails.
    """
    params.pop('ports', None)
    ret = client.portgroup.create(**params)
    return ret.uuid


@create_single_handler('chassis')
def create_single_chassis(client, **params):
    """Call the client to create a chassis.

    :param client: ironic client instance.
    :param params: dictionary to be POSTed to /chassis endpoint, excluding
        "nodes" key.
    :returns: UUID of the created chassis or None in case of exception, and an
        exception, if it appears.
    :raises: InvalidAttribute, if some parameters passed to client's
        create_method are invalid.
    :raises: ClientException, if the creation of the chassis fails.
    """
    params.pop('nodes', None)
    ret = client.chassis.create(**params)
    return ret.uuid


def create_ports(client, port_list, node_uuid, portgroup_uuid=None):
    """Create ports from dictionaries.

    :param client: ironic client instance.
    :param port_list: list of dictionaries to be POSTed to /ports
        endpoint.
    :param node_uuid: UUID of a node the ports should be associated with.
    :param portgroup_uuid: UUID of a port group the ports should be associated
        with, if they are its members.
    :returns: array of exceptions encountered during creation.
    """
    errors = []
    for port in port_list:
        port_node_uuid = port.get('node_uuid')
        if port_node_uuid and port_node_uuid != node_uuid:
            errors.append(exc.ClientException(
                'Cannot create a port as part of node %(node_uuid)s '
                'because the port %(port)s has a different node UUID '
                'specified.',
                {'node_uuid': node_uuid,
                 'port': port}))
            continue
        port['node_uuid'] = node_uuid
        if portgroup_uuid:
            port_portgroup_uuid = port.get('portgroup_uuid')
            if port_portgroup_uuid and port_portgroup_uuid != portgroup_uuid:
                errors.append(exc.ClientException(
                    'Cannot create a port as part of port group '
                    '%(portgroup_uuid)s because the port %(port)s has a '
                    'different port group UUID specified.',
                    {'portgroup_uuid': portgroup_uuid,
                     'port': port}))
                continue
            port['portgroup_uuid'] = portgroup_uuid
        port_uuid, error = create_single_port(client, **port)
        if error:
            errors.append(error)
    return errors


def create_portgroups(client, portgroup_list, node_uuid):
    """Create port groups from dictionaries.

    :param client: ironic client instance.
    :param portgroup_list: list of dictionaries to be POSTed to /portgroups
        endpoint, if some of them contain "ports" key, its content is POSTed
        separately to /ports endpoint.
    :param node_uuid: UUID of a node the port groups should be associated with.
    :returns: array of exceptions encountered during creation.
    """
    errors = []
    for portgroup in portgroup_list:
        portgroup_node_uuid = portgroup.get('node_uuid')
        if portgroup_node_uuid and portgroup_node_uuid != node_uuid:
            errors.append(exc.ClientException(
                'Cannot create a port group as part of node %(node_uuid)s '
                'because the port group %(portgroup)s has a different node '
                'UUID specified.',
                {'node_uuid': node_uuid,
                 'portgroup': portgroup}))
            continue
        portgroup['node_uuid'] = node_uuid
        portgroup_uuid, error = create_single_portgroup(client, **portgroup)
        if error:
            errors.append(error)
        ports = portgroup.get('ports')
        # Port group UUID == None means that port group creation failed, don't
        # create the ports inside it
        if ports is not None and portgroup_uuid is not None:
            errors.extend(create_ports(client, ports, node_uuid,
                                       portgroup_uuid=portgroup_uuid))
    return errors


def create_nodes(client, node_list, chassis_uuid=None):
    """Create nodes from dictionaries.

    :param client: ironic client instance.
    :param node_list: list of dictionaries to be POSTed to /nodes
        endpoint, if some of them contain "ports" key, its content is POSTed
        separately to /ports endpoint.
    :param chassis_uuid: UUID of a chassis the nodes should be associated with.
    :returns: array of exceptions encountered during creation.
    """
    errors = []
    for node in node_list:
        if chassis_uuid is not None:
            node_chassis_uuid = node.get('chassis_uuid')
            if node_chassis_uuid and node_chassis_uuid != chassis_uuid:
                errors.append(exc.ClientException(
                    'Cannot create a node as part of chassis %(chassis_uuid)s '
                    'because the node %(node)s has a different chassis UUID '
                    'specified.' %
                    {'chassis_uuid': chassis_uuid,
                     'node': node}))
                continue
            node['chassis_uuid'] = chassis_uuid
        node_uuid, error = create_single_node(client, **node)
        if error:
            errors.append(error)
        ports = node.get('ports')
        portgroups = node.get('portgroups')
        # Node UUID == None means that node creation failed, don't
        # create the port(group)s inside it
        if node_uuid is not None:
            if portgroups is not None:
                errors.extend(
                    create_portgroups(client, portgroups, node_uuid))
            if ports is not None:
                errors.extend(create_ports(client, ports, node_uuid))
    return errors


def create_chassis(client, chassis_list):
    """Create chassis from dictionaries.

    :param client: ironic client instance.
    :param chassis_list: list of dictionaries to be POSTed to /chassis
        endpoint, if some of them contain "nodes" key, its content is POSTed
        separately to /nodes endpoint.
    :returns: array of exceptions encountered during creation.
    """
    errors = []
    for chassis in chassis_list:
        chassis_uuid, error = create_single_chassis(client, **chassis)
        if error:
            errors.append(error)
        nodes = chassis.get('nodes')
        # Chassis UUID == None means that chassis creation failed, don't
        # create the nodes inside it
        if nodes is not None and chassis_uuid is not None:
            errors.extend(create_nodes(client, nodes,
                                       chassis_uuid=chassis_uuid))
    return errors
