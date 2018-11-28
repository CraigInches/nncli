Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_ , and this project adheres to
`Semantic Versioning`_.

Unreleased_
-----------

Added
~~~~~

- ``CHANGELOG.rst``

- ``TODO.txt``

- ``clear_ids.py`` contrib script

Changed
~~~~~~~

- References to Github repo changed to point to git.danielmoch.com
  (Github is now a mirror only)

- Fixed exception in ``nncli sync``

v0.3.1_ – 2018-10-30
--------------------

Added
~~~~~

- Partial unit testing for ``nncli.py`` module

Changed
~~~~~~~

- Refactored code (addressing pylint findings)

- Fixed bad exception handling in Python 3.4

Removed
~~~~~~~

v0.3.0_ – 2018-09-07
--------------------

Added
~~~~~

- Documentation as PDF format

Changed
~~~~~~~

- Numerous documentation corrections

v0.2.0_ – 2018-09-03
--------------------

Added
~~~~~

- ``.travis.yml``

- Pytest, tox, et all added to support automated testing

- Both tox and Travis testing back to Python 3.4

v0.1.2_ – 2018-08-30
--------------------

Added
~~~~~

- Support for ``--version`` flag

Changed
~~~~~~~

- requirements.txt replaced with Pipfile{,.lock}

v0.1.1_ – 2018-08-07
--------------------

Added
~~~~~

- README content included in PyPI

Changed
~~~~~~~

- README content and formatting

- Fix ``nncli import`` command

v0.1.0 – 2018-07-31
-------------------

Added
~~~~~

- Hard fork of sncli

.. _Keep a Changelog: https://keepachangelog.com/en/1.0.0/
.. _Semantic Versioning: https://semver.org/spec/v2.0.0.html
.. _Unreleased: https://git.danielmoch.com/nncli.git/diff/?id=master&id2=v0.3.1
.. _v0.3.1: https://git.danielmoch.com/nncli.git/diff/?id=v0.3.1&id2=v0.3.0
.. _v0.3.0: https://git.danielmoch.com/nncli.git/diff/?id=v0.3.0&id2=v0.2.0
.. _v0.2.0: https://git.danielmoch.com/nncli.git/diff/?id=v0.2.0&id2=v0.1.2
.. _v0.1.2: https://git.danielmoch.com/nncli.git/diff/?id=v0.1.2&id2=v0.1.1
.. _v0.1.1: https://git.danielmoch.com/nncli.git/diff/?id=v0.1.1&id2=v0.1.0
