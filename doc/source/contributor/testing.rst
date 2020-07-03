.. _testing:

=======
Testing
=======

Python Guideline Enforcement
............................

All code has to pass the pep8 style guideline to merge into OpenStack, to
validate the code against these guidelines you can run::

    $ tox -e pep8

Unit Testing
............

It is strongly encouraged to run the unit tests locally under one or more
test environments prior to submitting a patch. To run all the recommended
environments sequentially and pep8 style guideline run::

    $ tox

You can also selectively pick specific test environments by listing your
chosen environments after a -e flag::

    $ tox -e py3,pep8

.. note::
  Tox sets up virtual environment and installs all necessary dependencies.
  Sharing the environment with devstack testing is not recommended due to
  conflicting configuration with system dependencies.

Functional Testing
..................

Functional testing assumes the existence of the script run_functional.sh in the
python-ironicclient/tools directory. The script run_functional.sh generates
test.conf file. To run functional tests just run ./run_functional.sh.

Also, the test.conf file could be created manually or generated from
environment variables. It assumes the existence of an openstack
cloud installation along with admin credentials. The test.conf file lives in
ironicclient/tests/functional/ directory. To run functional tests in that way
create test.conf manually and run::

    $ tox -e functional

An example test.conf file::

    [functional]
    api_version = 1
    os_auth_url=http://192.168.0.2:5000/v2.0/
    os_username=admin
    os_password=admin
    os_project_name=admin

If you are testing ironic in standalone mode, only the parameters
'auth_strategy', 'os_auth_token' and 'ironic_url' are required;
all others will be ignored.

An example test.conf file for standalone host::

    [functional]
    auth_strategy = noauth
    os_auth_token = fake
    ironic_url = http://10.0.0.2:6385
