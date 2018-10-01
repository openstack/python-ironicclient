==================================
Python bindings for the Ironic API
==================================

Team and repository tags
------------------------

.. image:: https://governance.openstack.org/tc/badges/python-ironicclient.svg
    :target: https://governance.openstack.org/tc/reference/tags/index.html

Overview
--------

This is a client for the OpenStack `Bare Metal API
<https://developer.openstack.org/api-ref/baremetal/>`_. It provides:

* a Python API: the ``ironicclient`` module, and
* two command-line interfaces: ``openstack baremetal`` and ``ironic``
  (deprecated, please use ``openstack baremetal``).

Development takes place via the usual OpenStack processes as outlined in the
`developer guide <https://docs.openstack.org/infra/manual/developers.html>`_.
The master repository is on `git.openstack.org
<https://git.openstack.org/cgit/openstack/python-ironicclient>`_.

``python-ironicclient`` is licensed under the Apache License, Version 2.0,
like the rest of OpenStack.

.. contents:: Contents:
   :local:

Useful Links
------------

* Documentation: https://docs.openstack.org/python-ironicclient/latest/
* Source: https://git.openstack.org/cgit/openstack/python-ironicclient
* Bugs: https://storyboard.openstack.org/#!/project/959
* Release notes: https://docs.openstack.org/releasenotes/python-ironicclient/

Python API
----------

Quick-start Example::

    >>> from ironicclient import client
    >>>
    >>> kwargs = {'os_auth_token': '3bcc3d3a03f44e3d8377f9247b0ad155',
    >>>           'ironic_url': 'http://ironic.example.org:6385/'}
    >>> ironic = client.get_client(1, **kwargs)


``openstack baremetal`` CLI
---------------------------

The ``openstack baremetal`` command line interface is available when the bare
metal plugin (included in this package) is used with the `OpenStackClient
<https://docs.openstack.org/python-openstackclient/latest/>`_.

There are two ways to install the OpenStackClient (python-openstackclient)
package:

* along with this python-ironicclient package::

  # pip install python-ironicclient[cli]

* directly::

  # pip install python-openstackclient

An example of creating a basic node with the ``ipmi`` driver::

    $ openstack baremetal node create --driver ipmi

An example of creating a port on a node::

    $ openstack baremetal port create --node <UUID> AA:BB:CC:DD:EE:FF

An example of updating driver properties for a node::

    $ openstack baremetal node set --driver-info ipmi_address=<IPaddress> <UUID or name>

For more information about the ``openstack baremetal`` command and
the subcommands available, run::

    $ openstack help baremetal

``ironic`` CLI (deprecated)
---------------------------

This is deprecated and will be removed in the S* release. Please use the
``openstack baremetal`` CLI instead.

This package will install the ``ironic`` command line interface that you
can use to interact with the ``ironic`` API.

In order to use the ``ironic`` CLI you'll need to provide your OpenStack
tenant, username, password and authentication endpoint. You can do this with
the ``--os-tenant-name``, ``--os-username``, ``--os-password`` and
``--os-auth-url`` parameters, though it may be easier to set them
as environment variables::

    $ export OS_PROJECT_NAME=project
    $ export OS_USERNAME=user
    $ export OS_PASSWORD=pass
    $ export OS_AUTH_URL=http://auth.example.com:5000/v2.0

To use a specific Ironic API endpoint::

    $ export IRONIC_URL=http://ironic.example.com:6385

An example of creating a basic node with the ``ipmi`` driver::

    $ ironic node-create -d ipmi

An example of creating a port on a node::

    $ ironic port-create -a AA:BB:CC:DD:EE:FF -n nodeUUID

An example of updating driver properties for a node::

    $ ironic node-update nodeUUID add driver_info/ipmi_address=<IPaddress>
    $ ironic node-update nodeUUID add driver_info/ipmi_username=<username>
    $ ironic node-update nodeUUID add driver_info/ipmi_password=<password>


For more information about the ``ironic`` command and the subcommands
available, run::

    $ ironic help
