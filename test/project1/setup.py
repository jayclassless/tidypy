from setuptools import setup, find_packages

version = '0.0foo'

setup(
    name='project1',
    version=version,
    description="Test",
    long_description='.. fake::\n:something:foo bar',
    classifiers=[],
    keywords='',
    author='',
    author_email='',
    url='',
    license='',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    install_requires=[
    ],
    entry_points="""
    """,
)

