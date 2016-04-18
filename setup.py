#!/usr/bin/env python
# -*- coding=UTF-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: setup.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-04-16 22:19:36 (CST)
# Last Update:
#          By:
# Description:
# **************************************************************************
from setuptools import setup


setup(
    name='Flask-Maple',
    version='1.0',
    url='http://honmaple.com',
    license='BSD',
    author='honmaple',
    author_email='xiyang0807@gmail.com',
    description='Very short description',
    long_description=__doc__,
    py_modules=['flask_maple'],
    # if you would be using a package instead use packages instead
    # of py_modules:
    # packages=['flask_sqlite3'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask'
        'Flask-Login'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
