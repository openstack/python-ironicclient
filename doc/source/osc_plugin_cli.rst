============================================================================
:program:`openstack baremetal` OpenStack Client Command-Line Interface (CLI)
============================================================================

.. program:: openstack baremetal
.. highlight:: bash

Synopsis
========

:program:`openstack [options] baremetal` <command> [command-options]

:program:`openstack help baremetal` <command>


Description
===========

The OpenStack Client plugin interacts with the Bare Metal service
through the ``openstack baremetal`` command line interface (CLI).

To use ``openstack`` CLI, the OpenStackClient should be installed::

    # pip install python-openstackclient

To use the CLI, you must provide your OpenStack username, password,
project, and auth endpoint. You can use configuration options
:option:`--os-username`, :option:`--os-password`, :option:`--os-project-id`
(or :option:`--os-project-name`), and :option:`--os-auth-url`,
or set the corresponding environment variables::

    $ export OS_USERNAME=user
    $ export OS_PASSWORD=password
    $ export OS_PROJECT_NAME=project                         # or OS_PROJECT_ID
    $ export OS_PROJECT_DOMAIN_ID=default
    $ export OS_USER_DOMAIN_ID=default
    $ export OS_IDENTITY_API_VERSION=3
    $ export OS_AUTH_URL=http://auth.example.com:5000/identity

This CLI is provided by python-openstackclient and osc-lib projects:

* https://git.openstack.org/openstack/python-openstackclient
* https://git.openstack.org/openstack/osc-lib


Getting help
============

To get a list of available (sub)commands and options, run::

    $ openstack help baremetal

To get usage and options of a command, run::

    $ openstack help baremetal <sub-command>


Examples
========

Get information about the openstack baremetal node create command::

    $ openstack help baremetal node create

Get a list of available drivers::

    $ openstack baremetal driver list

Enroll a node with "agent_ipmitool" driver::

    $ openstack baremetal node create --driver agent_ipmitool --driver-info ipmi_address=1.2.3.4

Get a list of nodes::

    $ openstack baremetal node list

The baremetal API version can be specified via:

* environment variable OS_BAREMETAL_API_VERSION::

    $ export OS_BAREMETAL_API_VERSION=1.25

* or optional command line argument --os-baremetal-api-version::

    $ openstack baremetal port group list --os-baremetal-api-version 1.25
