setup::
	@pipenv install --dev --skip-lock

lint::
	@pipenv run tidypy check

test::
	@pipenv run coverage run --rcfile=setup.cfg --module py.test
	@pipenv run coverage report --rcfile=setup.cfg

ci:: test
	@pipenv run coveralls --rcfile=setup.cfg

build::
	@rm -rf dist build
	@python setup.py sdist
	@python setup.py bdist_wheel

publish::
	@twine upload dist/*

