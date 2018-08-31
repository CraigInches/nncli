Usage
=====

.. index:: single: usage

::

    nncli [OPTIONS] [COMMAND] [COMMAND_ARGS]

    OPTIONS:
     -h, --help                  - usage help
     -v, --verbose               - verbose output
     -n, --nosync                - don't perform a server sync
     -r, --regex                 - search string is a regular expression
     -k <key>, --key=<key>       - note key
     -t <title>, --title=<title> - title of note for create (cli mode)
     -c <file>, --config=<file>  - config file to read from
     --version                   - version information

    COMMANDS:
     <none>                      - console gui mode when no command specified
     sync                        - perform a full sync with the server
     list [search_string]        - list notes (refined with search string)
     export [search_string]      - export notes in JSON (refined with search string)
     dump [search_string]        - dump notes (refined with search string)
     create [-]                  - create a note ('-' content from stdin)
     import [-]                  - import a note in JSON format ('-' JSON from stdin)
     export                      - export a note in JSON format (specified by <key>)
     dump                        - dump a note (specified by <key>)
     edit                        - edit a note (specified by <key>)
     delete                      - delete a note (specified by <key>)
     < favorite | unfavorite >   - favorite/unfavorite a note (specified by <key>)
     cat get                     - retrieve the category from a note (specified by <key>)
     cat set <category>          - set the category for a note (specified by <key>)
     cat rm                      - remove category from a note (specified by <key>)

.. index:: single: searching

Searching
---------

nncli supports two styles of search strings. First is a Google style
search string and second is a Regular Expression.

A Google style search string is a group of tokens (separated by spaces)
with an implied *AND* between each token. This style search is case
insensitive. For example::

   /category:category1 category:category2 word1 "word2 word3" category:category3

Regular expression searching also supports the use of flags (currently
only case-insensitive) by adding a final forward slash followed by the
flags. The following example will do a case-insensitive search for
``something``::

   (regex) /something/i

.. index:: single: command line; creating

Creating from command line
--------------------------

::
   # create a new note and open in editor
   nncli create

   # create a new note with contents of stdin
   echo 'hi' | nncli create -

.. index:: single: command line; importing

Importing
---------

nncli can import notes from raw json data (via stdin or editor). For
example::

   echo '{"category":"testing","content":"New note!"}' | nncli import -

Allowed fields are ``content``, ``category``, ``favorite``, and ``modified``

.. index:: single: command line; exporting

Exporting
---------

nncli can export notes as json data to stdout. Example::

   # export a single note by id
   nncli -k somekeyid export

   # export all notes
   nncli export

   # export notes matching search string
   nncli [-r] export some search keywords or regex

Note that nncli still stores all the notes data in the directory
specified by ``cfg_db_path``, so for easy backups, it may be
easier/quicker to simply backup this entire directory.

.. index:: single: command line; categories

Categories
----------

Note category can be modified directly from the command line. Example::

   # Retrieve note category (e.g. "category1")
   nncli -k somekeyid cat get
   # Returns "category1"

   # Add a category to a note, overwriting any existing one
   nncli -k somekeyid cat set "category3"
   # Now tagged as "category3"

   # Remove a category from a note
   nncli -k somekeyid cat rm
   # Note now has no category

.. index:: single: tricks

Tricks
------

Advanced text editors usually tailor their behavior based on the file
type being edited. For such editors, notes opened through nncli should
be treated as Markdown by default. However, you can change this
on a per-note basis through the use of modelines. In Vim, for instance,
a modeline is a comment line conforming to the pattern below::

   :: vim: ft=rst

Now when you edit this note Vim will automatically load the rst plugin.
