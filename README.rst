******
TidyPy
******

.. image:: https://img.shields.io/pypi/v/tidypy.svg
   :target: https://pypi.org/project/tidypy
.. image:: https://img.shields.io/pypi/l/tidypy.svg
   :target: https://pypi.org/project/tidypy
.. image:: https://readthedocs.org/projects/tidypy/badge/?version=latest
   :target: https://tidypy.readthedocs.io
.. image:: https://github.com/jayclassless/tidypy/workflows/Test/badge.svg
   :target: https://github.com/jayclassless/tidypy/actions
.. image:: https://github.com/jayclassless/tidypy/workflows/Publish%20Docker%20Image/badge.svg
   :target: https://hub.docker.com/r/tidypy/tidypy


.. contents:: Contents


Overview
--------
TidyPy is a tool that encapsulates a number of other static analysis tools and
makes it easy to configure, execute, and review their results.


Features
--------
* It's a consolidated tool for performing static analysis on an entire Python
  project -- not just your ``*.py`` source files. In addition to executing a
  number of different `tools`_ on your code, it can also check your YAML, JSON,
  PO, POT, and RST files.

* Rather than putting yet another specialized configuration file in your
  project, TidyPy uses the ``pyproject.toml`` file defined by `PEP 518`_. All
  options for all the tools TidyPy uses are declared in one place, rather than
  requiring that you configure each tool in a different way.

  .. _PEP 518: https://www.python.org/dev/peps/pep-0518/

* Honors the pseudo-standard ``# noqa`` comment in your Python source to easily
  ignore issues reported by any tool.

* Includes a number of `integrations`_ so you can use it with your favorite
  toolchain.

* Includes a variety of `reporters`_ that allow you to view or use the results
  of TidyPy's analysis in whatever way works best for you.

* Provides a simple API for you to implement your own tool or reporter and
  include it in the analysis of your project.

* Supports both Python 2 and 3, as well as PyPy. Even runs on Windows.


Usage
-----
When TidyPy is installed (``pip install tidypy``), the ``tidypy`` command
should become available in your environment::

    $ tidypy --help
    Usage: tidypy [OPTIONS] COMMAND [ARGS]...

      A tool that executes several static analysis tools upon a Python project
      and aggregates the results.

    Options:
      --version  Show the version and exit.
      --help     Show this message and exit.

    Commands:
      check               Executes the tools upon the project files.
      default-config      Outputs a default configuration that can be used to
                          bootstrap your own configuration file.
      extensions          Outputs a listing of all available TidyPy extensions.
      install-vcs         Installs TidyPy as a pre-commit hook into the specified
                          VCS.
      list-codes          Outputs a listing of all known issue codes that tools
                          may report.
      purge-config-cache  Deletes the cache of configurations retrieved from
                          outside the primary configuration.
      remove-vcs          Removes the TidyPy pre-commit hook from the specified
                          VCS.

To have TidyPy analyze your project, use the ``check`` subcommand::

    $ tidypy check --help
    Usage: tidypy check [OPTIONS] [PATH]

      Executes the tools upon the project files.

      Accepts one argument, which is the path to the base of the Python project.
      If not specified, defaults to the current working directory.

    Options:
      -x, --exclude REGEX             Specifies a regular expression matched
                                      against paths that you want to exclude from
                                      the examination. Can be specified multiple
                                      times. Overrides the expressions specified
                                      in the configuration file.
      -t, --tool [bandit|dlint|eradicate|jsonlint|manifest|mccabe|polint|pycodestyle|pydiatra|pydocstyle|pyflakes|pylint|pyroma|rstlint|secrets|vulture|yamllint]
                                      Specifies the name of a tool to use during
                                      the examination. Can be specified multiple
                                      times. Overrides the configuration file.
      -r, --report [console,csv,custom,json,null,pycodestyle,pylint,pylint-parseable,toml,yaml][:filename]
                                      Specifies the name of a report to execute
                                      after the examination. Can specify an
                                      optional output file name using the form -r
                                      report:filename. If filename is unset, the
                                      report will be written on stdout. Can be
                                      specified multiple times. Overrides the
                                      configuration file.
      -c, --config FILENAME           Specifies the path to the TidyPy
                                      configuration file to use instead of the
                                      configuration found in the project's
                                      pyproject.toml.
      --workers NUM_WORKERS           The number of workers to use to concurrently
                                      execute the tools. Overrides the
                                      configuration file.
      --disable-merge                 Disable the merging of issues from various
                                      tools when TidyPy considers them equivalent.
                                      Overrides the configuration file.
      --disable-progress              Disable the display of the progress bar.
      --disable-noqa                  Disable the ability to ignore issues using
                                      the "# noqa" comment in Python files.
      --disable-config-cache          Disable the use of the cache when retrieving
                                      configurations referenced by the "extends"
                                      option.
      --help                          Show this message and exit.

