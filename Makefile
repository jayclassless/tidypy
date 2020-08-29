
setup::
	@poetry install

env::
	@poetry self --version
	@poetry version
	@poetry env info
	@poetry show --all

clean::
	@rm -rf dist .coverage.* poetry.lock

clean-full:: clean
	@poetry env remove `poetry run which python`

lint::
	@poetry run tidypy check

test::
	@poetry run coverage run --module py.test
	@poetry run coverage combine
	@poetry run coverage report

build::
	@poetry build

publish::
	@poetry publish

docs::
	@rm -rf docs/build
	@cd docs && make html

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

