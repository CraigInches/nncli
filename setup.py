# -*- encoding: utf-8 -*-

from setuptools import setup
import nnotes_cli

deps = ['urwid', 'requests', 'appdirs']
test_deps = ['pytest', 'pytest-cov', 'pytest-runner', 'pytest-mock']

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
      name=nnotes_cli.__productname__,
      description=nnotes_cli.__description__,
      long_description=long_description,
      long_description_content_type="text/x-rst",
      author=nnotes_cli.__author__,
      author_email=nnotes_cli.__author_email__,
      url=nnotes_cli.__url__,
      license=nnotes_cli.__license__,
      requires=deps,
      install_requires=deps,
      tests_require=test_deps,
      use_scm_version= {'write_to': 'nnotes_cli/version.py'},
      setup_requires=['setuptools_scm'],
      extras_require={'docs': ['sphinx']},
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
