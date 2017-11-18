*****************
TidyPy Change Log
*****************

.. contents:: Releases


0.4.0 (TBD)
===========




0.3.0 (2017-11-18)
==================

**Enhancements**

* Added ``ignore-directives`` and ``load-directives`` options to the
  ``rstlint`` tool to help deal with non-standard ReST directives.
* Added support for the ``extension-pkg-whitelist`` option to the ``pylint``
  tool.
* Added ``install-vcs`` and ``remove-vcs`` commands to install/remove
  pre-commit hooks into the VCS of a project that will execute TidyPy.
  Currently supports both Git and Mercurial.

**Changes**

* Changed the ``merge_issues`` and ``ignore_missing_extends`` options to
  ``merge-issues`` and ``ignore-missing-extends`` for naming consistency.
* Replaced the ``radon`` tool with the traditional ``mccabe`` tool.

**Fixes**

* Fixed issue that caused TidyPy to spin out of control if you used CTRL-C to
  kill it while it was executing tools.
* Fixed issue where ``pylint``'s ``duplicate-code`` issue was reported only
  against one file, and it was usually the wrong file. TidyPy will now report
  an issue against each file identified with the duplicate code.
* Numerous fixes to support running TidyPy on Windows.


0.2.0 (2017-11-04)
==================

**Enhancements**

* Added a ``2to3`` tool.
* All tools that report issues against Python source files can now use the
  ``# noqa`` comment to ignore issues for that specific line.
* Added support for the ``ignore-nosec`` option in the ``bandit`` tool.
* Added the ability for TidyPy configurations to extend from other
  configuration files via the ``extends`` property.
* Upgraded the ``vulture`` tool.
* Upgraded the ``pyflakes`` tool.

**Changes**

* Changed the ``--no-merge`` and ``--no-progress`` options to the ``check``
  command to ``--disable-merge`` and ``--disable-progress``.
* The ``check`` command will now return ``1`` to the shell if TidyPy finds
  issues.
* No longer overriding ``pycodestyle``'s default max-line-length.

**Fixes**

* If any tools output directly to stdout or stderr, TidyPy will now capture it
  and report it as a ``tidypy:tool`` issue.
* Fixed crash/hang that occurred when using ``--disable-progress``.


0.1.0 (2017-10-15)
==================

* Initial public release.

