#!/usr/bin/env python3
#
# The MIT License (MIT)
#
# Copyright (c) 2018 Daniel Moch
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

# Copyright (c) 2014 Eric Davis
# Licensed under the MIT License

from setuptools import setup
import nnotes_cli

deps = ['urwid', 'requests']

setup(
      name=nnotes_cli.__productname__,
      description=nnotes_cli.__description__,
      version=nnotes_cli.__version__,
      author=nnotes_cli.__author__,
      author_email=nnotes_cli.__author_email__,
      url=nnotes_cli.__url__,
      license=nnotes_cli.__license__,
      requires=deps,
      install_requires=deps,
      packages=['nnotes_cli'],
      entry_points={
          'console_scripts': [
              'nncli = nnotes_cli.nncli:main'
          ]
      },
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console :: Curses',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
      ],
)
