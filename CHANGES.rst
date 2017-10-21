*****************
TidyPy Change Log
*****************

.. contents:: Releases


0.2.0 (TBD)
===========

* If any tools output directly to stdout or stderr, TidyPy will now capture it
  and report it as a ``tidypy:tool`` issue.
* Changed the ``--no-merge`` and ``--no-progress`` options to the ``check``
  command to ``--disable-merge`` and ``--disable-progress``.
* All tools that report issues against Python source files can now use the
  ``# noqa`` comment to ignore issues for that specific line.
* Added support for the ``ignore-nosec`` option in the ``bandit`` tool.


0.1.0 (2017-10-15)
==================

* Initial public release.

