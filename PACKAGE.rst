How to make a package and to publish it to PyPI
===============================================

Prerequisites
-------------

Install `setuptools`, `wheel`, `twine` and `gitchangelog`

.. code-block:: console

   $ pip install setuptools wheel twine gitchangelog -U

Optional: install `keyring` to store credential

.. code-block:: console

   $ pip install keyring

   $ keyring set https://test.pypi.org/legacy/ ricard

   $ keyring set https://upload.pypi.org/legacy/ ricard


Automated script
================

The `make_release.py` script allows to automate the publishing process.
Simply answer to the questions.

.. code-block:: console

     $ make_release.py


Manual steps
============

Bump version
------------

Edit file `my_django_tweaks/__init__.py` and set the version value.

Then create a tag with the same name:

.. code-block:: console

    $ git tag "1.0.0"

Make changelog
--------------

.. code-block:: console

    $ gitchangelog > CHANGELOG.rst
    $ git commit CHANGELOG.rst -m "Update changelog for 1.0.0"

Making package
--------------

.. code-block:: console

   $ python setup.py sdist bdist_wheel

Publish to testing PyPI server (optional)
-----------------------------------------

If you need to make some test, it's preferable to publish the package on PyPI test server

.. code-block:: console

   $ twine upload --repository-url https://test.pypi.org/legacy/ dist/*

Publish to PyPI server
-----------------------------------------

.. code-block:: console

   $ twine upload dist/*

Push to master
--------------

.. code-block:: console

    $ git push origin master
    $ git push origin "1.0.0"
