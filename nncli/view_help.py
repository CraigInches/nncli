# -*- coding: utf-8 -*-
"""view_help module"""
import re
import urwid

class ViewHelp(urwid.ListBox):
    """ViewHelp class"""
    def __init__(self, config):
        self.config = config

        self.descr_width = 26
        self.config_width = 29

        lines = []
        lines.extend(self.create_kb_help_lines('Keybinds Common', 'common'))
        lines.extend(self.create_kb_help_lines('Keybinds Note List', 'titles'))
        lines.extend(
                self.create_kb_help_lines('Keybinds Note Content', 'notes')
                )
        lines.extend(self.create_config_help_lines())
        lines.extend(self.create_color_help_lines())
        lines.append(urwid.Text(('help_header', '')))

        super(ViewHelp, self).__init__(urwid.SimpleFocusListWalker(lines))

    def get_status_bar(self):
        """get the status bar"""
        cur = -1
        total = 0
        if self.body.positions():
            cur = self.focus_position
            total = len(self.body.positions())

        status_title = \
            urwid.AttrMap(urwid.Text('Help',
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

    def create_kb_help_lines(self, header, use):
        """create the help page for the keybindings"""
        lines = [urwid.AttrMap(urwid.Text(''),
                               'help_header',
                               'help_focus')]
        lines.append(urwid.AttrMap(urwid.Text(' ' + header),
                                   'help_header',
                                   'help_focus'))
        for config in self.config.keybinds:
            if use not in self.config.get_keybind_use(config):
                continue
            keybinds_text = urwid.Text(
                    [
                            (
                                    'help_descr',
                                    (
                                            '{:>' + str(self.descr_width) + '} '
                                    ).format(
                                            self.config.get_keybind_descr(
                                                    config
                                                    )
                                            )
                            ),
                            (
                                    'help_config',
                                    (
                                            '{:>' + str(self.config_width) \
                                                    + '} '
                                    ).format('kb_' + config)
                            ),
                            (
                                    'help_value',
                                    "'" +
                                    self.config.get_keybind(config) + "'"
                            )
                    ])
            lines.append(
                    urwid.AttrMap(
                            urwid.AttrMap(
                                    keybinds_text,
                                    attr_map=None,
                                    focus_map= \
                                          {
                                                  'help_value': 'help_focus',
                                                  'help_config' : 'help_focus',
                                                  'help_descr'  : 'help_focus'
                                          }),
                            'default', 'help_focus'))
        return lines

    def create_config_help_lines(self):
        """create the help lines for the general config settings"""
        lines = [urwid.AttrMap(urwid.Text(''),
                               'help_header',
                               'help_focus')]
        lines.append(urwid.AttrMap(urwid.Text(' Configuration'),
                                   'help_header',
                                   'help_focus'))
        for config in self.config.configs:
            if config in ['nn_username', 'nn_password']:
                continue
            config_text = urwid.Text(
                    [
                            ('help_descr',
                             ('{:>' + str(self.descr_width) + '} ').
                             format(self.config.get_config_descr(config))),
                            ('help_config',
                             ('{:>' + str(self.config_width) + '} ').
                             format('cfg_' + config)),
                            ('help_value',
                             "'" +
                             str(self.config.get_config(config)) + "'")
                    ])
            lines.append(
                    urwid.AttrMap(urwid.AttrMap(
                            config_text,
                            attr_map=None,
                            focus_map={
                                    'help_value'  : 'help_focus',
                                    'help_config' : 'help_focus',
                                    'help_descr'  : 'help_focus'
                            }
                    ), 'default', 'help_focus'))
        return lines

    def create_color_help_lines(self):
        """create the help lines for the color settings"""
        lines = [urwid.AttrMap(urwid.Text(''),
                               'help_header',
                               'help_focus')]
        lines.append(urwid.AttrMap(urwid.Text(' Colors'),
                                   'help_header',
                                   'help_focus'))
        fmap = {}
        for config in self.config.colors:
            fmap[re.search('^(.*)(_fg|_bg)$', config).group(1)] = 'help_focus'
        for color in self.config.colors:
            colors_text = urwid.Text(
                    [
                            ('help_descr',
                             ('{:>' + str(self.descr_width) + '} ').
                             format(self.config.get_color_descr(color))),
                            ('help_config',
                             ('{:>' + str(self.config_width) + '} ').
                             format('clr_' + color)),
                            (re.search('^(.*)(_fg|_bg)$', color).group(1),
                             "'" + self.config.get_color(color) + "'")
                    ])
            lines.append(
                    urwid.AttrMap(urwid.AttrMap(
                            colors_text,
                            attr_map=None,
                            focus_map=fmap
                    ), 'default', 'help_focus'))
        return lines

    def keypress(self, size, key):
        return key
