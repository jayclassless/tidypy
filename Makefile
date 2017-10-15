setup::
	@pipenv install --dev --skip-lock
	@find test/project1 -name noaccess.* -exec chmod a-rwx {} \;

lint::
	@pipenv run tidypy check

test::
	@pipenv run pytest

build::
	@rm -rf dist build
	@python setup.py sdist
	@python setup.py bdist_wheel

publish::
	@twine upload dist/*

