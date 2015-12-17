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

import unifiedrpc

from setuptools import setup, find_packages

requirements = [ x.strip() for x in open('requirements.txt').readlines() ]

setup(
    name = 'unifiedrpc',
    version = unifiedrpc.__version__,
    author = 'lipixun',
    author_email = 'lipixun@outlook.com',
    url = 'https://github.com/lipixun/pyunified-rpc',
    packages = find_packages(),
    install_requires = requirements,
    license = 'LICENSE',
    description = 'The unified RPC framework',
    long_description = open('README.md').read(),
    keywords = [ 'python', 'rpc', 'web', 'restful' ],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ]
)

