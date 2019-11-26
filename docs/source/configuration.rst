.. _configuration:

Configuration
=============

The current NextCloud Notes API does not support oauth authentication so
your NextCloud Notes account password must be stored someplace
accessible to nncli.

.. index:: single: configuration file

.. _config-file:

Configuration File
------------------

nncli pulls in configuration from the ``config`` file located in the
standard location for your platform:

- Windows: ``%USERPROFILE%\AppData\Local\djmoch\nncli``

- macOS: ``~/Library/Preferences/nncli``

- \*nix: ``$XDG_CONFIG_HOME/nncli/config`` or
  ``$HOME/.config/nncli/config``

The following directives are accepted within the ``config`` file:

.. index:: pair: configuration file; general options

General Options
~~~~~~~~~~~~~~~

.. confval:: cfg_nn_host

   Sets the URL of the NextCloud instance to connect to.

   Required.

.. confval:: cfg_nn_username

   The user name to log in as.

   Required.

.. confval:: cfg_nn_password

   The password to use for log in.

   Optional. Overrides :confval:`cfg_nn_password_eval` if both are
   specified.

   .. note::

      For security reasons, use of the ``cfg_nn_password_eval`` option
      is recommended

.. confval:: cfg_nn_password_eval

   A command to run to retrieve the password. The command should return
   the password on ``stdout``.

   Optional. Required if :confval:`cfg_nn_password` is not specified.

.. confval:: cfg_db_path

   Specifies the path of the local notes cache.

   Optional. Default value:

   - Windows: ``%USERPROFILE%\AppData\Local\djmoch\nncli\Cache``

   - macOS: ``~/Library/Caches/nncli``

   - \*nix: ``$XDG_CACHE_HOME/nncli`` or ``$HOME/.cache/nncli``

.. confval:: cfg_search_categories

   Set to ``yes`` to include categories in searches. Otherwise set to
   ``no``.

   Optional. Default value: ``yes``

.. confval:: cfg_sort_mode

   Sets how notes are sorted in the console GUI. Set to ``date``
   to have them sorted by date (newest on top). Set to ``alpha`` to have
   them sorted alphabetically.

   Optional. Default value: ``date``

.. confval:: cfg_favorite_ontop

   Determines whether notes marked as favorite are sorted on top.

   Optional. Default value: ``yes``

.. confval:: cfg_tabstop

   Sets the width of a tabstop character.

   Optional. Default value: ``4``

.. confval:: cfg_format_strftime

   Sets the format of the note timestamp (``%D``) in the note title. The
   format values are the specified in :py:func:`time.strftime`.

   Optional. Default value: ``%Y/%m/%d``

.. confval:: cfg_format_note_title

   Sets the format of each line in the console GUI note list. Various
   formatting tags are supported for dynamically building the title
   string. Each of these formatting tags supports a width specifier
   (decimal) and a left justification (``-``) like that supported by
   printf:

   .. code-block:: none

      %F - flags (fixed 2 char width)
           X - needs sync
           * - favorited
      %T - category
      %D - date
      %N - title

   The default note title format pushes the note category to the far
   right of the terminal and left justifies the note title after the
   date and flags.

   Optional. Default value: ``[%D] %F %-N %T``

   Note that the ``%D`` date format is further defined by the strftime
   format specified in :confval:`cfg_format_strftime`.

.. confval:: cfg_status_bar

   Sets whether or not the status bar is visible at the top of the
   console GUI.

   Optional. Default value: ``yes``

.. confval:: cfg_editor

   Sets the command to run when opening a note for editing. The special
   values ``{fname}`` and ``{line}`` can be used to specify respectively
   the file name and line number to pass to the command.

   Optional. Default value: ``$VISUAL`` or ``$EDITOR`` if defined in the
   user's environment (preferring ``$VISUAL``), else ``vim {fname} +{line}``.

.. confval:: cfg_pager

   Sets the command to run when opening a note for viewing in an
   external pager.

   Optional. Default value: ``$PAGER`` if defined in the user's
   environment, else ``less -c``.

.. confval:: cfg_max_logs

   Sets the number of log events to display together in the consule GUI
   footer.

   Optional. Default value: ``5``

.. confval:: cfg_log_timeout

   Sets the rate to poll for log events. Unit is seconds.

   Optional. Default value: ``5``

.. confval:: cfg_log_reversed

   Sets whether or not the log is displayed in reverse-chronological
   order.

   Optional. Default value: ``yes``

.. confval:: cfg_tempdir

   Sets a directory path to store temporary files in. ``nncli`` uses
   :func:`tempfile.mkstemp` under the hood, and the most nuanced
   description of how this value is used can be found in the discussion
   of the ``dir`` keyword argument there. Basically you should not
   specify this if you want to use the platform-standard temporary
   folder.

   Optional. Default value: *[blank]*

.. index:: pair: configuration file; keybindings

Keybindings
~~~~~~~~~~~

