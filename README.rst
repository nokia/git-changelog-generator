README
======

**GCG** stands for *Git Changelog Generator*.


Rationale
---------

Keeping a reasonable changelog is an invaluable asset for everyone who tries
to track progress of a project or figure out whether their issue
has or has not be fixed.

In Linux world, such changelogs are often embedded into packages, for
example RPM has an optional section in the *spec* file (``%changelog``)
and Debian versioning goes even further - it explicitly **depends**
on a proper version information inside the changelog to build
and maintain the package(s).

There are good reasons why the log is ideally maintained manually,
you can read all about it at https://keepachangelog.com/en/

That said, it's not all black and white. A couple of questions:

- what if you spend a lot of work making sure your commit descriptions
  are telling the story; should this work be disregarded and repeated
  in the changelog?
- what if the reality kicks in, project members keep forgetting to update
  the changelog (or it is "yet another menial task")?
- what if you need to maintain the log in multiple formats?

If advice from keepchangelog.com doesn't address your questions,
you don't want to tie yourself to a specific Git manager (like  Github,
Gitlab, Bitbucket) and as a project you're committed to maintain sensible
Git commit descriptions - gcg might be just the fit for you.

Releases
========


At this point, *gcg* official packages are created and maintained only for
Python; they're available via PyPI index: https://pypi.org/project/gcg

That said, unofficial packages for most common distribution formats can
be obtained from the following repositories:

* RPM: https://bintray.com/weakcamel/yum-oss
* DEB: https://bintray.com/weakcamel/deb-oss

To use the DEB packages from those repositories, you need to install
the [Bintray GPG key](https://bintray.com/user/downloadSubjectPublicKey?username=weakcamel);
otherwise your `apt-get update` will fail.

For example::

    # either of:
    curl -qL https://bintray.com/user/downloadSubjectPublicKey?username=bintray | sudo apt-key add -

    curl -qL https://bintray.com/user/downloadSubjectPublicKey?username=weakcamel | sudo apt-key add -


PIP
---

Only tagged packages are uploaded to https://pypi.org index,
test versions will be made available under
https://test.pypi.org/manage/project/gcg/releases/

TravisCI builds try to ensure the version (``version.txt``) is unique for
each CI build by adding ``.dev<TRAVIS_BUILD_NUMBER>`` suffix
for development versions of the package.

.. tip::

    See also: https://packaging.python.org/tutorials/installing-packages/






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


Usage
=====


To see available options, run as:

.. code:: bash

    $ gcg --help

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
