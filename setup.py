#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ast
import re

from setuptools import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('teamsupport/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.rst') as changelog_file:
    changelog = changelog_file.read()

requirements = [
    'demands',
    'lxml',
    'property-caching',
    'querylist',
]

test_requirements = [
    'mock',
]

setup(
    name='teamsupport',
    version=version,
    description='Python library for interfacing with the TeamSupport API',
    long_description=readme + '\n\n' + changelog,
    author='Yola Engineers',
    author_email='engineers@yola.com',
    url='https://github.com/yola/teamsupport-python',
    packages=[
        'teamsupport',
    ],
    include_package_data=True,
    install_requires=requirements,
    license='MIT',
    zip_safe=False,
    classifiers=[
        'Development Status:: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
