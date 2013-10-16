#!/usr/bin/env python

"""
The MIT License (MIT)

Copyright (c) 2013 Sam Rudge (sam@codesam.co.uk)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from setuptools import setup, find_packages
import sys, os
 
version = '1.0.2'

setup(name='dnsyo',
    version=version,
    author='Sam Rudge',
    author_email='sam@codesam.co.uk',
    description='Query over 1500 global DNS servers and colate their results. Track the propagation of your domains around the world.',
    url='https://github.com/samarudge/dnsyo',
    packages=['dnsyo'],
    include_package_data=False,
    zip_safe=True,
    license='https://raw.github.com/samarudge/dnsyo/master/LICENCE.txt',
    classifiers=[
            "Environment :: Console",
            "Intended Audience :: Developers",
            "Intended Audience :: System Administrators",
            "License :: OSI Approved :: MIT License",
            "Topic :: Internet :: Name Service (DNS)"
            ],
    install_requires=['PyYAML==3.10', 'dnspython==1.11.1', 'requests==2.0.0'],
    entry_points="""
[console_scripts]
dnsyo = dnsyo.cli:run
"""
    )