If you need to generate a skeleton configuration file with the default options,
use the ``default-config`` subcommand::

    $ tidypy default-config --help
    Usage: tidypy default-config [OPTIONS]

      Outputs a default configuration that can be used to bootstrap your own
      configuration file.

    Options:
      --pyproject  Output the config so that it can be used in a pyproject.toml
                   file.
      --help       Show this message and exit.

If you'd like to see a list of the possible issue codes that could be returned,
use the ``list-codes`` subcommand::

    $ tidypy list-codes --help
    Usage: tidypy list-codes [OPTIONS]

      Outputs a listing of all known issue codes that tools may report.

    Options:
      -t, --tool [bandit|dlint|eradicate|jsonlint|manifest|mccabe|polint|pycodestyle|pydiatra|pydocstyle|pyflakes|pylint|pyroma|rstlint|secrets|vulture|yamllint]
                                      Specifies the name of a tool whose codes
                                      should be output. If not specified, defaults
                                      to all tools.
      -f, --format [toml|json|yaml|csv]
                                      Specifies the format in which the tools
                                      should be output. If not specified, defaults
                                      to TOML.
      --help                          Show this message and exit.

If you want to install or remove TidyPy as a pre-commit hook in your project's
VCS, use the ``install-vcs``/``remove-vcs`` subcommands::

    $ tidypy install-vcs --help
    Usage: tidypy install-vcs [OPTIONS] VCS [PATH]

      Installs TidyPy as a pre-commit hook into the specified VCS.

      Accepts two arguments:

        VCS: The version control system to install the hook into. Choose from:
        git, hg

        PATH: The path to the base of the repository to install the hook into.
        If not specified, defaults to the current working directory.

    Options:
      --strict  Whether or not the hook should prevent the commit if TidyPy finds
                issues.
      --help    Show this message and exit.

    $ tidypy remove-vcs --help
    Usage: tidypy remove-vcs [OPTIONS] VCS [PATH]

      Removes the TidyPy pre-commit hook from the specified VCS.

      Accepts two arguments:

        VCS: The version control system to remove the hook from. Choose from:
        git, hg

        PATH: The path to the base of the repository to remove the hook from. If
        not specified, defaults to the current working directory.

    Options:
      --help  Show this message and exit.

If you'd like to enable bash completion for TidyPy, run the following in your
shell (or put it in your bash startup scripts)::

    $ eval "$(_TIDYPY_COMPLETE=source tidypy)"


Docker
------
If you don't want to install TidyPy locally on your system or in your
virtualenv, you can use the `published Docker
<https://hub.docker.com/r/tidypy/tidypy>`_ image::

   $ docker run --rm --tty --volume=`pwd`:/project tidypy/tidypy

