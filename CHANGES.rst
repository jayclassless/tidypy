*****************
TidyPy Change Log
*****************

.. contents:: Releases


0.2.0 (2017-11-04)
==================

Enhancements
------------
* Added a ``2to3`` tool.
* All tools that report issues against Python source files can now use the
  ``# noqa`` comment to ignore issues for that specific line.
* Added support for the ``ignore-nosec`` option in the ``bandit`` tool.
* Added the ability for TidyPy configurations to extend from other
  configuration files via the ``extends`` property.
* Upgraded the ``vulture`` tool.
* Upgraded the ``pyflakes`` tool.

Changes
-------
* Changed the ``--no-merge`` and ``--no-progress`` options to the ``check``
  command to ``--disable-merge`` and ``--disable-progress``.
* The ``check`` command will now return ``1`` to the shell if TidyPy finds
  issues.
* No longer overriding ``pycodestyle``'s default max-line-length.

Fixes
-----
* If any tools output directly to stdout or stderr, TidyPy will now capture it
  and report it as a ``tidypy:tool`` issue.
* Fixed crash/hang that occurred when using ``--disable-progress``.


0.1.0 (2017-10-15)
==================

* Initial public release.

