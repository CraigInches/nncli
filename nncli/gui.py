# -*- coding: utf-8 -*-
"""nncli_gui module"""
import hashlib
import subprocess
import threading

import urwid
from . import view_titles, view_note, view_help, view_log, user_input
from .utils import exec_cmd_on_note, get_pager

# pylint: disable=too-many-instance-attributes, unused-argument
class NncliGui:
    """NncliGui class. Responsible for the console GUI view logic."""
    def __init__(self, config, logger, ndb, key=None):
        self.ndb = ndb
        self.logger = logger
        self.config = config
        self.last_view = []
        self.status_bar = self.config.get_config('status_bar')
        self.config.state.current_sort_mode = \
                self.config.get_config('sort_mode')


        self.log_lock = threading.Lock()
        self.log_alarms = 0
        self.logs = []

        self.thread_sync = threading.Thread(
                target=self.ndb.sync_worker,
                args=[self.config.state.do_server_sync]
                )
        self.thread_sync.setDaemon(True)

        self.view_titles = \
            view_titles.ViewTitles(
                    self.config,
                    {
                            'ndb'           : self.ndb,
                            'search_string' : None,
                            'log'           : self.log
                    }
                    )
        self.view_note = \
            view_note.ViewNote(
                    self.config,
                    {
                            'ndb' : self.ndb,
                            'id' : key, # initial key to view or None
                            'log' : self.log
                    }
                    )

        self.view_log = view_log.ViewLog(self.config, self.logger)
        self.view_help = view_help.ViewHelp(self.config)

        palette = \
                [
                        (
                                'default',
                                self.config.get_color('default_fg'),
                                self.config.get_color('default_bg')
                        ),
                        (
                                'status_bar',
                                self.config.get_color('status_bar_fg'),
                                self.config.get_color('status_bar_bg')
                        ),
                        (
                                'log',
                                self.config.get_color('log_fg'),
                                self.config.get_color('log_bg')
                        ),
                        (
                                'user_input_bar',
                                self.config.get_color('user_input_bar_fg'),
                                self.config.get_color('user_input_bar_bg')
                        ),
                        (
                                'note_focus',
                                self.config.get_color('note_focus_fg'),
                                self.config.get_color('note_focus_bg')
                        ),
                        (
                                'note_title_day',
                                self.config.get_color('note_title_day_fg'),
                                self.config.get_color('note_title_day_bg')
                        ),
                        (
                                'note_title_week',
                                self.config.get_color('note_title_week_fg'),
                                self.config.get_color('note_title_week_bg')
                        ),
                        (
                                'note_title_month',
                                self.config.get_color('note_title_month_fg'),
                                self.config.get_color('note_title_month_bg')
                        ),
                        (
                                'note_title_year',
                                self.config.get_color('note_title_year_fg'),
                                self.config.get_color('note_title_year_bg')
                        ),
                        (
                                'note_title_ancient',
                                self.config.get_color('note_title_ancient_fg'),
                                self.config.get_color('note_title_ancient_bg')
                        ),
                        (
                                'note_date',
                                self.config.get_color('note_date_fg'),
                                self.config.get_color('note_date_bg')
                        ),
                        (
                                'note_flags',
                                self.config.get_color('note_flags_fg'),
                                self.config.get_color('note_flags_bg')
                        ),
                        (
                                'note_category',
                                self.config.get_color('note_category_fg'),
                                self.config.get_color('note_category_bg')
                        ),
                        (
                                'note_content',
                                self.config.get_color('note_content_fg'),
                                self.config.get_color('note_content_bg')
                        ),
                        (
                                'note_content_focus',
                                self.config.get_color('note_content_focus_fg'),
                                self.config.get_color('note_content_focus_bg')
                        ),
                        (
                                'note_content_old',
                                self.config.get_color('note_content_old_fg'),
                                self.config.get_color('note_content_old_bg')
                        ),
                        (
                                'note_content_old_focus',
                                self.config.get_color(
                                        'note_content_old_focus_fg'
                                        ),
                                self.config.get_color(
                                        'note_content_old_focus_bg'
                                        )
                        ),
                        (
                                'help_focus',
                                self.config.get_color('help_focus_fg'),
                                self.config.get_color('help_focus_bg')
                        ),
                        (
                                'help_header',
                                self.config.get_color('help_header_fg'),
                                self.config.get_color('help_header_bg')
                        ),
                        (
                                'help_config',
                                self.config.get_color('help_config_fg'),
                                self.config.get_color('help_config_bg')
                        ),
                        (
                                'help_value',
                                self.config.get_color('help_value_fg'),
                                self.config.get_color('help_value_bg')
                        ),
                        (
                                'help_descr',
                                self.config.get_color('help_descr_fg'),
                                self.config.get_color('help_descr_bg')
                        )
                ]

        self.master_frame = urwid.Frame(
                body=urwid.Filler(urwid.Text('')),
                header=None,
                footer=urwid.Pile([urwid.Pile([]), urwid.Pile([])]),
                focus_part='body')

        self.nncli_loop = urwid.MainLoop(self.master_frame,
                                         palette,
                                         handle_mouse=False)

        self.nncli_loop.set_alarm_in(0, self._gui_init_view, \
                bool(key))

    def run(self):
        """Run the GUI"""
        self.nncli_loop.run()

    def _gui_header_clear(self):
        """Clear the console GUI header row"""
        self.master_frame.contents['header'] = (None, None)
        self.nncli_loop.draw_screen()

    def _gui_header_set(self, widget):
        """Set the content of the console GUI header row"""
        self.master_frame.contents['header'] = (widget, None)
        self.nncli_loop.draw_screen()

    def _gui_footer_log_clear(self):
        """Clear the log at the bottom of the GUI"""
        gui = self._gui_footer_input_get()
        self.master_frame.contents['footer'] = \
                (urwid.Pile([urwid.Pile([]), urwid.Pile([gui])]), None)
        self.nncli_loop.draw_screen()

    def _gui_footer_log_set(self, pile):
        """Set the log at the bottom of the GUI"""
        gui = self._gui_footer_input_get()
        self.master_frame.contents['footer'] = \
                (urwid.Pile([urwid.Pile(pile), urwid.Pile([gui])]), None)
        self.nncli_loop.draw_screen()

    def _gui_footer_log_get(self):
        """Get the log at the bottom of the GUI"""
        return self.master_frame.contents['footer'][0].contents[0][0]

    def _gui_footer_input_clear(self):
        """Clear the input at the bottom of the GUI"""
        pile = self._gui_footer_log_get()
        self.master_frame.contents['footer'] = \
                (urwid.Pile([urwid.Pile([pile]), urwid.Pile([])]), None)
        self.nncli_loop.draw_screen()

    def _gui_footer_input_set(self, gui):
        """Set the input at the bottom of the GUI"""
        pile = self._gui_footer_log_get()
        self.master_frame.contents['footer'] = \
                (urwid.Pile([urwid.Pile([pile]), urwid.Pile([gui])]), None)
        self.nncli_loop.draw_screen()

    def _gui_footer_input_get(self):
        """Get the input at the bottom of the GUI"""
        return self.master_frame.contents['footer'][0].contents[1][0]

    def _gui_footer_focus_input(self):
        """Set the GUI focus to the input at the bottom of the GUI"""
        self.master_frame.focus_position = 'footer'
        self.master_frame.contents['footer'][0].focus_position = 1

    def _gui_body_set(self, widget):
        """Set the GUI body"""
        self.master_frame.contents['body'] = (widget, None)
        self._gui_update_status_bar()
        self.nncli_loop.draw_screen()

    def gui_body_get(self):
        """Get the GUI body"""
        return self.master_frame.contents['body'][0]

    def _gui_body_focus(self):
        """Set the GUI focus to the body"""
        self.master_frame.focus_position = 'body'

    def gui_update_view(self):
        """Update the GUI"""
        if not self.config.state.do_gui:
            return

        try:
            cur_key = self.view_titles.note_list \
                    [self.view_titles.focus_position].note['localkey']
        except IndexError:
            cur_key = None

        self.view_titles.update_note_list(
                self.view_titles.search_string,
                sort_mode=self.config.state.current_sort_mode
                )
        self.view_titles.focus_note(cur_key)

        if self.gui_body_get().__class__ == view_note.ViewNote:
            self.view_note.update_note_view()

        self._gui_update_status_bar()

    def _gui_update_status_bar(self):
        """Update the GUI status bar"""
        if self.status_bar != 'yes':
            self._gui_header_clear()
        else:
            self._gui_header_set(self.gui_body_get().get_status_bar())

    def _gui_switch_frame_body(self, new_view, save_current_view=True):
        """
        Switch the body frame of the GUI. Used to switch to a new
        view
        """
        if new_view is None:
            if not self.last_view:
                self._gui_stop()
            else:
                self._gui_body_set(self.last_view.pop())
        else:
            if self.gui_body_get().__class__ != new_view.__class__:
                if save_current_view:
                    self.last_view.append(self.gui_body_get())
                self._gui_body_set(new_view)

    def _delete_note_callback(self, key, delete):
        """Update the GUI after deleting a note"""
        if not delete:
            return
        self.ndb.set_note_deleted(key, True)

        if self.gui_body_get().__class__ == view_titles.ViewTitles:
            self.view_titles.update_note_title()

        self._gui_update_status_bar()
        self.ndb.sync_worker_go()

    def _gui_yes_no_input(self, args, yes_no):
        """Create a yes/no input dialog at the GUI footer"""
        self._gui_footer_input_clear()
        self._gui_body_focus()
        self.master_frame.keypress = self._gui_frame_keypress
        args[0](args[1],
                yes_no in ['YES', 'Yes', 'yes', 'Y', 'y']
                )

    def _gui_search_input(self, args, search_string):
        """Create a search input dialog at the GUI footer"""
        self._gui_footer_input_clear()
        self._gui_body_focus()
        self.master_frame.keypress = self._gui_frame_keypress
        if search_string:
            if self.gui_body_get() == self.view_note:
                self.config.state.search_direction = args[1]
                self.view_note.search_note_view_next(
                        search_string=search_string,
                        search_mode=args[0]
                        )
            else:
                self.view_titles.update_note_list(
                        search_string,
                        args[0],
                        sort_mode=self.config.state.current_sort_mode
                        )
                self._gui_body_set(self.view_titles)

    def _gui_category_input(self, args, category):
        """Create a category input at the GUI footer"""
        self._gui_footer_input_clear()
        self._gui_body_focus()
        self.master_frame.keypress = self._gui_frame_keypress
        if category is not None:
            if self.gui_body_get().__class__ == view_titles.ViewTitles:
                note = self.view_titles.note_list \
                        [self.view_titles.focus_position].note
            else: # self.gui_body_get().__class__ == view_note.ViewNote:
                note = self.view_note.note

            self.ndb.set_note_category(note['localkey'], category)

            if self.gui_body_get().__class__ == view_titles.ViewTitles:
                self.view_titles.update_note_title()
            else: # self.gui_body_get().__class__ == view_note.ViewNote:
                self.view_note.update_note_view()

            self._gui_update_status_bar()
            self.ndb.sync_worker_go()

    def _gui_pipe_input(self, args, cmd):
        """Create a pipe input dialog at the GUI footoer"""
        self._gui_footer_input_clear()
        self._gui_body_focus()
        self.master_frame.keypress = self._gui_frame_keypress
        if cmd is not None:
            if self.gui_body_get().__class__ == view_titles.ViewTitles:
                note = self.view_titles.note_list \
                        [self.view_titles.focus_position].note
            else: # self.gui_body_get().__class__ == view_note.ViewNote:
                note = self.view_note.old_note \
                        if self.view_note.old_note \
                        else self.view_note.note
            try:
                self._gui_clear()
                pipe = subprocess.Popen(cmd, stdin=subprocess.PIPE, shell=True)
                pipe.communicate(note['content'].encode('utf-8'))
                pipe.stdin.close()
                pipe.wait()
            except OSError as ex:
                self.log('Pipe error: %s' % ex)
            finally:
                self._gui_reset()

    # pylint: disable=too-many-return-statements, too-many-branches
    # pylint: disable=too-many-statements
    def _gui_frame_keypress(self, size, key):
        """Keypress handler for the GUI"""
        # convert space character into name
        if key == ' ':
            key = 'space'

        contents = self.gui_body_get()

        if key == self.config.get_keybind('quit'):
            self._gui_switch_frame_body(None)

        elif key == self.config.get_keybind('help'):
            self._gui_switch_frame_body(self.view_help)

        elif key == self.config.get_keybind('sync'):
            self.ndb.last_sync = 0
            self.ndb.sync_worker_go()

        elif key == self.config.get_keybind('view_log'):
            self.view_log.update_log()
            self._gui_switch_frame_body(self.view_log)

        elif key == self.config.get_keybind('down'):
            if not contents.body.positions():
                return None
            last = len(contents.body.positions())
            if contents.focus_position == (last - 1):
                return None
            contents.focus_position += 1
            contents.render(size)

        elif key == self.config.get_keybind('up'):
            if not contents.body.positions():
                return None
            if contents.focus_position == 0:
                return None
            contents.focus_position -= 1
            contents.render(size)

        elif key == self.config.get_keybind('page_down'):
            if not contents.body.positions():
                return None
            last = len(contents.body.positions())
            next_focus = contents.focus_position + size[1]
            if next_focus >= last:
                next_focus = last - 1
            contents.change_focus(size, next_focus,
                                  offset_inset=0,
                                  coming_from='above')

        elif key == self.config.get_keybind('page_up'):
            if not contents.body.positions():
                return None
            if 'bottom' in contents.ends_visible(size):
                last = len(contents.body.positions())
                next_focus = last - size[1] - size[1]
            else:
                next_focus = contents.focus_position - size[1]
            if next_focus < 0:
                next_focus = 0
            contents.change_focus(size, next_focus,
                                  offset_inset=0,
                                  coming_from='below')

        elif key == self.config.get_keybind('half_page_down'):
            if not contents.body.positions():
                return None
            last = len(contents.body.positions())
            next_focus = contents.focus_position + (size[1] // 2)
            if next_focus >= last:
                next_focus = last - 1
            contents.change_focus(size, next_focus,
                                  offset_inset=0,
                                  coming_from='above')

        elif key == self.config.get_keybind('half_page_up'):
            if not contents.body.positions():
                return None
            if 'bottom' in contents.ends_visible(size):
                last = len(contents.body.positions())
                next_focus = last - size[1] - (size[1] // 2)
            else:
                next_focus = contents.focus_position - (size[1] // 2)
            if next_focus < 0:
                next_focus = 0
            contents.change_focus(size, next_focus,
                                  offset_inset=0,
                                  coming_from='below')

        elif key == self.config.get_keybind('bottom'):
            if not contents.body.positions():
                return None
            contents.change_focus(size, (len(contents.body.positions()) - 1),
                                  offset_inset=0,
                                  coming_from='above')

        elif key == self.config.get_keybind('top'):
            if not contents.body.positions():
                return None
            contents.change_focus(size, 0,
                                  offset_inset=0,
                                  coming_from='below')

        elif key == self.config.get_keybind('view_next_note'):
            if self.gui_body_get().__class__ != view_note.ViewNote:
                return key

            if not self.view_titles.body.positions():
                return None
            last = len(self.view_titles.body.positions())
            if self.view_titles.focus_position == (last - 1):
                return None
            self.view_titles.focus_position += 1
            contents.update_note_view(
                    self.view_titles. \
                            note_list[self.view_titles. \
                            focus_position].note['localkey']
                    )
            self._gui_switch_frame_body(self.view_note)

        elif key == self.config.get_keybind('view_prev_note'):
            if self.gui_body_get().__class__ != view_note.ViewNote:
                return key

            if not self.view_titles.body.positions():
                return None
            if self.view_titles.focus_position == 0:
                return None
            self.view_titles.focus_position -= 1
            contents.update_note_view(
                    self.view_titles. \
                            note_list[self.view_titles. \
                            focus_position].note['localkey']
                    )
            self._gui_switch_frame_body(self.view_note)

        elif key == self.config.get_keybind('status'):
            if self.status_bar == 'yes':
                self.status_bar = 'no'
            else:
                self.status_bar = self.config.get_config('status_bar')

        elif key == self.config.get_keybind('create_note'):
            if self.gui_body_get().__class__ != view_titles.ViewTitles:
                return key

            self._gui_clear()
            content = exec_cmd_on_note(None, self.config, self, self.logger)
            self._gui_reset()

            if content:
                self.log('New note created')
                self.ndb.create_note(content)
                self.gui_update_view()
                self.ndb.sync_worker_go()

        elif key == self.config.get_keybind('edit_note') or \
             key == self.config.get_keybind('view_note_ext') or \
             key == self.config.get_keybind('view_note_json'):
            if self.gui_body_get().__class__ != view_titles.ViewTitles and \
               self.gui_body_get().__class__ != view_note.ViewNote:
                return key

            if self.gui_body_get().__class__ == view_titles.ViewTitles:
                if not contents.body.positions():
                    return None
                note = contents.note_list[contents.focus_position].note
            else: # self.gui_body_get().__class__ == view_note.ViewNote:
                if key == self.config.get_keybind('edit_note'):
                    note = contents.note
                else:
                    note = contents.old_note if contents.old_note \
                            else contents.note

            self._gui_clear()
            if key == self.config.get_keybind('edit_note'):
                content = exec_cmd_on_note(note, self.config, self,
                                           self.logger)
            elif key == self.config.get_keybind('view_note_ext'):
                content = exec_cmd_on_note(
                        note,
                        self.config,
                        self,
                        self.logger,
                        cmd=get_pager(self.config, self.logger))
            else: # key == self.config.get_keybind('view_note_json')
                content = exec_cmd_on_note(
                        note,
                        self.config,
                        self,
                        self.logger,
                        cmd=get_pager(self.config, self.logger),
                        raw=True
                        )

            self._gui_reset()

            if not content:
                return None

            md5_old = hashlib.md5(note['content'].encode('utf-8')).digest()
            md5_new = hashlib.md5(content.encode('utf-8')).digest()

            if md5_old != md5_new:
                self.log('Note updated')
                self.ndb.set_note_content(note['localkey'], content)
                if self.gui_body_get().__class__ == view_titles.ViewTitles:
                    contents.update_note_title()
                else: # self.gui_body_get().__class__ == view_note.ViewNote:
                    contents.update_note_view()
                self.ndb.sync_worker_go()
            else:
                self.log('Note unchanged')

        elif key == self.config.get_keybind('view_note'):
            if self.gui_body_get().__class__ != view_titles.ViewTitles:
                return key

            if not contents.body.positions():
                return None
            self.view_note.update_note_view(
                    contents.note_list[contents.focus_position]. \
                            note['localkey'])
            self._gui_switch_frame_body(self.view_note)

        elif key == self.config.get_keybind('pipe_note'):
            if self.gui_body_get().__class__ != view_titles.ViewTitles and \
               self.gui_body_get().__class__ != view_note.ViewNote:
                return key

            if self.gui_body_get().__class__ == view_titles.ViewTitles:
                if not contents.body.positions():
                    return None
                note = contents.note_list[contents.focus_position].note
            else: # self.gui_body_get().__class__ == view_note.ViewNote:
                note = contents.old_note if contents.old_note else contents.note

            self._gui_footer_input_set(
                    urwid.AttrMap(
                            user_input.UserInput(
                                    self.config,
                                    key,
                                    '',
                                    self._gui_pipe_input,
                                    None
                                    ),
                            'user_input_bar'
                            )
                    )
            self._gui_footer_focus_input()
            self.master_frame.keypress = \
                    self._gui_footer_input_get().keypress

        elif key == self.config.get_keybind('note_delete'):
            if self.gui_body_get().__class__ != view_titles.ViewTitles and \
               self.gui_body_get().__class__ != view_note.ViewNote:
                return key

            if self.gui_body_get().__class__ == view_titles.ViewTitles:
                if not contents.body.positions():
                    return None
                note = contents.note_list[contents.focus_position].note
            else: # self.gui_body_get().__class__ == view_note.ViewNote:
                note = contents.note

            self._gui_footer_input_set(
                    urwid.AttrMap(
                            user_input.UserInput(
                                    self.config,
                                    'Delete (y/n): ',
                                    '',
                                    self._gui_yes_no_input,
                                    [
                                            self._delete_note_callback,
                                            note['localkey']
                                    ]
                                    ),
                            'user_input_bar'
                            )
                    )
            self._gui_footer_focus_input()
            self.master_frame.keypress = \
                    self._gui_footer_input_get().keypress

        elif key == self.config.get_keybind('note_favorite'):
            if self.gui_body_get().__class__ != view_titles.ViewTitles and \
               self.gui_body_get().__class__ != view_note.ViewNote:
                return key

            if self.gui_body_get().__class__ == view_titles.ViewTitles:
                if not contents.body.positions():
                    return None
                note = contents.note_list[contents.focus_position].note
            else: # self.gui_body_get().__class__ == view_note.ViewNote:
                note = contents.note

            favorite = not note['favorite']

            self.ndb.set_note_favorite(note['localkey'], favorite)

            if self.gui_body_get().__class__ == view_titles.ViewTitles:
                contents.update_note_title()

            self.ndb.sync_worker_go()

        elif key == self.config.get_keybind('note_category'):
            if self.gui_body_get().__class__ != view_titles.ViewTitles and \
               self.gui_body_get().__class__ != view_note.ViewNote:
                return key

            if self.gui_body_get().__class__ == view_titles.ViewTitles:
                if not contents.body.positions():
                    return None
                note = contents.note_list[contents.focus_position].note
            else: # self.gui_body_get().__class__ == view_note.ViewNote:
                note = contents.note

            self._gui_footer_input_set(
                    urwid.AttrMap(
                            user_input.UserInput(
                                    self.config,
                                    'Category: ',
                                    note['category'],
                                    self._gui_category_input,
                                    None
                                    ),
                            'user_input_bar'
                            )
                    )
            self._gui_footer_focus_input()
            self.master_frame.keypress = \
                    self._gui_footer_input_get().keypress

        elif key == self.config.get_keybind('search_gstyle') or \
             key == self.config.get_keybind('search_regex') or \
             key == self.config.get_keybind('search_prev_gstyle') or \
             key == self.config.get_keybind('search_prev_regex'):
            if self.gui_body_get().__class__ != view_titles.ViewTitles and \
                 self.gui_body_get().__class__ != view_note.ViewNote:
                return key

            if self.gui_body_get().__class__ == view_note.ViewNote:
                if key == self.config.get_keybind('search_prev_gstyle') or \
                     key == self.config.get_keybind('search_prev_regex'):
                    self.view_note.search_direction = 'backward'
                else:
                    self.view_note.search_direction = 'forward'

            options = [
                    'gstyle' if key == self.config.get_keybind('search_gstyle')
                    or key == self.config.get_keybind('search_prev_gstyle')
                    else 'regex',
                    'backward' if key ==
                    self.config.get_keybind('search_prev_gstyle')
                    or key == self.config.get_keybind('search_prev_regex')
                    else 'forward'
            ]

            caption = '{}{}'.format('(regex) '
                                    if options[0] == 'regex'
                                    else '',
                                    '/' if options[1] == 'forward'
                                    else '?')

            self._gui_footer_input_set(
                    urwid.AttrMap(
                            user_input.UserInput(
                                    self.config,
                                    caption,
                                    '',
                                    self._gui_search_input,
                                    options
                                    ),
                            'user_input_bar'
                            )
                    )
            self._gui_footer_focus_input()
            self.master_frame.keypress = \
                    self._gui_footer_input_get().keypress

        elif key == self.config.get_keybind('search_next'):
            if self.gui_body_get().__class__ != view_note.ViewNote:
                return key

            self.view_note.search_note_view_next()

        elif key == self.config.get_keybind('search_prev'):
            if self.gui_body_get().__class__ != view_note.ViewNote:
                return key

            self.view_note.search_note_view_prev()

        elif key == self.config.get_keybind('clear_search'):
            if self.gui_body_get().__class__ != view_titles.ViewTitles:
                return key

            self.view_titles.update_note_list(
                    None,
                    sort_mode=self.config.state.current_sort_mode
                    )
            self._gui_body_set(self.view_titles)

        elif key == self.config.get_keybind('sort_date'):
            if self.gui_body_get().__class__ != view_titles.ViewTitles:
                return key

            self.config.state.current_sort_mode = 'date'
            self.view_titles.sort_note_list('date')

        elif key == self.config.get_keybind('sort_alpha'):
            if self.gui_body_get().__class__ != view_titles.ViewTitles:
                return key

            self.config.state.current_sort_mode = 'alpha'
            self.view_titles.sort_note_list('alpha')

        elif key == self.config.get_keybind('sort_categories'):
            if self.gui_body_get().__class__ != view_titles.ViewTitles:
                return key

            self.config.state.current_sort_mode = 'categories'
            self.view_titles.sort_note_list('categories')

        elif key == self.config.get_keybind('copy_note_text'):
            if self.gui_body_get().__class__ != view_note.ViewNote:
                return key

            self.view_note.copy_note_text()

        else:
            return contents.keypress(size, key)

        self._gui_update_status_bar()
        return None

    def _gui_init_view(self, loop, show_note):
        """Initialize the GUI"""
        self.master_frame.keypress = self._gui_frame_keypress
        self._gui_body_set(self.view_titles)

        if show_note:
            # note that title view set first to prime the view stack
            self._gui_switch_frame_body(self.view_note)

        self.thread_sync.start()

    def _gui_clear(self):
        """Clear the GUI"""
        self.nncli_loop.widget = urwid.Filler(urwid.Text(''))
        self.nncli_loop.draw_screen()

    def _gui_reset(self):
        """Reset the GUI"""
        self.nncli_loop.widget = self.master_frame
        self.nncli_loop.draw_screen()

    def _gui_stop(self):
        """Stop the GUI"""
        # don't exit if there are any notes not yet saved to the disk

        # NOTE: this was originally causing hangs on exit with urllib2
        # should not be a problem now since using the requests library
        # ref https://github.com/insanum/sncli/issues/18#issuecomment-105517773
        if self.ndb.verify_all_saved():
            # clear the screen and exit the urwid run loop
            self._gui_clear()
            raise urwid.ExitMainLoop()
        self.log('WARNING: Not all notes saved'
                 'to disk (wait for sync worker)')

    def log(self, msg):
        """Log as message, displaying to the user as appropriate"""
        self.logger.log(msg)

        self.log_lock.acquire()

        self.log_alarms += 1
        self.logs.append(msg)

        if len(self.logs) > int(self.config.get_config('max_logs')):
            self.log_alarms -= 1
            self.logs.pop(0)

        log_pile = []
        for log in self.logs:
            log_pile.append(urwid.AttrMap(urwid.Text(log), 'log'))

        if self.config.state.verbose:
            self._gui_footer_log_set(log_pile)

        self.nncli_loop.set_alarm_in(
                int(self.config.get_config('log_timeout')),
                self._log_timeout, None)

        self.log_lock.release()

    def _log_timeout(self, loop, arg):
        """
        Run periodically to check for new log entries to append to
        the GUI footer
        """
        self.log_lock.acquire()

        self.log_alarms -= 1

        if self.log_alarms == 0:
            self._gui_footer_log_clear()
            self.logs = []
        else:
            if self.logs:
                self.logs.pop(0)

            log_pile = []

            for log in self.logs:
                log_pile.append(urwid.AttrMap(urwid.Text(log), 'log'))

            if self.config.state.verbose:
                self._gui_footer_log_set(log_pile)

        self.log_lock.release()
