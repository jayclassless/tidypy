setup::
	@pipenv install --dev

setup3::
	@pipenv install --dev --three

lint::
	@pipenv run tidypy check

test::
	@pipenv run coverage run --rcfile=setup.cfg --module py.test
	@pipenv run coverage combine --rcfile=setup.cfg
	@pipenv run coverage report --rcfile=setup.cfg

ci:: test
	@pipenv run coveralls --rcfile=setup.cfg

clean::
	@rm -rf dist build .cache .pytest_cache Pipfile.lock

build:: clean
	@pipenv run python setup.py sdist
	@pipenv run python setup.py bdist_wheel

docs::
	@rm -rf docs/build
	@cd docs && pipenv run make html

publish::
	@pipenv run twine upload dist/*


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

