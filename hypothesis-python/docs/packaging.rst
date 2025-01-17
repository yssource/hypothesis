====================
Packaging Guidelines
====================

Downstream packagers often want to package Hypothesis. Here are some guidelines.

The primary guideline is this: If you are not prepared to keep up with the Hypothesis release schedule,
don't. You will annoy me and are doing your users a disservice.

Hypothesis has a very frequent release schedule. It's rare that it goes a week without a release,
and there are often multiple releases in a given week.

If you *are* prepared to keep up with this schedule, you might find the rest of this document useful.

----------------
Release tarballs
----------------

These are available from :gh-link:`the GitHub releases page <releases>`. The
tarballs on PyPI are intended for installation from a Python tool such as :pypi:`pip` and should not
be considered complete releases. Requests to include additional files in them will not be granted. Their absence
is not a bug.


------------
Dependencies
------------

~~~~~~~~~~~~~~~
Python versions
~~~~~~~~~~~~~~~

Hypothesis is designed to work with a range of Python versions.  We always support
`all versisions of CPython with upstream support <https://devguide.python.org/#status-of-python-branches>`_,
and plan to drop Python 2 at EOL in 2020.  We also support the latest versions of PyPy
for Python 3, and for Python 2 until the CPython 2 EOL.

If you feel the need to have separate Python 3 and Python 2 packages you can, but Hypothesis works unmodified
on either.

~~~~~~~~~~~~~~~~~~~~~~
Other Python libraries
~~~~~~~~~~~~~~~~~~~~~~

Hypothesis has *mandatory* dependencies on the following libraries:

* :pypi:`attrs`
* :pypi:`enum34` is required on Python 2.7

Hypothesis has *optional* dependencies on the following libraries:

.. literalinclude:: ../setup.py
   :prepend: extras_require = {
   :start-after: extras = {
   :end-before: }
   :append: }

The way this works when installing Hypothesis normally is that these features become available if the relevant
library is installed.

Specifically for :pypi:`pytest`, our plugin supports versions of pytest which
have been out of upstream support for some time.  Hypothesis tests can still
be executed by even older versions of pytest - you just won't have the plugin
to provide automatic marks, helpful usage warnings, and per-test statistics.

------------------
Testing Hypothesis
------------------

If you want to test Hypothesis as part of your packaging you will probably not want to use the mechanisms
Hypothesis itself uses for running its tests, because it has a lot of logic for installing and testing against
different versions of Python.

The tests must be run with fairly recent tooling; check the :gh-file:`requirements/`
directory for details.

The organisation of the tests is described in the :gh-file:`hypothesis-python/tests/README.rst`.

--------
Examples
--------

* `arch linux <https://www.archlinux.org/packages/community/any/python-hypothesis/>`_
* `fedora <https://src.fedoraproject.org/rpms/python-hypothesis>`_
* `gentoo <https://packages.gentoo.org/packages/dev-python/hypothesis>`_
