******
TidyPy
******

.. contents:: Contents


Overview
--------
TidyPy is a tool that encapsulates a number of other static analysis tools and
makes it easy to configure, execute, and review their results.


Features
--------
TODO


Usage
-----
When TidyPy is installed, the ``tidypy`` command should become available in
your environment::

    $ tidypy
    Usage: tidypy [OPTIONS] COMMAND [ARGS]...

      A tool that executes several static analysis tools upon a Python project
      and aggregates the results.

    Options:
      --version  Show the version and exit.
      --help     Show this message and exit.

    Commands:
      check           Executes the tools upon the project files.
      default-config  Outputs a default configuration that can be used to
                      bootstrap your own configuration file.
      list-codes      Outputs a listing of all known issue codes that tools may
                      report.

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
      -t, --tool [bandit|eradicate|jsonlint|polint|pycodestyle|pydocstyle|pyflakes|pylint|pyroma|radon|rstlint|vulture|yamllint]
                                      Specifies the name of a tool to use during
                                      the examination. Can be specified multiple
                                      times. Overrides the configuration file.
      -r, --report [console|csv|json|null|pycodestyle|pylint|toml|yaml]
                                      Specifies the name of a report to execute
                                      after the examination. Can be specified
                                      multiple times. Overrides the configuration
                                      file.
      --no-merge                      Disable the merging of issues from various
                                      tools when TidyPy considers them equivalent.
                                      Overrides the configuration file.
      --silence-tool-crashes          If the execution of a tool results in an
                                      unexpected Exception, be quiet about it.
                                      Default behavior is to print an error and
                                      traceback to stderr.
      --threads NUM_THREADS           The number of threads to use to concurrently
                                      execute the tools. Overrides the
                                      configuration file.  [default: 3]
      --no-progress                   Disable the display of the progress bar.
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
      -t, --tool [bandit|eradicate|jsonlint|polint|pycodestyle|pydocstyle|pyflakes|pylint|pyroma|radon|rstlint|vulture|yamllint]
                                      Specifies the name of a tool whose codes
                                      should be output. If not specified, defaults
                                      to all tools.
      -f, --format [toml|json|yaml|csv]
                                      Specifies the format in which the tools
                                      should be output. If not specified, defaults
                                      to TOML.
      --help                          Show this message and exit.

If you'd like to enable bash completion for TidyPy, run the following in your
shell (or put it in your bash startup scripts)::

    $ eval "$(_TIDYPY_COMPLETE=source tidypy)"



Configuration
-------------
TODO


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

radon
    `Radon`_ is a Python tool that computes various metrics from the source code.

    .. _Radon: https://github.com/rubik/radon

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
    A part of the `dennis`_, package this tool lints PO and POT files for
    problems.

    .. _dennis: https://github.com/willkg/dennis


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

setuptools
    TidyPy can be invoked via the ``setup.py`` of your project. Just execute
    ``python setup.py tidypy``.


Extending TidyPy
----------------
A simple interface exists for extending TidyPy to include more and different
tools and reporters. When the API settles down, I'll document it here.


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
this code, simply clone it, make sure you have `Pipenv`_ installed (it's a
great tool, you should use it even if you're not working on this project), and
then run ``make setup``. This will create a virtualenv with all the tools
you'll need. The ``Makefile`` also has a ``test`` target for running the pytest
suite, and a ``lint`` target for running TidyPy on itself.

.. _Pipenv: https://github.com/kennethreitz/pipenv


License
-------
TidyPy is released under the terms of the `MIT License`_.

.. _MIT License: https://opensource.org/licenses/MIT
