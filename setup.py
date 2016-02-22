# encoding=utf8

"""
    Author: lipixun
    Created Time : 四 12/17 17:28:50 2015

    File Name: setup.py
    Description:

"""

import sys
reload(sys)
sys.setdefaultencoding('utf8')

from datetime import datetime

import unifiedrpc

from setuptools import setup, find_packages

requirements = [ x.strip() for x in open('requirements.txt').readlines() ]

# Fix up the version
version = unifiedrpc.__version__
if len(version.split('.')) < 3:
    version = '%s.%s' % (version, datetime.now().strftime('%s'))
    unifiedrpc.setVersion(version)

setup(
    name = 'unifiedrpc',
    version = version,
    author = 'lipixun',
    author_email = 'lipixun@outlook.com',
    url = 'https://github.com/lipixun/pyunified-rpc',
    packages = find_packages(),
    install_requires = requirements,
    description = 'The unified RPC framework',
    long_description = open('README.md').read(),
)

