Usage
=====

.. program:: nncli

When ``nncli`` is run without any options or arguments an interactive
console GUI will appear. The behavior of this interface is highly
configurable (see: :ref:`configuration`).

In addition to this default behavior, there are several options
available when calling ``nncli`` without a subcommand.

.. option:: --help, -h

Displays a brief decription of the ``nncli`` options and subcommands.

.. option:: --version, -V

Displays the version information.

Also available when calling ``nncli`` by itself is the ``--config``
option, for which see: :ref:`general-options`.

Subcommands
-----------

There are a variety of subcommands available from the command line when
using ``nncli``. The intent is for these subcommands to enable
scripting against your NextCloud Notes database. The subcommands are:

- sync

- list

- export

- dump

- create

- import

- edit

- delete

- (un)favorite

- cat {get,set,rm}

These subcommands and the options available to them are described below.

.. _general-options:

General Subcommand Options
~~~~~~~~~~~~~~~~~~~~~~~~~~

Several ``nncli`` options apply to multiple subcommands. They are:

.. option:: --verbose, -v

Print verbose logging information to ``stdout``

.. option:: --nosync, -n

Operate only on the local notes cache. Do not reach out to the server.

.. option:: --regex, -r

For subcommands that accept a search string, treat the search string as
a regular expression.

.. option:: --key, -k

The ID of the note to operate on. This option is required for many of
the subcommands.

.. option:: --config, -c

Specify the config file to read from. This option is only required to
override the default location (see: :ref:`config-file`).

nncli sync
~~~~~~~~~~

.. program:: nncli sync

Command format: ``nncli sync``

Performs a full, bi-directional sync between the local notes cache and
the NextCloud Notes server. There are no available options for this
subcommand.

- Available options: None

- Arguments: None

nncli list
~~~~~~~~~~

.. program:: nncli list

Command format: ``nncli list [search_string]``

List notes by ID, flags, and title. Flags indicate whether the note has
been modified locally (``X``), and/or if it is marked as a favorite
(``*``).

- Available options:

  - ``--regex, -r`` See :ref:`general-options`

- Arguments:

  - ``search_string`` Optional. A search term used to refine the search.

nncli export
~~~~~~~~~~~~

.. program:: nncli export

Command format: ``nncli export [search_string]``

Exports notes in raw, JSON format. The JSON format is a superset of the
format outlined in the NextCloud Notes API specification with
information added for managing the local notes cache. Note that nncli
still stores all the notes data in the directory specified by
``cfg_db_path``, so for easy backups, it may be easier/quicker to simply
backup this entire directory.

- Available options:

  - :ref:`general-options`

     - ``--regex, -r`` Mutually exclusive with ``--key``

     - ``--key, -k``

- Arguments:

  - ``search_string`` Required if ``--regex`` is specified. A search
    term used to refine the search.

Example:

.. code-block:: sh

   # export a single note by id
   nncli -k somekeyid export

   # export all notes
   nncli export

   # export notes matching search string
   nncli [-r] export some search keywords or regex

nncli dump
~~~~~~~~~~

.. program:: nncli dump

Command format: ``nncli dump [search_string]``

Prints notes to ``stdout``. The printed format is the text of the note
preceeded by a header displaying information about the note title, key,
modified date, category, and flags. Flags indicate whether the note has
been modified locally (``X``), and/or if it is marked as a favorite
(``*``).

- Available options:

  - :ref:`general-options`

     - ``--regex, -r`` Mutually exclusive with ``--key``

     - ``--key, -k``

- Arguments:

  - ``search_string`` Required if ``--regex`` is specified. A search
    term used to refine the search.

nncli create
~~~~~~~~~~~~

.. program:: nncli create

Command format: ``nncli create [-]``

Create a note. Without arguments, this command will open your configured
editor. The note syncs to the server after the editor is closed.

- Available options: None

- Arguments:

  - `-` Optional. If specified, the note content is read from ``stdin``.

Example:

.. code-block:: sh

   # create a new note and open in editor
   nncli create

   # create a new note with contents of stdin
   echo 'hi' | nncli create -

nncli import
~~~~~~~~~~~~

.. program:: nncli import

Command format: ``nncli import [-]``

Import a JSON-formatted note. nncli can import notes from raw json data
(via stdin or editor). Allowed fields are ``content``, ``category``,
``favorite``, and ``modified``.

- Available options: None

- Arguments:

  - ``-`` Optional. If specified, the note content is read from ``stdin``.

Example:

.. code-block:: none

   echo '{"category":"testing","content":"New note!"}' | nncli import -

nncli edit
~~~~~~~~~~

.. program:: nncli edit

Command format: ``nncli -k <key> edit``

Open the note specified by ``<key>`` in the configured editor. The note
syncs to the server after the editor is saved and closed.

- Available options:

  - ``--key, -k`` Required. See :ref:`general-options`

- Arguments: None

nncli delete
~~~~~~~~~~~~

.. program:: nncli delete

Command format: ``nncli -k <key> delete``

Delete the note specified by ``<key>``.

- Available options:

  - ``--key, -k`` Required. See :ref:`general-options`

- Arguments: None

nncli favorite
~~~~~~~~~~~~~~

.. program:: nncli favorite

Command format: ``nncli -k <key> favorite|unfavorite``

Favorite (or unfavorite) the note specified by ``<key>``.

- Available options:

  - ``--key, -k`` Required. See :ref:`general-options`

- Arguments: None

nncli cat
~~~~~~~~~

.. program:: nncli cat

Command format: ``nncli -k <key> cat get|set|rm``

Read or modify a note category from the command line.

- Available options:

  - ``--key, -k`` Required. See :ref:`general-options`

- Arguments:

  - ``get`` Get the note category

  - ``set`` Set the note category

  - ``rm`` Remove the note category

Example:

.. code-block:: sh

   # Retrieve note category (e.g. "category1")
   nncli -k somekeyid cat get
   # Returns "category1"

   # Add a category to a note, overwriting any existing one
   nncli -k somekeyid cat set "category3"
   # Now tagged as "category3"

   # Remove a category from a note
   nncli -k somekeyid cat rm
   # Note now has no category

Console GUI Usage
-----------------

.. index:: single: searching

Searching
~~~~~~~~~

nncli supports two styles of search strings. First is a Google style
search string and second is a Regular Expression.

A Google style search string is a group of tokens (separated by spaces)
with an implied *AND* between each token. This style search is case
insensitive. For example:

.. code-block:: none

   /category:category1 category:category2 word1 "word2 word3" category:category3

Regular expression searching also supports the use of flags (currently
only case-insensitive) by adding a final forward slash followed by the
flags. The following example will do a case-insensitive search for
``something``:

.. code-block:: none

   (regex) /something/i

.. index:: single: modelines

Modelines
~~~~~~~~~

Advanced text editors usually tailor their behavior based on the file
type being edited. For such editors, notes opened through nncli should
be treated as Markdown by default. However, you can change this
on a per-note basis through the use of modelines. In Vim, for instance,
a modeline is a comment line conforming to the pattern below::

   :: vim: ft=rst

Now when you edit this note Vim will automatically load the rst plugin.
