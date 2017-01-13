==============================================
:program:`ironic` Command-Line Interface (CLI)
==============================================

.. program:: ironic
.. highlight:: bash

SYNOPSIS
========

:program:`ironic` [options] <command> [command-options]

:program:`ironic help`

:program:`ironic help` <command>


DESCRIPTION
===========

The :program:`ironic` command-line interface (CLI) interacts with the
OpenStack Bare Metal Service (Ironic).

In order to use the CLI, you must provide your OpenStack username, password,
project (historically called tenant), and auth endpoint. You can use
configuration options :option:`--os-username`, :option:`--os-password`,
:option:`--os-tenant-id` (or :option:`--os-tenant-name`),
and :option:`--os-auth-url`, or set the corresponding
environment variables::

    $ export OS_USERNAME=user
    $ export OS_PASSWORD=password
    $ export OS_PROJECT_ID=b363706f891f48019483f8bd6503c54b  # or OS_PROJECT_NAME
    $ export OS_PROJECT_NAME=project                         # or OS_PROJECT_ID
    $ export OS_AUTH_URL=http://auth.example.com:5000/v2.0

The command-line tool will attempt to reauthenticate using the provided
credentials for every request. You can override this behavior by manually
supplying an auth token using :option:`--ironic-url` and
:option:`--os-auth-token`, or by setting the corresponding environment
variables::

    $ export IRONIC_URL=http://ironic.example.org:6385/
    $ export OS_AUTH_TOKEN=3bcc3d3a03f44e3d8377f9247b0ad155

Since Keystone can return multiple regions in the Service Catalog, you can
specify the one you want with :option:`--os-region-name` or set the following
environment variable. (It defaults to the first in the list returned.)
::

    export OS_REGION_NAME=region

Ironic CLI supports bash completion. The command-line tool can automatically
fill partially typed commands. To use this feature, source the below file
(available at
https://git.openstack.org/cgit/openstack/python-ironicclient/tree/tools/ironic.bash_completion)
to your terminal and then bash completion should work::

    $ source ironic.bash_completion

To avoid doing this every time, add this to your ``.bashrc`` or copy the
ironic.bash_completion file to the default bash completion scripts directory
on your linux distribution.

OPTIONS
=======

To get a list of available (sub)commands and options, run::

    $ ironic help

To get usage and options of a command, run::

    $ ironic help <command>


EXAMPLES
========

Get information about the node-create command::

    $ ironic help node-create

Get a list of available drivers::

    $ ironic driver-list

Enroll a node with "fake" deploy driver and "ipmitool" power driver::

    $ ironic node-create -d fake_ipmitool -i ipmi_address=1.2.3.4

Get a list of nodes::

    $ ironic node-list