Keybindings specify the behavior of the console GUI, and are never
required in the ``config`` file. However, they all have default values,
as outlined below. More information on specifying keybindings can be
found in the :ref:`Urwid documentation <urwid:keyboard-input>`.

.. confval:: kb_help

   Press to enter the help screen.

   Default value: ``h``

.. confval:: kb_quit

   Press to exit the console GUI.

   Default value: ``q``

.. confval:: kb_sync

   Press to force a full, bi-directional sync with the server.

   Default value: ``S``

.. confval:: kb_down

   Press to move down one row.

   Default value: ``j``

.. confval:: kb_up

   Press to move one row up.

   Default value: ``k``

.. confval:: kb_page_down

   Press to move one page down.

   Default value: ``space``

.. confval:: kb_page_up

   Press to move one page up.

   Default value: ``b``

.. confval:: kb_half_page_down

   Press to move one half-page down.

   Default value: ``ctrl d``

.. confval:: kb_half_page_up

   Press to move one half-page up.

   Default value: ``ctrl u``

.. confval:: kb_bottom

   Press to move to the last line.

   Default value: ``G``

.. confval:: kb_top

   Press to move to the first line.

   Default value: ``g``

.. confval:: kb_status

   Press to toggle the visibility of the status bar.

   Default value: ``s``

.. confval:: kb_create_note

   Press to create a new note and open in the configured editor (see
   :confval:`cfg_editor`).

   Default value: ``C``

.. confval:: kb_edit_note

   Press to edit the highlighted note in the configured editor (see
   :confval:`cfg_editor`).

   Default value: ``e``

.. confval:: kb_view_note

   Press to view the highlighted note in read-only mode.

   Default value: ``enter``

.. confval:: kb_view_note_ext

   Press to view the highlighted note in the configured pager (see
   :confval:`cfg_pager`).

   Default value: ``meta enter``

.. confval:: kb_view_note_json

   Press to view the raw JSON contents of the highlighted note in
   read-only mode.

   Default value: ``O``

.. confval:: kb_pipe_note

   Press to send the contents of the highlighted note to ``stdin`` of
   another program. A small command window opens at the bottom of the
   screen to enter the desired program.

   Default value: ``|``

.. confval:: kb_view_next_note

   Press to view the contents of the next note in read-only mode.

   Default value: ``J``

.. confval:: kb_view_prev_note

   Press to view the contents of the previous note in read-only mode.

   Default value: ``K``

.. confval:: kb_view_log

   Press to view the log.

   Default value: ``l``

.. confval:: kb_tabstop2

   Press to set the tabstop for the internal pager to a width of two
   characters.

   Default value: ``2``

.. confval:: kb_tabstop4

   Press to set the tabstop for the internal pager to a width of four
   characters.

   Default value: ``4``

.. confval:: kb_tabstop8

   Press to set the tabstop for the internal pager to a width of eight
   characters.

   Default value: ``8``

.. confval:: kb_search_gstyle

   Press to initiate a search of your notes against a Google-style
   search term. A command window will open at the bottom of the screen
   to enter your search term.

   Default value: ``/``

.. confval:: kb_search_regex

   Press to initiate a search of your notes against a regular
   expression. A command window will open at the bottom of the screen to
   enter your search term.

   Default value: ``meta /``

.. confval:: kb_search_prev_gstyle

   Press to initiate a reverse search of your notes against a
   Google-style search term. A command window will open at the bottom of
   the screen to enter your search term.

   Default value: ``?``

.. confval:: kb_search_prev_regex

   Press to initiate a reverse search of your notes against a regular
   expression.  A command window will open at the bottom of the screen
   to enter your search term.

   Default value: ``meta ?``

.. confval:: kb_search_next

   Press after a search has been initiated to move to the next match.

   Default value: ``n``

.. confval:: kb_search_prev

   Press after a search has been initiated to move to the previous
   match.

   Default value: ``N``

.. confval:: kb_clear_search

   Press to clear the current search.

   Default value: ``A``

.. confval:: kb_sort_date

   Press to display notes sorted by date.

   Default value: ``d``

.. confval:: kb_sort_alpha

   Press to display notes sorted alphabetically.

   Default value: ``a``

.. confval:: kb_sort_categories

   Press to display notes sorted by category.

   Default value: ``ctrl t``

.. confval:: kb_note_delete

   Press to delete a note. The note will be deleted locally and
   reflected on the server after the next full sync (see
   :confval:`kb_sync`).

   Default value: ``D``

.. confval:: kb_note_favorite

   Press to toggle the ``favorite`` flag for a note.

   Default value: ``p``

.. confval:: kb_note_category

   Press to set/edit the note category. A command window will appear at
   the bottom of the screen containing the current category (if it has
   one). Set to an empty string to clear the category.

   Default value: ``t``

.. confval:: kb_copy_note_text

   Press to copy the note text to the system clipboard.

   Default value: ``y``

