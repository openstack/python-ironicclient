====================================================
``openstack baremetal`` Command-Line Interface (CLI)
====================================================

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

To use the ``openstack`` CLI, the OpenStackClient (python-openstackclient)
package  must be installed. There are two ways to do this:

* along with this python-ironicclient package::

  $ pip install python-ironicclient[cli]

* directly::

  $ pip install python-openstackclient

This CLI is provided by python-openstackclient and osc-lib projects:

* https://opendev.org/openstack/python-openstackclient
* https://opendev.org/openstack/osc-lib

.. _osc-auth:

Authentication
--------------

To use the CLI, you must provide your OpenStack username, password,
project, and auth endpoint. You can use configuration options
``--os-username``, ``--os-password``, ``--os-project-id``
(or ``--os-project-name``), and ``--os-auth-url``,
or set the corresponding environment variables::

    $ export OS_USERNAME=user
    $ export OS_PASSWORD=password
    $ export OS_PROJECT_NAME=project                         # or OS_PROJECT_ID
    $ export OS_PROJECT_DOMAIN_ID=default
    $ export OS_USER_DOMAIN_ID=default
    $ export OS_IDENTITY_API_VERSION=3
    $ export OS_AUTH_URL=http://auth.example.com:5000/identity


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

Enroll a node with the ``ipmi`` driver::

    $ openstack baremetal node create --driver ipmi --driver-info ipmi_address=1.2.3.4

Get a list of nodes::

    $ openstack baremetal node list

The baremetal API version can be specified via:

* environment variable OS_BAREMETAL_API_VERSION::

    $ export OS_BAREMETAL_API_VERSION=1.25

* or optional command line argument --os-baremetal-api-version::

    $ openstack baremetal port group list --os-baremetal-api-version 1.25


Command Reference
=================
.. toctree::
   :glob:
   :maxdepth: 3

   osc/v1/*
