#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys, os
import django_throttling

setup(
    name='django-throttling',
    version=django_throttling.get_version(),
    description="Basic throttling app for Django",
    long_description=open('README.rst', 'r').read(),
    keywords='django, throttling',
    author='Igor',
    author_email='lilo.panic@gmail.com',
    url='http://github.com/night-crawler/django-throttling',
    license='MIT',
    package_dir={'django_throttling': 'django_throttling'},
    include_package_data=True,
    packages=find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",        
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Page Counters",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        "Topic :: Security",        
        "Topic :: Utilities",
    ]
)