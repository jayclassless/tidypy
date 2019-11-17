VENV = .venv

setup::
	@python -m venv ${VENV} || virtualenv ${VENV}
	@${VENV}/bin/pip install --upgrade pip
	@${VENV}/bin/pip install -r requirements.txt
	@${VENV}/bin/pip install -e .

freeze::
	@${VENV}/bin/python --version
	@${VENV}/bin/pip --version
	@${VENV}/bin/pip freeze

lint::
	@${VENV}/bin/tidypy check

test::
	@${VENV}/bin/coverage run --rcfile=setup.cfg --module py.test
	@${VENV}/bin/coverage combine --rcfile=setup.cfg
	@${VENV}/bin/coverage report --rcfile=setup.cfg

ci:: test

clean::
	@rm -rf dist build .cache .pytest_cache pip-wheel-metadata .coverage.*

clean-full:: clean
	@rm -rf .venv

build:: clean
	@${VENV}/bin/python setup.py sdist
	@${VENV}/bin/python setup.py bdist_wheel

docs::
	@rm -rf docs/build
	@cd docs && make html

publish::
	@${VENV}/bin/twine upload dist/*


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