.. index:: pair: configuration file; colors

Colors
~~~~~~

nncli utilizes the Python Urwid_ module to implement the console user
interface.

.. note::

   At this time, nncli does not yet support 256-color terminals and is
   limited to just 16-colors. Color names that can be specified in the
   ``config`` file are listed :ref:`here
   <urwid:16-standard-foreground>`.

The following pairs of configuration values represent the foreground and
background colors for different elements of the console GUI. In each
case the configuration value corresponding to the foreground color ends
in ``_fg``, and the configuration value corresponding to the
background color ends in ``_bg``. The default color values are listed in
foreground/background format.

.. _Urwid: http://urwid.org

.. confval:: clr_default_fg

.. confval:: clr_default_bg

   The default foreground/background colors.

   Default values: ``default/default``

.. confval:: clr_status_bar_fg

.. confval:: clr_status_bar_bg

   The foreground/background colors for the status bar.

   Default values: ``dark gray/light gray``

.. confval:: clr_log_fg

.. confval:: clr_log_bg

   The foreground/background colors for the log.

   Default values: ``dark gray/light gray``

.. confval:: clr_user_input_bar_fg

.. confval:: clr_user_input_bar_bg

   The foreground/background colors for the input bar.

   Default values: ``white/light red``

.. confval:: clr_note_focus_fg

.. confval:: clr_note_focus_bg

   The foreground/background colors for the selected note.

   Default values: ``white/light red``

.. confval:: clr_note_title_day_fg

.. confval:: clr_note_title_day_bg

   The foreground/background colors for notes edited within the past 24
   hours.

   Default values: ``light red/default``

.. confval:: clr_note_title_week_fg

.. confval:: clr_note_title_week_bg

   The foreground/background colors for notes edited within the past
   week,

   Default values: ``light green/default``

.. confval:: clr_note_title_month_fg

.. confval:: clr_note_title_month_bg

   The foreground/background colors for notes edited within the past
   month.

   Default values: ``brown/default``

.. confval:: clr_note_title_year_fg

.. confval:: clr_note_title_year_bg

   The foreground/background colors for notes edited within the past
   year.

   Default values: ``light blue/default``

.. confval:: clr_note_title_ancient_fg

.. confval:: clr_note_title_ancient_bg

   The foreground/background colors for notes last edited more than one
   year ago.

   Default values: ``light blue/default``

.. confval:: clr_note_date_fg

.. confval:: clr_note_date_bg

   The foreground/background colors for the note date (i.e. the ``%D``
   portion of :confval:`cfg_format_note_title`).

   Default values: ``dark blue/default``

.. confval:: clr_note_flags_fg

.. confval:: clr_note_flags_bg

   The foreground/background colors for the note flags (i.e., the ``%F``
   portion of :confval:`cfg_format_note_title`).

   Default values: ``dark magenta/default``

.. confval:: clr_note_category_fg

.. confval:: clr_note_category_bg

   The foreground/background colors for the note category (i.e., the
   ``%T`` portion of :confval:`cfg_format_note_title`).

   Default values: ``dark red/default``

.. confval:: clr_note_content_fg

.. confval:: clr_note_content_bg

   The foreground/background colors for the note content as displayed
   in the internal pager.

   Default values: ``default/default``

.. confval:: clr_note_content_focus_fg

.. confval:: clr_note_content_focus_bg

   The foreground/background colors for focused content within the
   internal pager.

   Default values: ``white/light red``

.. confval:: clr_note_content_old_fg

.. confval:: clr_note_content_old_bg

   The foreground/background colors for old note content as displayed
   within the internal pager.

   Default values: ``yellow/dark gray``

.. confval:: clr_note_content_old_focus_fg

.. confval:: clr_note_content_old_focus_bg

   The foreground/background colors for old note focused content as
   displayed within the internal pager.

   Default values: ``white/light red``

.. confval:: clr_help_focus_fg

.. confval:: clr_help_focus_bg

   The foreground/background colors for focused content in the help
   screen.

   Default values: ``white/light red``

.. confval:: clr_help_header_fg

.. confval:: clr_help_header_bg

   The foreground/background colors for header content in the help
   screen.

   Default values: ``dark blue/default``

.. confval:: clr_help_config_fg

.. confval:: clr_help_config_bg

   The foreground/background colors for configuration option name (e.g.,
   ``clr_help_focus_bg``) in the help screen.

   Default values: ``dark green/default``

.. confval:: clr_help_value_fg

.. confval:: clr_help_value_bg

   The foreground/background colors for the value of a configuration
   option as set in ``config``.

   Default values: ``dark red/default``

.. confval:: clr_help_descr_fg

.. confval:: clr_help_descr_bg

   The foreground/background colors for the configuration options
   description in the help screen.

   Default values: ``default/default``

Examples
--------

At the very least, the following example ``config`` will get you going
(using your account information):

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
