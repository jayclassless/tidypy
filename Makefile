VENV = .venv
BINDIR = $(if $(wildcard ${VENV}/bin), '${VENV}/bin/', '')


setup::
	@python -m venv ${VENV} || virtualenv ${VENV}
	@${MAKE} install

setup-ci:: install

install::
	@${BINDIR}pip install --upgrade pip
	@${BINDIR}pip install -r requirements.txt
	@${BINDIR}pip install -e .

freeze::
	@${BINDIR}python --version
	@${BINDIR}pip --version
	@${BINDIR}pip freeze

clean::
	@rm -rf dist build .cache .pytest_cache pip-wheel-metadata .coverage.*

clean-full:: clean
	@rm -rf .venv


lint::
	@${BINDIR}tidypy check

test::
	@${BINDIR}coverage run --rcfile=setup.cfg --module py.test
	@${BINDIR}coverage combine --rcfile=setup.cfg
	@${BINDIR}coverage report --rcfile=setup.cfg

test-ci:: test


build:: clean
	@${BINDIR}python setup.py sdist
	@${BINDIR}python setup.py bdist_wheel

docs::
	@rm -rf docs/build
	@cd docs && make html

publish::
	@${BINDIR}twine upload dist/*


NO_ACCESS_FILES = \
	test/project1/data/noaccess.json \
	test/project1/data/noaccess.po \
	test/project1/data/noaccess.pot \
	test/project1/data/noaccess.rst \
	test/project1/data/noaccess.yaml \
	test/project1/project1/noaccess.py

noaccess::
	@for file in ${NO_ACCESS_FILES}; do \
		touch $$file; \
		chmod a-rwx $$file; \
	done;

clean-noaccess::
	@for file in ${NO_ACCESS_FILES}; do \
		rm $$file; \
	done;


build-docker::
	@docker build . --pull --tag=tidypy:latest

lint-docker::
	@docker run --rm --tty --volume=`pwd`:/project tidypy

