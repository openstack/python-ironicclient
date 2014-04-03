.. _api_v1:

=======================
ironicclient Python API
=======================

The ironicclient python API lets you access ironic, the OpenStack
Bare Metal Provisioning Service.

For example, to manipulate nodes, you interact with an `ironicclient.v1.node`_ object.
You obtain access to nodes via attributes of the `ironicclient.v1.client.Client`_ object.

Usage
=====

Get a Client object
-------------------
First, create an `ironicclient.v1.client.Client`_ instance by passing your
credentials to `ironicclient.client.get_client()`_. By default, the
Bare Metal Provisioning system is configured so that only administrators
(users with 'admin' role) have access.

There are two different sets of credentials that can be used::

   * ironic endpoint and auth token
   * Identity Service (keystone) credentials

Using ironic endpoint and auth token
.....................................

An auth token and the ironic endpoint can be used to authenticate::

      * os_auth_token: authentication token (from Identity Service)
      * ironic_url: ironic API endpoint, eg http://ironic.example.org:6385/v1

To create the client, you can use the API like so::

   >>> from ironicclient import client
   >>>
   >>> kwargs = {'os_auth_token': '3bcc3d3a03f44e3d8377f9247b0ad155'
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

To create a client, you can use the API like so::

   >>> from ironicclient import client
   >>>
   >>> kwargs = {'os_username': 'name'
   >>>           'os_password': 'password',
   >>>           'os_auth_url': 'http://keystone.example.org:5000/',
   >>>           'os_tenant_name': 'tenant',
   >>> ironic = client.get_client(1, **kwargs)

Perform ironic operations
-------------------------

Once you have an ironic `Client`_, you can perform various tasks::

   >>> ironic.driver.list()  # list of drivers
   >>> ironic.node.list()  # list of nodes
   >>> ironic.node.get(node_uuid)  # information about a particular node

When the `Client`_ needs to propagate an exception, it will usually
raise an instance subclassed from
`ironicclient.exc.BaseException`_ or `ironicclient.exc.ClientException`_.

Refer to the modules themselves, for more details.

ironicclient Modules
====================

.. toctree::
      :maxdepth: 1

    modules <api/autoindex>


.. _ironicclient.v1.node: api/ironicclient.v1.node.html#ironicclient.v1.node.Node
.. _ironicclient.v1.client.Client: api/ironicclient.v1.client.html#ironicclient.v1.client.Client
.. _Client: api/ironicclient.v1.client.html#ironicclient.v1.client.Client
.. _ironicclient.client.get_client(): api/ironicclient.client.html#ironicclient.client.get_client
.. _ironicclient.exc.BaseException: api/ironicclient.exc.html#ironicclient.exc.BaseException
.. _ironicclient.exc.ClientException: api/ironicclient.exc.html#ironicclient.exc.ClientException
