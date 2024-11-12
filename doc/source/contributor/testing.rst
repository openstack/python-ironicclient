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

Functional tests have been removed as of November 2024.
