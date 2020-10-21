===================================================
Creating the Bare Metal service resources from file
===================================================

It is possible to create a set of resources using their descriptions in JSON
or YAML format. It can be done in one of two ways:

1. Using OpenStackClient bare metal plugin CLI's command ``openstack baremetal
   create``::

    $ openstack -h baremetal create
    usage: openstack baremetal create [-h] <file> [<file> ...]

    Create resources from files

    positional arguments:
      <file>      File (.yaml or .json) containing descriptions of the
                  resources to create. Can be specified multiple times.

2. Programmatically using the Python API:

   .. autofunction:: ironicclient.v1.create_resources.create_resources
      :noindex:

File containing Resource Descriptions
=====================================

The resources to be created can be described either in JSON or YAML. A file
ending with ``.json`` is assumed to contain valid JSON, and a file ending with
``.yaml`` is assumed to contain valid YAML. Specifying a file with any other
extension leads to an error.

The resources that can be created are chassis, nodes, port groups and ports.
A chassis can contain nodes (and resources of nodes) definitions nested under
``"nodes"`` key. A node can contain port groups definitions nested under
``"portgroups"``, and ports definitions under ``"ports"`` keys. Ports can be
also nested under port groups in ``"ports"`` key.

The schema used to validate the supplied data is the following::

    {
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

More detailed description of the creation process can be seen in the following
sections.

Examples
========

Here is an example of the JSON file that can be passed to the ``create``
command::

    {
        "chassis": [
            {
                "description": "chassis 3 in row 23",
                "nodes": [
                    {
                        "name": "node-3",
                        "driver": "ipmi",
                        "portgroups": [
                            {
                                "name": "switch.cz7882.ports.1-2",
                                "ports": [
                                    {
                                        "address": "ff:00:00:00:00:00"
                                    },
                                    {
                                        "address": "ff:00:00:00:00:01"
                                    }
                                ]
                            }
                        ],
                        "ports": [
                            {
                                "address": "00:00:00:00:00:02"
                            },
                            {
                                "address": "00:00:00:00:00:03"
                            }
                        ],
                        "driver_info": {
                            "ipmi_address": "192.168.1.23",
                            "ipmi_username": "BmcUsername",
                            "ipmi_password": "BmcPassword",
                        }
                    },
                    {
                        "name": "node-4",
                        "driver": "ipmi",
                        "ports": [
                            {
                                "address": "00:00:00:00:00:04"
                            },
                            {
                                "address": "00:00:00:00:00:01"
                            }
                        ]
                    }
                ]
            }
        ],
        "nodes": [
            {
                "name": "node-5",
                "driver": "ipmi",
                "chassis_uuid": "74d93e6e-7384-4994-a614-fd7b399b0785",
                "ports": [
                    {
                        "address": "00:00:00:00:00:00"
                    }
                ]
            },
            {
                "name": "node-6",
                "driver": "ipmi"
            }
        ]
    }

Creation Process
================

#. The client deserializes the files' contents and validates that the top-level
   dictionary in each of them contains only "chassis" and/or "nodes" keys,
   and their values are lists. The creation process is aborted if any failure
   is encountered in this stage. The rest of the validation is done by the
   ironic-api service.

#. Each resource is created via issuing a POST request (with the resource's
   dictionary representation in the body) to the ironic-api service. In the
   case of nested resources (``"nodes"`` key inside chassis, ``"portgroups"``
   key inside nodes, ``"ports"`` key inside nodes or portgroups), the top-level
   resource is created first, followed by the sub-resources. For example, if a
   chassis contains a list of nodes, the chassis will be created first followed
   by the creation of each node. The same is true for ports and port groups
   described within nodes.

#. If a resource could not be created, it does not stop the entire process.
   Any sub-resources of the failed resource will not be created, but otherwise,
   the rest of the resources will be created if possible. Any failed resources
   will be mentioned in the response.
