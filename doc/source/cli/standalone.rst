=====================================================
``baremetal`` Standalone Command-Line Interface (CLI)
=====================================================

.. program:: baremetal
.. highlight:: bash

Synopsis
========

:program:`baremetal [options]` <command> [command-options]

:program:`baremetal help` <command>


Description
===========

The standalone ``baremetal`` tool allows interacting with the Bare Metal
service without installing the OpenStack Client tool as in
:doc:`osc_plugin_cli`.

The standalone tool is mostly identical to its OSC counterpart, with two
exceptions:

#. No need to prefix commands with ``openstack``.
#. No authentication is assumed by default.

Check the :doc:`OSC CLI reference </cli/osc/v1/index>` for a list of available
commands.

Standalone usage
----------------

To use the CLI with a standalone bare metal service, you need to provide an
endpoint to connect to. It can be done in three ways:

#. Provide an explicit ``--os-endpoint`` argument, e.g.:

   .. code-block:: bash

    $ baremetal --os-endpoint https://ironic.host:6385 node list

#. Set the corresponding environment variable, e.g.:

   .. code-block:: bash

    $ export OS_ENDPOINT=https://ironic.host:6385
    $ baremetal node list

#. Populate a clouds.yaml_ file, setting ``baremetal_endpoint_override``, e.g.:

   .. code-block:: bash

    $ cat ~/.config/openstack/clouds.yaml
    clouds:
      ironic:
        auth_type: none
        baremetal_endpoint_override: http://127.0.0.1:6385
    $ export OS_CLOUD=ironic
    $ baremetal node list

.. _clouds.yaml: https://docs.openstack.org/openstacksdk/latest/user/guides/connect_from_config.html

Usage with OpenStack
--------------------

The standalone CLI can also be used with the Bare Metal service installed as
part of OpenStack. See :ref:`osc-auth` for information on the required input.
