nncli
=====

NextCloud Notes Command Line Interface

nncli is a Python application that gives you access to your NextCloud
Notes account via the command line. It's a fork of
[sncli](https://github.com/insanum/sncli) You can access your notes via
a customizable console GUI that implements vi-like keybinds or via a
simple command line interface that you can script.

Notes can be viewed/created/edited in *both an* **online** *and*
**offline** *mode*. All changes are saved to a local cache on disk and
automatically sync'ed when nncli is brought online.

**Pull requests are welcome!**

Check your OS distribution for installation packages.

### Requirements

* [Python 3](http://python.org)
* [pip](https://pip.pypa.io/en/stable/)
* [Urwid](http://urwid.org) Python 3 module
* [Requests](https://requests.readthedocs.org/en/master/) Python 3
  module
* A love for the command line!

### Installation

* Via pip (latest release):
  - `pip3 install nncli`
* Manually:
  - Clone this repository to your hard disk: `git clone
    https://github.com/insanum/nncli.git`
  - Install the requirements `pip3 install -r requirements.txt`
  - Install _nncli_: `python3 setup.py install`

### Features

* Console GUI
  - full two-way sync with NextCloud Notes performed dynamically in the
    background
  - all actions logged and easily reviewed
  - list note titles (configurable format w/ title, date, flags, tags,
    keys, etc)
  - sort notes by date, alpha by title, tags, pinned on top
  - search for notes using a Google style search pattern or Regular
    Expression
  - view note contents and meta data
  - view and restore previous versions of notes
  - pipe note contents to external command
  - create and edit notes (using your editor)
  - edit note tags
  - trash/untrash notes
  - pin/unpin notes
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
  - trash/untrash a note
  - pin/unpin a note
  - view and edit note tags

### HowTo

``` Usage: nncli [OPTIONS] [COMMAND] [COMMAND_ARGS]

 OPTIONS: -h, --help                  - usage help -v, --verbose
 - verbose output -n, --nosync                - don't perform a server
   sync -r, --regex                 - search string is a regular
   expression -k <key>, --key=<key>       - note key -t <title>,
   --title=<title> - title of note for create (cli mode) -c <file>,
   --config=<file>  - config file to read from (defaults to ~/.nnclirc)

 COMMANDS: <none>                      - console gui mode when no
 command specified sync                        - perform a full sync
 with the server list [search_string]        - list notes (refined with
 search string) export [search_string]      - export notes in JSON
 (refined with search string) dump [search_string]        - dump notes
 (refined with search string) create [-]                  - create a
 note ('-' content from stdin) import [-]                  - import a
 note in JSON format ('-' JSON from stdin) export                      -
 export a note in JSON format (specified by <key>) dump
 - dump a note (specified by <key>) edit                        - edit a
   note (specified by <key>) < trash | untrash >         - trash/untrash
   a note (specified by <key>) < pin | unpin >             - pin/unpin a
   - retrieve the tags from a note (specified by <key>) tag set <tags>
   - set the tags for a note (specified by <key>) tag add <tags>
     - add tags to a note (specified by <key>) tag rm <tags>
       - remove tags from a note (specified by <key>) ```

#### Configuration

The current NextCloud Notes API does not support oauth authentication so
your NextCloud Notes account information must live in the configuration
file.  Please be sure to protect this file.

nncli pulls in configuration from the `.nnclirc` file located in your
$HOME directory. At the very least, the following example `.nnclirc`
will get you going (using your account information):

``` [nncli] cfg_sn_username = lebowski@thedude.com cfg_sn_password =
nihilist ```

Start nncli with no arguments which starts the console GUI mode. nncli
with start sync'ing all your existing notes and you'll see log messages
at the bottom of the console. You can view these log messages at any
time by pressing the `l` key.

View the help by pressing `h`. Here you'll see all the keybinds and
configuration items. The middle column shows the config name that can be
used in your `.nnclirc` to override the default setting.

See example configuration file below for more notes.

``` [nncli] cfg_sn_username = lebowski@thedude.com cfg_sn_password =
nihilist

# as an alternate to cfg_sn_password you could use the following config
item # any shell command can be used; its stdout is used for the
password # trailing newlines are stripped for ease of use # note: if
both password config are given, cfg_sn_password will be used
cfg_sn_password_eval = gpg --quiet --for-your-eyes-only --no-tty
--decrypt ~/.nncli-pass.gpg

# see http://urwid.org/manual/userinput.html for examples of more key
combinations kb_edit_note = space kb_page_down = ctrl f

# note that values must not be quoted clr_note_focus_bg = light blue

# if this editor config value is not provided, the $EDITOR env var will
be used instead # warning: if neither $EDITOR or cfg_editor is set, it
will be impossible to edit notes cfg_editor = nvim

# alternatively, {fname} and/or {line} are substituted with the filename
and # current line number in nncli's pager.  # If {fname} isn't
supplied, the filename is simply appended.  # examples: cfg_editor =
nvim {fname} +{line} cfg_editor = nano +{line}

# this is also supported for the pager: cfg_pager = less -c +{line} -N
{fname} ```

#### Note Title Format

The format of each line in the note list is driven by the
`cfg_format_note_title` config item. Various formatting tags are
supported for dynamically building the title string. Each of these
formatting tags supports a width specifier (decimal) and a left
justification (-) like that supported by printf:

``` %F - flags (fixed 5 char width) X - needs sync T - trashed
       * - pinned S - published/shared m - tags %D - date
         %N - title ```

The default note title format pushes the note tags to the far right of
the terminal and left justifies the note title after the date and flags:

``` cfg_format_note_title = '[%D] %F %-N %T' ```

Note that the `%D` date format is further defined by the strftime format
specified in `cfg_format_strftime`.

#### Colors

nncli utilizes the Python [Uwrid](http://urwid.org) module to implement
the console user interface.

At this time, nncli does not yet support 256-color terminals and is
limited to just 16-colors. Color names that can be specified in the
`.nnclirc` file are listed
[here](http://urwid.org/manual/displayattributes.html#standard-foreground-colors).

### Searching

nncli supports two styles of search strings. First is a Google style
search string and second is a Regular Expression.

A Google style search string is a group of tokens (separated by spaces)
with an implied *AND* between each token. This style search is case
insensitive. For example:

``` /tag:tag1 tag:tag2 word1 "word2 word3" tag:tag3 ```

Regular expression searching also supports the use of flags (currently
only case-insensitive) by adding a final forward slash followed by the
flags. The following example will do a case-insensitive search for
`something`:

``` (regex) /something/i ```

### Creating from command line

``` # create a new note and open in editor nncli create

# create a new note with contents of stdin echo 'hi' | nncli create -
```

### Importing

nncli can import notes from raw json data (via stdin or editor). For
example:

``` echo '{"tags":["testing","new"],"content":"New note!"}' | nncli
import - ```

Allowed fields are `content`, `tags`, `systemtags`, `modified`,
`createdate`, and `deleted`.

### Exporting

nncli can export notes as json data to stdout. Example:

``` # export a single note by id nncli -k somekeyid export

# export all notes nncli export

# export notes matching search string nncli [-r] export some search
keywords or regex ```

Note that nncli still stores all the notes data in the directory
specified by `cfg_db_path`, so for easy backups, it may be
easier/quicker to simply backup this entire directory.

### Tags

Note tags can be modified directly from the command line. Example:

``` # Retrieve note tags, as one comma-separated string (e.g.
"tag1,tag2") nncli -k somekeyid tag get                  # Returns
"tag1,tag2"

# Add a tag to a note, if it doesn't already have it nncli -k somekeyid
tag add "tag3"           # Now tagged as "tag1,tag2,tag3"

# Remove a tag from a note nncli -k somekeyid tag rm "tag2"            #
Now tagged as "tag1,tag3"

# Overwrite all of the tags for a note nncli -k somekeyid tag set
"tag2,tag4"      # Now tagged as "tag2,tag4" ```

Note that in SimpleNote, tags are case-insensitive, so "TAG2", "tag2",
and "tAg2" are interpreted as the same and will all be converted to
lowercase.


### Tricks

I personally store a lot of my notes in
[Votl/VimOutliner](https://github.com/insanum/votl) format. Specific to
Vim, I put a modeline at the end of these notes (note that Emacs also
supports modelines):

``` ; vim:ft=votl ```

Now when I edit this note Vim will automatically load the votl plugin.
Lots of possibilities here...

### Thanks

This application pulls in and uses the
[simplenote.py](https://github.com/mrtazz/simplenote.py) module by
[mrtazz](https://github.com/mrtazz) and the
[notes_db.py](https://github.com/cpbotha/nvpy/blob/master/nvpy/notes_db.py)
module from [nvpy](https://github.com/cpbotha/nvpy) by
[cpbotha](https://github.com/cpbotha).