The command above will run ``tidypy check`` on the contents of the current
directory. If you want to run it on a different directory, then change the
```pwd``` to whatever path you need (the goal being to mount your project
directory to the container's ``/project`` volume).

Running TidyPy in this manner has a few limitiations, mostly around the fact
that since TidyPy is running in its own, isolated Python environment, tools
like pylint won't be able to introspect the packages your project installed
locally, so it may report false positives around "import-error",
"no-name-in-module", "no-member", etc.

If you want to run a command other than ``check``, just pass that along when
you invoke docker::

   $ docker run --rm --tty --volume=`pwd`:/project tidypy/tidypy tidypy list-codes


Configuration
-------------
TODO


Ignoring Issues
---------------
In addition to ignoring entire files, tools, or specific issue types from tools
via your configuration file, you can also use comments in your Python source
files to ignore issues on specific lines. Some tools have their own built-in
support and notation for doing this:

* `pylint will respect <https://pylint.readthedocs.io/en/latest/faq.html
  #message-control>`_ comments that look like: ``# pylint``
* `bandit will respect <https://github.com/openstack/bandit#exclusions>`_
  comments that look like: ``# nosec``
* `pycodestyle will respect <http://pycodestyle.pycqa.org/en/latest/intro.html
  #error-codes>`_ comments that look like: ``# noqa``
* `pydocstyle will also respect <http://www.pydocstyle.org/en/2.1.1/
  usage.html#in-file-configuration>`_ comments that look like: ``# noqa``
* `detect-secrets will respect <https://github.com/Yelp/detect-secrets
  #inline-whitelisting>`_ comments that look like: ``# pragma: whitelist
  secret``

TidyPy goes beyond these tool-specific flags to implement ``# noqa`` on a
global scale for Python source files. It will ignore issues for lines that have
the ``# noqa`` comment, regardless of what tools raise the issues. If you only
want to ignore a particular type of issue on a line, you can use syntax like
the following::

    # noqa: CODE1,CODE2

Or, if a particular code is used in multiple tools, you can specify the exact
tool in the comment::

    # noqa: pycodestyle:CODE1,pylint:CODE2

Or, if you want to ignore any issue a specific tool raises on a line, you can
specify the tool::

    # noqa: @pycodestyle,@pylint

You can, of course, mix and match all three notations in a single comment if
you need to::

    # noqa: CODE1,pylint:CODE2,@pycodestyle

You can disable TidyPy's NOQA behavior by specifying the ``--disable-noqa``
option on the command line, or by setting the ``noqa`` option to ``false`` in
your configuration file. A caveat, though: currently pycodestyle and pydocstyle
do not respect this option and will always honor any ``# noqa`` comments they
find.


.. _tools:

Included Tools
--------------
Out of the box, TidyPy includes support for a number of tools:

pylint
    `Pylint`_ is a Python source code analyzer which looks for programming
    errors, helps enforcing a coding standard and sniffs for some code smells.

    .. _Pylint: https://github.com/PyCQA/pylint

pycodestyle
    `pycodestyle`_ is a tool to check your Python code against some of the
    style conventions in `PEP 8`_.

    .. _pycodestyle: https://github.com/PyCQA/pycodestyle
    .. _PEP 8: https://www.python.org/dev/peps/pep-0008/

pydocstyle
    `pydocstyle`_ is a static analysis tool for checking compliance with Python
    docstring conventions (e.g., `PEP 257`_).

    .. _pydocstyle: https://github.com/PyCQA/pydocstyle
    .. _PEP 257: https://www.python.org/dev/peps/pep-0257/

pyroma
    `Pyroma`_ tests your project's packaging friendliness.

    .. _Pyroma: https://github.com/regebro/pyroma

vulture
    `Vulture`_ finds unused code in Python programs.

    .. _Vulture: https://github.com/jendrikseipp/vulture

bandit
    `Bandit`_ is a security linter for Python source code.

    .. _Bandit: https://wiki.openstack.org/wiki/Security/Projects/Bandit

eradicate
    `Eradicate`_ finds commented-out code in Python files.

    .. _Eradicate: https://github.com/myint/eradicate

pyflakes
    `Pyflakes`_ is a simple program which checks Python source files for
    errors.

    .. _Pyflakes: https://github.com/PyCQA/pyflakes

mccabe
    Ned Batchelder's script to check the `McCabe`_ cyclomatic complexity of
    Python code.

    .. _McCabe: https://github.com/pycqa/mccabe

jsonlint
    A part of the `demjson`_ package, this tool validates your JSON documents
    for strict conformance to the JSON specification, and to detect potential
    data portability issues.

    .. _demjson: https://github.com/dmeranda/demjson

yamllint
    The `yamllint`_ tool, as its name implies, is a linter for YAML files.

    .. _yamllint: https://github.com/adrienverge/yamllint

rstlint
    The `restructuredtext-lint`_ tool, as its name implies, is a linter for
    reStructuredText files.

    .. _restructuredtext-lint: https://github.com/twolfson/restructuredtext-lint

polint
    A part of the `dennis`_ package, this tool lints PO and POT files for
    problems.

    .. _dennis: https://github.com/willkg/dennis

manifest
    Uses the `check-manifest`_ script to detect discrepancies or problems with
    your project's MANIFEST.in file.

    .. _check-manifest: https://github.com/mgedmin/check-manifest

pydiatra
    `pydiatra`_ is yet another static checker for Python code.

    .. _pydiatra: https://github.com/jwilk/pydiatra

secrets
    The `detect-secrets`_ tool attempts to find secrets (keys, passwords, etc)
    within a code base.

    .. _detect-secrets: https://github.com/Yelp/detect-secrets

dlint
    `Dlint`_ is a tool for encouraging best coding practices and helping ensure
    we're writing secure Python code.

    .. _Dlint: https://github.com/duo-labs/dlint

.. _reporters:

Included Reporters
------------------
TidyPy includes a number of different methods to present and/or export the
results of the analysis of a project. Out of the box, it provides the
following:

console
    The default reporter. Prints a colored report to the console that groups
    issues by the file they were found in.

pylint
    Prints a report to the console that is in the same format as `Pylint`_'s
    default output.

pylint-parseable
    Prints a report to the console that is in roughly the same format as
    `Pylint`_'s "parseable" output.

pycodestyle
    Prints a report to the console that is in the same format as
    `pycodestyle`_'s default output.

json
    Generates a JSON-serialized object that contains the results of the
    analysis.

yaml
    Generates a YAML-serialized object that contains the results of the
    analysis.

toml
    Generates a TOML-serialized object that contains the results of the
    analysis.

csv
    Generates a set of CSV records that contains the results of the analysis.

custom
    Prints ouput to the console that is in the format defined by a template
    string specified in the project configuration. The template string is
    expected to be one allowed by the `str.format()`_ Python method. It will
    receive the following arguments: ``filename``, ``line``, ``character``,
    ``tool``, ``code``, ``message``.

    .. _str.format(): https://docs.python.org/3/library/stdtypes.html#str.format


.. _integrations:

Included Integrations
---------------------
TidyPy includes a handful of plugins/integrations that hook it into other
tools.

pytest
    TidyPy can be run during execution of your `pytest`_ test suite. To enable
    it, you need to specify ``--tidypy`` on the command line when you run
    pytest, or include it as part of the ``addopts`` property in your pytest
    config.

    .. _pytest: https://docs.pytest.org

nose
    TidyPy can be run during execution of your `nose`_ test suite. To enable
    it, you can either specify ``--with-tidypy`` on the command line when you
    run nose, or set the ``with-tidypy`` property to ``1`` in your
    ``setup.cfg``.

    .. _nose: https://nose.readthedocs.io

pbbt
    TidyPy can be included in your `PBBT`_ scripts using the ``tidypy`` test.
    To enable it, you can either specify ``--extend=tidypy.plugin.pbbt`` on the
    command line when you run PBBT, or set the ``extend`` property in your
    ``setup.cfg`` or ``pbbt.yaml`` to ``tidypy.plugin.pbbt``.

    .. _PBBT: https://bitbucket.org/prometheus/pbbt


Extending TidyPy
----------------
A simple interface exists for extending TidyPy to include more and different
tools and reporters. To add a tool, create a class that extends `tidypy.Tool`_,
and in your ``setup.py``, declare an ``entry_point`` for ``tidypy.tools`` that
points to your class::

    entry_points={
        'tidypy.tools': [
            'mycooltool = path.to.model:MyCoolToolClassName',
        ],
    }

To add a reporter, the process is nearly identical, except that you extend
`tidypy.Report`_ and declare an ``entry_point`` for ``tidypy.reports``.

.. _tidypy.Tool: https://tidypy.readthedocs.io/en/stable/api.html#tidypy.Tool
.. _tidypy.Report: https://tidypy.readthedocs.io/en/stable/api.html#tidypy.Report


FAQs
----
Aren't there already tools like this?
    Yup. There's `prospector`_, `pylama`_, `flake8`_, and `ciocheck`_ just to
    name a few. But, as is customary in the world of software development, if
    the wheel isn't as round as you'd like it to be, you must spend countless
    hours to reinvent it. I've tried a number of these tools (and even
    contributed to some), but in the end, I always found something lacking or
    annoying. Thus, TidyPy was born.

    .. _prospector: https://github.com/landscapeio/prospector
    .. _pylama: https://github.com/klen/pylama
    .. _flake8: https://gitlab.com/pycqa/flake8
    .. _ciocheck: https://github.com/ContinuumIO/ciocheck

