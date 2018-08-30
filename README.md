nncli
=====

![GitHub](https://img.shields.io/github/license/djmoch/nncli.svg)
[![PyPI](https://img.shields.io/pypi/v/nncli.svg)](https://pypi.org/project/nncli/)

NextCloud Notes Command Line Interface

nncli is a Python application that gives you access to your NextCloud
Notes account via the command line. It's a "hard" fork of
[sncli](https://github.com/insanum/sncli). You can access your notes via
a customizable console GUI that implements vi-like keybinds or via a
simple command line interface that you can script.

Notes can be viewed/created/edited in *both an* **online** *and*
**offline** *mode*. All changes are saved to a local cache on disk and
automatically sync'ed when nncli is brought online.

**Pull requests are welcome!**

Check your OS distribution for installation packages.

### Requirements

* [Python 3](http://python.org)
* [Urwid](http://urwid.org) Python 3 module
* [Requests](https://requests.readthedocs.org/en/master/) Python 3
  module
* A love for the command line!

### Installation

* Via pip (latest release):
  - `pip3 install nncli`
* Manually:
  - Clone this repository to your hard disk: `git clone
    https://github.com/djmoch/nncli.git`
  - Install _nncli_: `python3 setup.py install`
* Development:
  - Clone the repo
  - Install Pipenv: `pip install pipenv`
  - Stand up development environment: `pipenv install --dev`

### Features

* Console GUI
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
* Command Line (scripting)
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

### HowTo

```
Usage:
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
```

#### Configuration

The current NextCloud Notes API does not support oauth authentication so
your NextCloud Notes account password must be stored someplace
accessible to nncli. Use of the `cfg_nn_password_eval` option is
recommended (see below).

nncli pulls in configuration from the `config` file located in the
standard location for your platform. At the very least, the following
example `config` will get you going (using your account information):

```
[nncli]
cfg_nn_username = lebowski@thedude.com
cfg_nn_password = nihilist
cfg_nn_host     = nextcloud.thedude.com
```

Start nncli with no arguments which starts the console GUI mode. nncli
will begin to sync your existing notes and you'll see log messages at
the bottom of the console. You can view these log messages at any time
by pressing the `l` key.

View the help by pressing `h`. Here you'll see all the keybinds and
configuration items. The middle column shows the config name that can be
used in your `config` to override the default setting.

See example configuration file below for more notes.

```
[nncli]
cfg_nn_username = lebowski@thedude.com
cfg_nn_password = nihilist
cfg_nn_host     = nextcloud.thedude.com

# as an alternate to cfg_nn_password you could use the following config item
# any shell command can be used; its stdout is used for the password
# trailing newlines are stripped for ease of use
# note: if both password config are given, cfg_nn_password will be used
cfg_nn_password_eval = gpg --quiet --for-your-eyes-only --no-tty --decrypt ~/.nncli-pass.gpg

# see http://urwid.org/manual/userinput.html for examples of more key
# combinations
kb_edit_note = space
kb_page_down = ctrl f

# note that values must not be quoted
clr_note_focus_bg = light blue

# if this editor config value is not provided, the $EDITOR env var will be
# used instead
# warning: if neither $EDITOR or cfg_editor is set, it will be impossible to
# edit notes
cfg_editor = nvim

# alternatively, {fname} and/or {line} are substituted with the filename and
# current line number in nncli's pager.
# If {fname} isn't supplied, the filename is simply appended.
# examples:
cfg_editor = nvim {fname} +{line}
cfg_editor = nano +{line}

# this is also supported for the pager:
cfg_pager = less -c +{line} -N {fname}
```

#### Note Title Format

The format of each line in the note list is driven by the
`cfg_format_note_title` config item. Various formatting tags are
supported for dynamically building the title string. Each of these
formatting tags supports a width specifier (decimal) and a left
justification (-) like that supported by printf:

```
%F - flags (fixed 5 char width)
     X - needs sync
     * - favorited
%T - category
%D - date
%N - title
```

The default note title format pushes the note category to the far right of
the terminal and left justifies the note title after the date and flags:

``` cfg_format_note_title = '[%D] %F %-N %T' ```

Note that the `%D` date format is further defined by the strftime format
specified in `cfg_format_strftime`.

#### Colors

nncli utilizes the Python [Uwrid](http://urwid.org) module to implement
the console user interface.

At this time, nncli does not yet support 256-color terminals and is
limited to just 16-colors. Color names that can be specified in the
`config` file are listed
[here](http://urwid.org/manual/displayattributes.html#standard-foreground-colors).

### Searching

nncli supports two styles of search strings. First is a Google style
search string and second is a Regular Expression.

A Google style search string is a group of tokens (separated by spaces)
with an implied *AND* between each token. This style search is case
insensitive. For example:

`/category:category1 category:category2 word1 "word2 word3" category:category3`

Regular expression searching also supports the use of flags (currently
only case-insensitive) by adding a final forward slash followed by the
flags. The following example will do a case-insensitive search for
`something`:

`(regex) /something/i`

### Creating from command line

```
# create a new note and open in editor
nncli create

# create a new note with contents of stdin
echo 'hi' | nncli create -
```

### Importing

nncli can import notes from raw json data (via stdin or editor). For
example:

`echo '{"category":"testing","content":"New note!"}' | nncli import - `

Allowed fields are `content`, `category`, `favorite`, and `modified`

### Exporting

nncli can export notes as json data to stdout. Example:

```
# export a single note by id
nncli -k somekeyid export

# export all notes
nncli export

# export notes matching search string
nncli [-r] export some search keywords or regex
```

Note that nncli still stores all the notes data in the directory
specified by `cfg_db_path`, so for easy backups, it may be
easier/quicker to simply backup this entire directory.

### Category

Note category can be modified directly from the command line. Example:

```
# Retrieve note category (e.g. "category1")
nncli -k somekeyid cat get
# Returns "category1"

# Add a category to a note, overwriting any existing one
nncli -k somekeyid cat set "category3"
# Now tagged as "category3"

# Remove a category from a note
nncli -k somekeyid cat rm
# Note now has no category
```
### Tricks

Advanced text editors usually tailor their behavior based on the file
type being edited. For such editors, notes opened through nncli should
be treated as Markdown by default. However, you can change this
on a per-note basis through the use of modelines. In Vim, for instance,
a modeline is a comment line conforming to the pattern below.

``` ; vim:ft=votl ```

Now when I edit this note Vim will automatically load the votl plugin.
Lots of possibilities here...

### Thanks

nncli is a fork of [sncli](https://github.com/insanum/sncli) by
[insanum](https://github.com/insanum). This application further pulls in
and uses modified versions of the
[simplenote.py](https://github.com/mrtazz/simplenote.py) module by
[mrtazz](https://github.com/mrtazz) and the
[notes_db.py](https://github.com/cpbotha/nvpy/blob/master/nvpy/notes_db.py)
module from [nvpy](https://github.com/cpbotha/nvpy) by
[cpbotha](https://github.com/cpbotha).
