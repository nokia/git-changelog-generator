README
======

**GCG** stands for *Git Changelog Generator*.

To see available options, run as:

.. code:: bash

    $ gcg.py --help

TODO: Not much to see here.. yet. Improve the README.

Build
=====

Prerequisites:
--------------

Base:

- python2.7
- pip
- virtualenv

To build RPMs:

- rpmbuild

To build DEB packages you need to set up Debian toolchain, which is not
in scope of this README.

Build
-----

We recommend you build this package using ``virtualenv``.

To set it up, run for example:

::

    virtualenv venv
    source venv/bin/activate

To test & build a binary Python package, use:

.. code:: bash

    python setup.py test bdist

RPM:

.. code:: bash

    python setup.py test bdist_rpm

DEB:

.. code:: bash

    python setup.py --command-packages=stdeb.command bdist_deb

Existing templates
------------------

The ``gcg`` module of the application comes with some default Jinja2
templates to render the changelog information.

Current implementation does not yet support using non-standard output
templates. The anticipated design would to be pass a template directory
as a command-line argument, that's still to be determined though.

DEB template
~~~~~~~~~~~~

Based on https://www.debian.org/doc/debian-policy/#s-dpkgchangelog

RPM template
~~~~~~~~~~~~

Based on one of allowed formats listed at
https://fedoraproject.org/wiki/Packaging:Guidelines?rd=Packaging/Guidelines#Changelogs
