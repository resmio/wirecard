#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='wirecard',
    version='2.0.1',
    description='An interface to wirecard payment gateway.',
    author='Resmio GmbH',
    author_email='info@resmio.com',
    url='https://github.com/resmio/wirecard/',
    long_description=open('README.md', 'r').read(),
    packages=['wirecard'],
    requires=['requests(>=2.18)'],
    test_suite='tests',
    install_requires=[
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
