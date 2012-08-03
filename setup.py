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
    version='0.0.1',
    description='An interface to wirecard payment gateway.',
    author='Niels Sandholt Busch',
    author_email='niels.busch@gmail.com',
    url='https://bitbucket.org/resmio/wirecard/',
    long_description=open('README', 'r').read(),
    packages=find_packages(),
    install_requires=['requests>=0.13.3',],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)