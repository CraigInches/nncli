
# Copyright (c) 2014 Eric Davis
# Licensed under the MIT License

import time, urwid
from . import utils
import re
from .clipboard import Clipboard
import logging

class ViewNote(urwid.ListBox):

    def __init__(self, config, args):
        self.config = config
        self.ndb = args['ndb']
        self.key = args['id']
        self.log = args['log']
        self.search_string = ''
        self.search_mode = 'gstyle'
        self.search_direction = ''
        self.note = self.ndb.get_note(self.key) if self.key else None
        self.old_note = None
        self.tabstop = int(self.config.get_config('tabstop'))
        self.clipboard = Clipboard()
        super(ViewNote, self).__init__(
                  urwid.SimpleFocusListWalker(self.get_note_content_as_list()))

    def get_note_content_as_list(self):
        lines = []
        if not self.key:
            return lines
        if self.old_note:
            for l in self.old_note['content'].split('\n'):
                lines.append(
                    urwid.AttrMap(urwid.Text(l.replace('\t', ' ' * self.tabstop)),
                                  'note_content_old',
                                  'note_content_old_focus'))
        else:
            for l in self.note['content'].split('\n'):
                lines.append(
                    urwid.AttrMap(urwid.Text(l.replace('\t', ' ' * self.tabstop)),
                                  'note_content',
                                  'note_content_focus'))
        lines.append(urwid.AttrMap(urwid.Divider('-'), 'default'))
        return lines

    def update_note_view(self, key=None, version=None):
        if key: # setting a new note
            self.key      = key
            self.note     = self.ndb.get_note(self.key)
            self.old_note = None

        self.body[:] = \
            urwid.SimpleFocusListWalker(self.get_note_content_as_list())
        if not self.search_string:
            self.focus_position = 0

    def lines_after_current_position(self):
        lines_after_current_position = list(range(self.focus_position + 1, len(self.body.positions()) - 1))
        return lines_after_current_position

    def lines_before_current_position(self):
        lines_before_current_position = list(range(0, self.focus_position))
        lines_before_current_position.reverse()
        return lines_before_current_position

    def search_note_view_next(self, search_string=None, search_mode=None):
        if search_string:
            self.search_string = search_string
        if search_mode:
            self.search_mode = search_mode
        note_range = self.lines_after_current_position() if self.search_direction == 'forward' else self.lines_before_current_position()
        self.search_note_range(note_range)

    def search_note_view_prev(self, search_string=None, search_mode=None):
        if search_string:
            self.search_string = search_string
        if search_mode:
            self.search_mode = search_mode
        note_range = self.lines_after_current_position() if self.search_direction == 'backward' else self.lines_before_current_position()
        self.search_note_range(note_range)

    def search_note_range(self, note_range):
        for line in note_range:
            line_content = self.note['content'].split('\n')[line]
            if (self.is_match(self.search_string, line_content)):
                self.focus_position = line
                break
        self.update_note_view()

    def is_match(self, term, full_text):
        if self.search_mode == 'gstyle':
            return term in full_text
        else:
            sspat = utils.build_regex_search(term)
            return sspat and sspat.search(full_text)

    def get_status_bar(self):
        if not self.key:
            return \
                urwid.AttrMap(urwid.Text('No note...'),
                              'status_bar')

        cur   = -1
        total = 0
        if len(self.body.positions()) > 0:
            cur   = self.focus_position
            total = len(self.body.positions())

        t = time.localtime(float(self.note['modified']))
        title    = utils.get_note_title(self.note)
        flags    = utils.get_note_flags(self.note)
        category = utils.get_note_category(self.note)

        mod_time = time.strftime('Date: %a, %d %b %Y %H:%M:%S', t)

        status_title = \
            urwid.AttrMap(urwid.Text('Title: ' +
                                     title,
                                     wrap='clip'),
                          'status_bar')

        status_key_index = \
            ('pack', urwid.AttrMap(urwid.Text(' [' +
                                              str(self.key) +
                                              '] ' +
                                              str(cur + 1) +
                                              '/' +
                                              str(total)),
                                   'status_bar'))

        status_date = \
            urwid.AttrMap(urwid.Text(mod_time,
                                     wrap='clip'),
                          'status_bar')

        status_category_flags = \
            ('pack', urwid.AttrMap(urwid.Text('[' +
                                              category +
                                              '] [' +
                                              flags +
                                              ']'),
                                   'status_bar'))

        pile_top = urwid.Columns([ status_title, status_key_index ])
        pile_bottom = urwid.Columns([ status_date, status_category_flags ])

        return \
            urwid.AttrMap(urwid.Pile([ pile_top, pile_bottom ]),
                          'status_bar')

    def copy_note_text(self):
        line_content = self.note['content'].split('\n')[self.focus_position]
        self.clipboard.copy(line_content)

    def keypress(self, size, key):
        if key == self.config.get_keybind('tabstop2'):
            self.tabstop = 2
            self.body[:] = \
                urwid.SimpleFocusListWalker(self.get_note_content_as_list())

        elif key == self.config.get_keybind('tabstop4'):
            self.tabstop = 4
            self.body[:] = \
                urwid.SimpleFocusListWalker(self.get_note_content_as_list())

        elif key == self.config.get_keybind('tabstop8'):
            self.tabstop = 8
            self.body[:] = \
                urwid.SimpleFocusListWalker(self.get_note_content_as_list())

        else:
            return key

        return None
