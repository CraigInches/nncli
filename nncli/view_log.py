# -*- coding: utf-8 -*-
"""view_log module"""
import urwid

class ViewLog(urwid.ListBox):
    """
    ViewLog class

    This class defines the urwid view class for the log viewer
    """
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        super(ViewLog, self).__init__(urwid.SimpleFocusListWalker([]))

    def update_log(self):
        """update the log"""
        lines = []
        with open(self.logger.logfile) as logfile:
            for line in logfile:
                lines.append(
                        urwid.AttrMap(urwid.Text(line.rstrip()),
                                      'note_content',
                                      'note_content_focus')
                        )
        if self.config.get_config('log_reversed') == 'yes':
            lines.reverse()
        self.body[:] = urwid.SimpleFocusListWalker(lines)
        self.focus_position = 0

    def get_status_bar(self):
        """get the log view status bar"""
        cur = -1
        total = 0
        if self.body.positions():
            cur = self.focus_position
            total = len(self.body.positions())

        status_title = \
            urwid.AttrMap(urwid.Text('Sync Log',
                                     wrap='clip'),
                          'status_bar')
        status_index = \
            ('pack', urwid.AttrMap(urwid.Text(' ' +
                                              str(cur + 1) +
                                              '/' +
                                              str(total)),
                                   'status_bar'))
        return \
            urwid.AttrMap(urwid.Columns([status_title, status_index]),
                          'status_bar')

    def keypress(self, size, key):
        return key
