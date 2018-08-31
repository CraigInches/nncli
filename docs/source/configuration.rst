.. _configuration:

Configuration
=============

The current NextCloud Notes API does not support oauth authentication so
your NextCloud Notes account password must be stored someplace
accessible to nncli. Use of the ``cfg_nn_password_eval`` option is
recommended (see below).

.. _config-file:

Configuration File
------------------

nncli pulls in configuration from the ``config`` file located in the
standard location for your platform. At the very least, the following
example ``config`` will get you going (using your account information):

.. code-block:: ini

   [nncli]
   cfg_nn_username = lebowski@thedude.com
   cfg_nn_password = nihilist
   cfg_nn_host     = nextcloud.thedude.com

Start nncli with no arguments which starts the console GUI mode. nncli
will begin to sync your existing notes and you'll see log messages at
the bottom of the console. You can view these log messages at any time
by pressing the ``l`` key.

View the help by pressing ``h``. Here you'll see all the keybinds and
configuration items. The middle column shows the config name that can be
used in your ``config`` to override the default setting.

See example configuration file below for more notes.

.. code-block:: ini

   [nncli]
   cfg_nn_username = lebowski@thedude.com
   cfg_nn_password = nihilist
   cfg_nn_host     = nextcloud.thedude.com

   ; as an alternate to cfg_nn_password you could use the following config item
   ; any shell command can be used; its stdout is used for the password
   ; trailing newlines are stripped for ease of use
   ; note: if both password config are given, cfg_nn_password will be used
   cfg_nn_password_eval = gpg --quiet --for-your-eyes-only --no-tty --decrypt ~/.nncli-pass.gpg

   ; see http://urwid.org/manual/userinput.html for examples of more key
   ; combinations
   kb_edit_note = space
   kb_page_down = ctrl f

   ; note that values must not be quoted
   clr_note_focus_bg = light blue

   ; if this editor config value is not provided, the $EDITOR env var will be
   ; used instead
   ; warning: if neither $EDITOR or cfg_editor is set, it will be impossible to
   ; edit notes
   cfg_editor = nvim

   ; alternatively, {fname} and/or {line} are substituted with the filename and
   ; current line number in nncli's pager.
   ; If {fname} isn't supplied, the filename is simply appended.
   ; examples:
   cfg_editor = nvim {fname} +{line}
   cfg_editor = nano +{line}

   ; this is also supported for the pager:
   cfg_pager = less -c +{line} -N {fname}

.. index:: single: configuration; gui titles

Note Title Format
-----------------

The format of each line in the note list is driven by the
``cfg_format_note_title`` config item. Various formatting tags are
supported for dynamically building the title string. Each of these
formatting tags supports a width specifier (decimal) and a left
justification (-) like that supported by printf::

   %F - flags (fixed 5 char width)
        X - needs sync
        * - favorited
   %T - category
   %D - date
   %N - title

The default note title format pushes the note category to the far right of
the terminal and left justifies the note title after the date and
flags:

.. code-block:: ini

   cfg_format_note_title = '[%D] %F %-N %T'

Note that the ``%D`` date format is further defined by the strftime format
specified in ``cfg_format_strftime``.

.. index:: single: configuration; gui colors

Colors
------

nncli utilizes the Python Urwid_ module to implement the console user
interface.

At this time, nncli does not yet support 256-color terminals and is
limited to just 16-colors. Color names that can be specified in the
``config`` file are listed here_.

.. _Urwid: http://urwid.org
.. _here: http://urwid.org/manual/displayattributes.html#standard-foreground-colors
