nncli is a Python application that gives you access to your NextCloud
Notes account via the command line. It's a "hard" fork of
sncli_. You can access your notes via
a customizable console GUI that implements vi-like keybinds or via a
simple command line interface that you can script.

Notes can be viewed/created/edited in *both an* **online** *and*
**offline** *mode*. All changes are saved to a local cache on disk and
automatically sync'ed when nncli is brought online.

More detailed documentation can be found at the homepage_.

Requirements
------------

- `Python 3`_

- Urwid_ Python 3 module

- Requests_ Python 3 module

- A love for the command line!

Installation
------------

- Via pip (latest release):

  - ``pip3 install nncli``

- Manually:

  - If you don't already have it, install Flit_: ``pip3 install flit``

  - Clone this repository to your hard disk: ``git clone
    https://git.danielmoch.com/nncli.git``

  - Install nncli: ``flit install --deps production``

- Development:

  - Clone the repo

  - Install Pipenv: ``pip3 install pipenv``

  - Stand up development virtualenv: ``pipenv install --dev``

Features
--------

- Console GUI

  - full two-way sync with NextCloud Notes performed dynamically in the
    background

  - all actions logged and easily reviewed

  - list note titles (configurable format w/ title, date, flags, category,
    keys, etc)

  - sort notes by date, alpha by title, category, favorite on top

  - search for notes using a Google style search pattern or Regular
    Expression

  - view note contents and meta data

  - pipe note contents to external command

  - create and edit notes (using your editor)

  - edit note category

  - delete notes

  - favorite/unfavorite notes

  - vi-like keybinds (fully configurable)

  - Colors! (fully configurable)

- Command Line (scripting)

  - force a full two-way sync with NextCloud Notes

  - all actions logged and easily reviewed

  - list note titles and keys

  - search for notes using a Google style search pattern or Regular
    Expression

  - dump note contents

  - create a new note (via stdin or editor)

  - import a note with raw json data (stdin or editor)

  - edit a note (via editor)

  - delete a note

  - favorite/unfavorite a note

  - view and edit note category

Contributing
------------

Pull requests are welcome, preferably via emailed output of ``git
request-pull`` sent to the maintainer (see here_ for more information).
Bug reports should also be directed to the maintainer via email_.

If you aren't hosting a fork anywhere online, you can also send patches
using ``git format-patch`` (again, see `the official documentation`_ ).

Releases
--------

Release tags will always be signed with the maintainer's `PGP key`_
(also available on any public keyserver_).  PGP-signed versions of
release tarballs and pre-built wheel_ packages are available on PyPI_,
with the signature files living alongside the corresponding artifact
(simply append an ``.asc`` extension). Because the maintainers of PyPI
do not consider PGP signatures to be a user-facing feature, the
extension must be added manually in your browser's URL bar in order to
download the signature files.

Acknowledgements
----------------

nncli is a fork of sncli_ by Eric Davis. This application further pulls
in and uses modified versions of the simplenote.py_ module by Daniel
Schauenberg and the notes_db.py module from nvpy_ by Charl P. Botha.

.. _homepage: https://nncli.org
.. _sncli: https://github.com/insanum/sncli
.. _Python 3: http://python.org
.. _Urwid: http://urwid.org
.. _Requests: https://requests.readthedocs.org/en/master
.. _simplenote.py: https://github.com/mrtazz/simplenote.py
.. _nvpy: https://github.com/cpbotha/nvpy
.. _Flit: https://flit.readthedocs.io
.. _here: https://www.git-scm.com/docs/git-request-pull
.. _PGP key: https://www.danielmoch.com/static/gpg.asc
.. _wheel: https://pythonwheels.com/
.. _PyPI: https://pypi.org/project/nncli/
.. _keyserver: https://pgp.mit.edu/pks/lookup?op=get&search=0x323C9F1784BDDD43
.. _email: daniel@danielmoch.com
.. _the official documentation: https://www.git-scm.com/docs/git-format-patch
