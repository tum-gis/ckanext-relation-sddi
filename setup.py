from setuptools import setup, find_packages
import sys, os

version = '3.0'

setup(
    name='ckanext-relation',
    version=version,
    description="An extension to create, delete and view relationship between datasets",
    long_description='''
    ''',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Mandana Moshrefzadeh',
    author_email='mandana.moshrefzadeh@tum.de',
    url='',
    license='Apache License, Version 2.0',
    packages=find_packages(exclude=['tests']),
    namespace_packages=['ckanext', 'ckanext.relation'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'jinja2',
    ],
    entry_points='''
        [ckan.plugins]
        relation=ckanext.relation.plugin:RelationPlugin
    ''',
        message_extractors={
        'ckanext': [
            ('**.py', 'python', None),
            ('**.js', 'javascript', None),
            ('**/templates/**.html', 'ckan', None),
        ],
    }
)