setup::
	@pipenv install --dev
	@find test/project1 -name noaccess.* -exec chmod a-rwx {} \;

lint::
	@tidypy check

test::
	@pytest

build::
	@rm -rf dist build
	@python setup.py sdist
	@python setup.py bdist_wheel

publish::
	@twine upload dist/*

