.. _configuration:

Configuration
=============

The current NextCloud Notes API does not support oauth authentication so
your NextCloud Notes account password must be stored someplace
accessible to nncli. Use of the ``cfg_nn_password_eval`` option is
recommended (see :ref:`config-file`).

.. _config-file:

Configuration File
------------------

nncli pulls in configuration from the ``config`` file located in the
standard location for your platform.

.. todo:: Add platform-specific location information

The following directives are accepted within the ``config`` file:

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

.. confval:: cfg_nn_password_eval

   A command to run to retrieve the password. The command should return
   the password on ``stdout``.

   Optional. Required if :confval:`cfg_nn_password` is not specified.

.. confval:: cfg_db_path

   Specifies the path of the local notes cache.

   Optional. Default value:

   - Windows: ``%USERPROFILE%\AppData\Local\djmoch\nncli\Cache``

   - macOS: ``~/Library/Caches/nncli``

   - \*nix: ``~/.cache/nncli``

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

   Optional. Default value: ``$EDITOR`` if defined in the user's
   environment, else ``vim {fname} +{line}``.

.. confval:: cfg_pager

   Sets the command to run when opening a note for viewing in an
   external pager.

   Optional. Default value: ``$PAGER`` if defined in the user's
   environment, else ``less -c``.

.. confval:: cfg_diff

   .. todo:: Remove ``cfg_diff``

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

Keybindings
~~~~~~~~~~~

.. confval:: kb_help

.. confval:: kb_quit

.. confval:: kb_sync

.. confval:: kb_down

.. confval:: kb_up

.. confval:: kb_page_down

.. confval:: kb_page_up

.. confval:: kb_half_page_down

.. confval:: kb_half_page_up

.. confval:: kb_bottom

.. confval:: kb_top

.. confval:: kb_status

.. confval:: kb_create_note

.. confval:: kb_edit_note

.. confval:: kb_view_note

.. confval:: kb_view_note_ext

.. confval:: kb_view_note_json

.. confval:: kb_pipe_note

.. confval:: kb_view_next_note

.. confval:: kb_view_prev_note

.. confval:: kb_view_log

.. confval:: kb_tabstop2

.. confval:: kb_tabstop4

.. confval:: kb_tabstop8

.. confval:: kb_search_gstyle

.. confval:: kb_search_regex

.. confval:: kb_search_prev_gstyle

.. confval:: kb_search_prev_regex

.. confval:: kb_search_next

.. confval:: kb_search_prev

.. confval:: kb_clear_search

.. confval:: kb_sort_date

.. confval:: kb_sort_alpha

.. confval:: kb_sort_categories

.. confval:: kb_note_delete

.. confval:: kb_note_favorite

.. confval:: kb_note_category

.. confval:: kb_copy_note_text

Colors
~~~~~~

.. confval:: clr_default_fg

.. confval:: clr_default_bg

.. confval:: clr_status_bar_fg

.. confval:: clr_status_bar_bg

.. confval:: clr_log_fg

.. confval:: clr_log_bg

.. confval:: clr_user_input_bar_fg

.. confval:: clr_user_input_bar_bg

.. confval:: clr_note_focus_fg

.. confval:: clr_note_focus_bg

.. confval:: clr_note_title_day_fg

.. confval:: clr_note_title_day_bg

.. confval:: clr_note_title_week_fg

.. confval:: clr_note_title_week_bg

.. confval:: clr_note_title_month_fg

.. confval:: clr_note_title_month_bg

.. confval:: clr_note_title_year_fg

.. confval:: clr_note_title_year_bg

.. confval:: clr_note_title_ancient_fg

.. confval:: clr_note_title_ancient_bg

.. confval:: clr_note_date_fg

.. confval:: clr_note_date_bg

.. confval:: clr_note_flags_fg

.. confval:: clr_note_flags_bg

.. confval:: clr_note_category_fg

.. confval:: clr_note_category_bg

.. confval:: clr_note_content_fg

.. confval:: clr_note_content_bg

.. confval:: clr_note_content_focus_fg

.. confval:: clr_note_content_focus_bg

.. confval:: clr_note_content_old_fg

.. confval:: clr_note_content_old_bg

.. confval:: clr_note_content_old_focus_fg

.. confval:: clr_note_content_old_focus_bg

.. confval:: clr_help_focus_fg

.. confval:: clr_help_focus_bg

.. confval:: clr_help_header_fg

.. confval:: clr_help_header_bg

.. confval:: clr_help_config_fg

.. confval:: clr_help_config_bg

.. confval:: clr_help_value_fg

.. confval:: clr_help_value_bg

.. confval:: clr_help_descr_fg

.. confval:: clr_help_descr_bg

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
