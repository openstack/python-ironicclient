.. _api_v1:

=======================
ironicclient Python API
=======================

The ironicclient python API lets you access ironic, the OpenStack
Bare Metal Provisioning Service.

For example, to manipulate nodes, you interact with an
:py:class:`ironicclient.v1.node.Node` object.
You obtain access to nodes via attributes of the
:py:class:`ironicclient.v1.client.Client` object.

Usage
=====

Get a Client object
-------------------
First, create an :py:class:`ironicclient.v1.client.Client` instance by passing
your credentials to :py:meth:`ironicclient.client.get_client()`. By default,
the Bare Metal Provisioning system is configured so that only administrators
(users with 'admin' role) have access.

.. note::

   Explicit instantiation of :py:class:`ironicclient.v1.client.Client` may
   cause errors since it doesn't verify provided arguments, using
   :py:meth:`ironicclient.client.get_client()` is preferred way to get client
   object.

There are two different sets of credentials that can be used::

   * ironic endpoint and auth token
   * Identity Service (keystone) credentials

Using ironic endpoint and auth token
....................................

An auth token and the ironic endpoint can be used to authenticate::

      * os_auth_token: authentication token (from Identity Service)
      * ironic_url: ironic API endpoint, eg http://ironic.example.org:6385/v1

To create the client, you can use the API like so::

   >>> from ironicclient import client
   >>>
   >>> kwargs = {'os_auth_token': '3bcc3d3a03f44e3d8377f9247b0ad155',
   >>>           'ironic_url': 'http://ironic.example.org:6385/'}
   >>> ironic = client.get_client(1, **kwargs)

Using Identity Service (keystone) credentials
.............................................

These Identity Service credentials can be used to authenticate::

   * os_username: name of user
   * os_password: user's password
   * os_auth_url: Identity Service endpoint for authorization
   * insecure: Boolean. If True, does not perform X.509 certificate
     validation when establishing SSL connection with identity
     service. default: False (optional)
   * os_tenant_{name|id}: name or ID of tenant

Also the following parameters are required when using the Identity API v3::

    * os_user_domain_name: name of a domain the user belongs to,
      usually 'default'
    * os_project_domain_name: name of a domain the project belongs to,
      usually 'default'

To create a client, you can use the API like so::

   >>> from ironicclient import client
   >>>
   >>> kwargs = {'os_username': 'name',
   >>>           'os_password': 'password',
   >>>           'os_auth_url': 'http://keystone.example.org:5000/',
   >>>           'os_project_name': 'project'}
   >>> ironic = client.get_client(1, **kwargs)

Perform ironic operations
-------------------------

Once you have an :py:class:`ironicclient.v1.client.Client`, you can perform
various tasks::

   >>> ironic.driver.list()  # list of drivers
   >>> ironic.node.list()  # list of nodes
   >>> ironic.node.get(node_uuid)  # information about a particular node

When the Client needs to propagate an exception, it will usually raise an
instance subclassed from
:py:class:`ironicclient.common.apiclient.exceptions.ClientException`.

Refer to the modules themselves, for more details.

ironicclient Modules
====================

* :ref:`modindex`