How do I run TidyPy on a single file?
    The short answer is, you don't (at the moment, anyway). It wasn't designed
    with that use case in mind. TidyPy was built to analyze a whole project,
    and show you everything.

I tried TidyPy out on my project and it reported hundreds/thousands of issues. My ego is now bruised.
    Yea, that happens. The philosophy I chose to follow with this tool is that
    I didn't want it to hide anything from me. I wanted its default behavior to
    execute every tool in its suite using their most obnoxious setting. Then,
    when I can see the full scope of damage, I can then decide to disable
    specific tools or issues via a project-level configuration. I figured if
    someone took the time to implement a check for a particular issue, they
    must think it has some value. If my tooling hides that from me by default,
    then I won't be able to gain any benefits from it.

    In general, I don't recommend starting to use linters or other sorts of
    static analyzers when you think you're "done". You should incorporate them
    into your workflow right at the beginning of a project -- just as you would
    (or should) your unit tests. That way you find things early and learn from
    them (or disable them). It's much less daunting a task to deal with when
    you address them incrementally.


Contributing
------------
Contributions are most welcome. Particularly if they're bug fixes! To hack on
this code, simply clone it, and then run ``make setup``. This will create a
virtualenv with all the tools you'll need. The ``Makefile`` also has a ``test``
target for running the pytest suite, and a ``lint`` target for running TidyPy
on itself.


License
-------
TidyPy is released under the terms of the `MIT License`_.

.. _MIT License: https://opensource.org/licenses/MIT

