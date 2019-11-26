# -*- coding: utf-8 -*-
"""config module"""
import collections
import configparser
import os
import subprocess
import sys

from appdirs import user_cache_dir, user_config_dir

# pylint: disable=too-few-public-methods
class Config:
    """A class to contain all configuration data for nncli"""
    class State:
        """A container class for state information"""
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    def __init__(self, custom_file=None):
        self.state = Config.State(do_server_sync=True,
                                  verbose=False,
                                  do_gui=False,
                                  search_direction=None)
        self.config_home = user_config_dir('nncli', 'djmoch')
        self.cache_home = user_cache_dir('nncli', 'djmoch')

        defaults = \
        {
                'cfg_nn_username'       : '',
                'cfg_nn_password'       : '',
                'cfg_nn_password_eval'  : '',
                'cfg_db_path'           : self.cache_home,
                'cfg_search_categories' : 'yes',  # with regex searches
                'cfg_sort_mode'         : 'date', # 'alpha' or 'date'
                'cfg_favorite_ontop'    : 'yes',
                'cfg_tabstop'           : '4',
                'cfg_format_strftime'   : '%Y/%m/%d',
                'cfg_format_note_title' : '[%D] %F %-N %T',
                'cfg_status_bar'        : 'yes',
                'cfg_pager'             : os.environ['PAGER'] \
                        if 'PAGER' in os.environ else 'less -c',
                'cfg_max_logs'          : '5',
                'cfg_log_timeout'       : '5',
                'cfg_log_reversed'      : 'yes',
                'cfg_nn_host'           : '',
                'cfg_tempdir'           : '',

                'kb_help'            : 'h',
                'kb_quit'            : 'q',
                'kb_sync'            : 'S',
                'kb_down'            : 'j',
                'kb_up'              : 'k',
                'kb_page_down'       : 'space',
                'kb_page_up'         : 'b',
                'kb_half_page_down'  : 'ctrl d',
                'kb_half_page_up'    : 'ctrl u',
                'kb_bottom'          : 'G',
                'kb_top'             : 'g',
                'kb_status'          : 's',
                'kb_create_note'     : 'C',
                'kb_edit_note'       : 'e',
                'kb_view_note'       : 'enter',
                'kb_view_note_ext'   : 'meta enter',
                'kb_view_note_json'  : 'O',
                'kb_pipe_note'       : '|',
                'kb_view_next_note'  : 'J',
                'kb_view_prev_note'  : 'K',
                'kb_view_log'        : 'l',
                'kb_tabstop2'        : '2',
                'kb_tabstop4'        : '4',
                'kb_tabstop8'        : '8',
                'kb_search_gstyle'   : '/',
                'kb_search_regex'    : 'meta /',
                'kb_search_prev_gstyle'   : '?',
                'kb_search_prev_regex'   : 'meta ?',
                'kb_search_next'     : 'n',
                'kb_search_prev'     : 'N',
                'kb_clear_search'    : 'A',
                'kb_sort_date'       : 'd',
                'kb_sort_alpha'      : 'a',
                'kb_sort_categories' : 'ctrl t',
                'kb_note_delete'     : 'D',
                'kb_note_favorite'   : 'p',
                'kb_note_category'   : 't',
                'kb_copy_note_text'  : 'y',

                'clr_default_fg'                : 'default',
                'clr_default_bg'                : 'default',
                'clr_status_bar_fg'             : 'dark gray',
                'clr_status_bar_bg'             : 'light gray',
                'clr_log_fg'                    : 'dark gray',
                'clr_log_bg'                    : 'light gray',
                'clr_user_input_bar_fg'         : 'white',
                'clr_user_input_bar_bg'         : 'light red',
                'clr_note_focus_fg'             : 'white',
                'clr_note_focus_bg'             : 'light red',
                'clr_note_title_day_fg'         : 'light red',
                'clr_note_title_day_bg'         : 'default',
                'clr_note_title_week_fg'        : 'light green',
                'clr_note_title_week_bg'        : 'default',
                'clr_note_title_month_fg'       : 'brown',
                'clr_note_title_month_bg'       : 'default',
                'clr_note_title_year_fg'        : 'light blue',
                'clr_note_title_year_bg'        : 'default',
                'clr_note_title_ancient_fg'     : 'light blue',
                'clr_note_title_ancient_bg'     : 'default',
                'clr_note_date_fg'              : 'dark blue',
                'clr_note_date_bg'              : 'default',
                'clr_note_flags_fg'             : 'dark magenta',
                'clr_note_flags_bg'             : 'default',
                'clr_note_category_fg'          : 'dark red',
                'clr_note_category_bg'          : 'default',
                'clr_note_content_fg'           : 'default',
                'clr_note_content_bg'           : 'default',
                'clr_note_content_focus_fg'     : 'white',
                'clr_note_content_focus_bg'     : 'light red',
                'clr_note_content_old_fg'       : 'yellow',
                'clr_note_content_old_bg'       : 'dark gray',
                'clr_note_content_old_focus_fg' : 'white',
                'clr_note_content_old_focus_bg' : 'light red',
                'clr_help_focus_fg'             : 'white',
                'clr_help_focus_bg'             : 'light red',
                'clr_help_header_fg'            : 'dark blue',
                'clr_help_header_bg'            : 'default',
                'clr_help_config_fg'            : 'dark green',
                'clr_help_config_bg'            : 'default',
                'clr_help_value_fg'             : 'dark red',
                'clr_help_value_bg'             : 'default',
                'clr_help_descr_fg'             : 'default',
                'clr_help_descr_bg'             : 'default'
        }

        if 'VISUAL' in os.environ:
            defaults['cfg_editor'] = os.environ['VISUAL']
        elif 'EDITOR' in os.environ:
            defaults['cfg_editor'] = os.environ['EDITOR']
        else:
            defaults['cfg_editor'] = 'vim {fname} +{line}'

        parser = configparser.ConfigParser(defaults)
        if custom_file is not None:
            parser.read([custom_file])
        else:
            parser.read([os.path.join(self.config_home, 'config')])

        cfg_sec = 'nncli'

        if not parser.has_section(cfg_sec):
            parser.add_section(cfg_sec)

        # ordered dicts used to ease help
        self._create_configs_dict(parser, cfg_sec)
        self._create_keybinds_dict(parser, cfg_sec)
        self._create_colors_dict(parser, cfg_sec)

    def _create_keybinds_dict(self, parser, cfg_sec):
        """Create an OrderedDict object with the keybinds"""
        self.keybinds = collections.OrderedDict()
        self.keybinds['help'] = \
                [parser.get(cfg_sec, 'kb_help'), ['common'], 'Help']
        self.keybinds['quit'] = \
                [parser.get(cfg_sec, 'kb_quit'), ['common'], 'Quit']
        self.keybinds['sync'] = \
                [parser.get(cfg_sec, 'kb_sync'), ['common'], 'Full sync']
        self.keybinds['down'] = \
                [
                        parser.get(cfg_sec, 'kb_down'),
                        ['common'],
                        'Scroll down one line'
                ]
        self.keybinds['up'] = \
                [
                        parser.get(cfg_sec, 'kb_up'),
                        ['common'],
                        'Scroll up one line'
                ]
        self.keybinds['page_down'] = \
                [
                        parser.get(cfg_sec, 'kb_page_down'),
                        ['common'],
                        'Page down'
                ]
        self.keybinds['page_up'] = \
                [parser.get(cfg_sec, 'kb_page_up'), ['common'], 'Page up']
        self.keybinds['half_page_down'] = \
                [
                        parser.get(cfg_sec, 'kb_half_page_down'),
                        ['common'],
                        'Half page down'
                ]
        self.keybinds['half_page_up'] = \
                [
                        parser.get(cfg_sec, 'kb_half_page_up'),
                        ['common'],
                        'Half page up'
                ]
        self.keybinds['bottom'] = \
                [
                        parser.get(cfg_sec, 'kb_bottom'),
                        ['common'],
                        'Goto bottom'
                ]
        self.keybinds['top'] = \
                [parser.get(cfg_sec, 'kb_top'), ['common'], 'Goto top']
        self.keybinds['status'] = \
                [
                        parser.get(cfg_sec, 'kb_status'),
                        ['common'],
                        'Toggle status bar'
                ]
        self.keybinds['view_log'] = \
                [
                        parser.get(cfg_sec, 'kb_view_log'),
                        ['common'],
                        'View log'
                ]
        self.keybinds['create_note'] = \
                [
                        parser.get(cfg_sec, 'kb_create_note'),
                        ['titles'],
                        'Create a new note'
                ]
        self.keybinds['edit_note'] = \
                [
                        parser.get(cfg_sec, 'kb_edit_note'),
                        ['titles', 'notes'],
                        'Edit note'
                ]
        self.keybinds['view_note'] = \
                [
                        parser.get(cfg_sec, 'kb_view_note'),
                        ['titles'],
                        'View note'
                ]
        self.keybinds['view_note_ext'] = \
                [
                        parser.get(cfg_sec, 'kb_view_note_ext'),
                        ['titles', 'notes'],
                        'View note with pager'
                ]
        self.keybinds['view_note_json'] = \
                [
                        parser.get(cfg_sec, 'kb_view_note_json'),
                        ['titles', 'notes'],
                        'View note raw json'
                ]
        self.keybinds['pipe_note'] = \
                [
                        parser.get(cfg_sec, 'kb_pipe_note'),
                        ['titles', 'notes'],
                        'Pipe note contents'
                ]
        self.keybinds['view_next_note'] = \
                [
                        parser.get(cfg_sec, 'kb_view_next_note'),
                        ['notes'],
                        'View next note'
                ]
        self.keybinds['view_prev_note'] = \
                [
                        parser.get(cfg_sec, 'kb_view_prev_note'),
                        ['notes'],
                        'View previous note'
                ]
        self.keybinds['tabstop2'] = \
                [
                        parser.get(cfg_sec, 'kb_tabstop2'),
                        ['notes'],
                        'View with tabstop=2'
                ]
        self.keybinds['tabstop4'] = \
                [
                        parser.get(cfg_sec, 'kb_tabstop4'),
                        ['notes'],
                        'View with tabstop=4'
                ]
        self.keybinds['tabstop8'] = \
                [
                        parser.get(cfg_sec, 'kb_tabstop8'),
                        ['notes'],
                        'View with tabstop=8'
                ]
        self.keybinds['search_gstyle'] = \
                [
                        parser.get(cfg_sec, 'kb_search_gstyle'),
                        ['titles', 'notes'],
                        'Search using gstyle'
                ]
        self.keybinds['search_prev_gstyle'] = \
                [
                        parser.get(cfg_sec, 'kb_search_prev_gstyle'),
                        ['notes'],
                        'Search backwards using gstyle'
                ]
        self.keybinds['search_regex'] = \
                [
                        parser.get(cfg_sec, 'kb_search_regex'),
                        ['titles', 'notes'],
                        'Search using regex'
                ]
        self.keybinds['search_prev_regex'] = \
                [
                        parser.get(cfg_sec, 'kb_search_prev_regex'),
                        ['notes'],
                        'Search backwards using regex'
                ]
        self.keybinds['search_next'] = \
                [
                        parser.get(cfg_sec, 'kb_search_next'),
                        ['notes'],
                        'Go to next search result'
                ]
        self.keybinds['search_prev'] = \
                [
                        parser.get(cfg_sec, 'kb_search_prev'),
                        ['notes'],
                        'Go to previous search result'
                ]
        self.keybinds['clear_search'] = \
                [
                        parser.get(cfg_sec, 'kb_clear_search'),
                        ['titles'],
                        'Show all notes'
                ]
        self.keybinds['sort_date'] = \
                [
                        parser.get(cfg_sec, 'kb_sort_date'),
                        ['titles'],
                        'Sort notes by date'
                ]
        self.keybinds['sort_alpha'] = \
                [
                        parser.get(cfg_sec, 'kb_sort_alpha'),
                        ['titles'],
                        'Sort notes by alpha'
                ]
        self.keybinds['sort_categories'] = \
                [
                        parser.get(cfg_sec, 'kb_sort_categories'),
                        ['titles'],
                        'Sort notes by categories'
                ]
        self.keybinds['note_delete'] = \
                [
                        parser.get(cfg_sec, 'kb_note_delete'),
                        ['titles', 'notes'],
                        'Delete a note'
                ]
        self.keybinds['note_favorite'] = \
                [
                        parser.get(cfg_sec, 'kb_note_favorite'),
                        ['titles', 'notes'],
                        'Favorite note'
                ]
        self.keybinds['note_category'] = \
                [
                        parser.get(cfg_sec, 'kb_note_category'),
                        ['titles', 'notes'],
                        'Edit note category'
                ]
        self.keybinds['copy_note_text'] = \
                [
                        parser.get(cfg_sec, 'kb_copy_note_text'),
                        ['notes'],
                        'Copy line (xsel/pbcopy)'
                ]

    def _create_colors_dict(self, parser, cfg_sec):
        """Create an OrderedDict object with the colors"""
        self.colors = collections.OrderedDict()
        self.colors['default_fg'] = \
                [parser.get(cfg_sec, 'clr_default_fg'), 'Default fg']
        self.colors['default_bg'] = \
                [parser.get(cfg_sec, 'clr_default_bg'), 'Default bg']
        self.colors['status_bar_fg'] = \
                [parser.get(cfg_sec, 'clr_status_bar_fg'), 'Status bar fg']
        self.colors['status_bar_bg'] = \
                [parser.get(cfg_sec, 'clr_status_bar_bg'), 'Status bar bg']
        self.colors['log_fg'] = \
                [parser.get(cfg_sec, 'clr_log_fg'), 'Log message fg']
        self.colors['log_bg'] = \
                [parser.get(cfg_sec, 'clr_log_bg'), 'Log message bg']
        self.colors['user_input_bar_fg'] = \
                [
                        parser.get(cfg_sec, 'clr_user_input_bar_fg'),
                        'User input bar fg'
                ]
        self.colors['user_input_bar_bg'] = \
                [
                        parser.get(cfg_sec, 'clr_user_input_bar_bg'),
                        'User input bar bg'
                ]
        self.colors['note_focus_fg'] = \
                [
                        parser.get(cfg_sec, 'clr_note_focus_fg'),
                        'Note title focus fg'
                ]
        self.colors['note_focus_bg'] = \
                [
                        parser.get(cfg_sec, 'clr_note_focus_bg'),
                        'Note title focus bg'
                ]
        self.colors['note_title_day_fg'] = \
                [
                        parser.get(cfg_sec, 'clr_note_title_day_fg'),
                        'Day old note title fg'
                ]
        self.colors['note_title_day_bg'] = \
                [
                        parser.get(cfg_sec, 'clr_note_title_day_bg'),
                        'Day old note title bg'
                ]
        self.colors['note_title_week_fg'] = \
                [
                        parser.get(cfg_sec, 'clr_note_title_week_fg'),
                        'Week old note title fg'
                ]
        self.colors['note_title_week_bg'] = \
                [
                        parser.get(cfg_sec, 'clr_note_title_week_bg'),
                        'Week old note title bg'
                ]
        self.colors['note_title_month_fg'] = \
                [
                        parser.get(cfg_sec, 'clr_note_title_month_fg'),
                        'Month old note title fg'
                ]
        self.colors['note_title_month_bg'] = \
                [
                        parser.get(cfg_sec, 'clr_note_title_month_bg'),
                        'Month old note title bg'
                ]
        self.colors['note_title_year_fg'] = \
                [
                        parser.get(cfg_sec, 'clr_note_title_year_fg'),
                        'Year old note title fg'
                ]
        self.colors['note_title_year_bg'] = \
                [
                        parser.get(cfg_sec, 'clr_note_title_year_bg'),
                        'Year old note title bg'
                ]
        self.colors['note_title_ancient_fg'] = \
                [
                        parser.get(cfg_sec, 'clr_note_title_ancient_fg'),
                        'Ancient note title fg'
                ]
        self.colors['note_title_ancient_bg'] = \
                [
                        parser.get(cfg_sec, 'clr_note_title_ancient_bg'),
                        'Ancient note title bg'
                ]
        self.colors['note_date_fg'] = \
                [parser.get(cfg_sec, 'clr_note_date_fg'), 'Note date fg']
        self.colors['note_date_bg'] = \
                [parser.get(cfg_sec, 'clr_note_date_bg'), 'Note date bg']
        self.colors['note_flags_fg'] = \
                [parser.get(cfg_sec, 'clr_note_flags_fg'), 'Note flags fg']
        self.colors['note_flags_bg'] = \
                [parser.get(cfg_sec, 'clr_note_flags_bg'), 'Note flags bg']
        self.colors['note_category_fg'] = \
                [
                        parser.get(cfg_sec, 'clr_note_category_fg'),
                        'Note category fg'
                ]
        self.colors['note_category_bg'] = \
                [
                        parser.get(cfg_sec, 'clr_note_category_bg'),
                        'Note category bg'
                ]
        self.colors['note_content_fg'] = \
                [parser.get(cfg_sec, 'clr_note_content_fg'), 'Note content fg']
        self.colors['note_content_bg'] = \
                [parser.get(cfg_sec, 'clr_note_content_bg'), 'Note content bg']
        self.colors['note_content_focus_fg'] = \
                [
                        parser.get(cfg_sec, 'clr_note_content_focus_fg'),
                        'Note content focus fg'
                ]
        self.colors['note_content_focus_bg'] = \
                [
                        parser.get(cfg_sec, 'clr_note_content_focus_bg'),
                        'Note content focus bg'
                ]
        self.colors['note_content_old_fg'] = \
                [
                        parser.get(cfg_sec, 'clr_note_content_old_fg'),
                        'Old note content fg'
                ]
        self.colors['note_content_old_bg'] = \
                [
                        parser.get(cfg_sec, 'clr_note_content_old_bg'),
                        'Old note content bg'
                ]
        self.colors['note_content_old_focus_fg'] = \
                [
                        parser.get(cfg_sec, 'clr_note_content_old_focus_fg'),
                        'Old note content focus fg'
                ]
        self.colors['note_content_old_focus_bg'] = \
                [
                        parser.get(cfg_sec, 'clr_note_content_old_focus_bg'),
                        'Old note content focus bg'
                ]
        self.colors['help_focus_fg'] = \
                [parser.get(cfg_sec, 'clr_help_focus_fg'), 'Help focus fg']
        self.colors['help_focus_bg'] = \
                [parser.get(cfg_sec, 'clr_help_focus_bg'), 'Help focus bg']
        self.colors['help_header_fg'] = \
                [parser.get(cfg_sec, 'clr_help_header_fg'), 'Help header fg']
        self.colors['help_header_bg'] = \
                [parser.get(cfg_sec, 'clr_help_header_bg'), 'Help header bg']
        self.colors['help_config_fg'] = \
                [parser.get(cfg_sec, 'clr_help_config_fg'), 'Help config fg']
        self.colors['help_config_bg'] = \
                [parser.get(cfg_sec, 'clr_help_config_bg'), 'Help config bg']
        self.colors['help_value_fg'] = \
                [parser.get(cfg_sec, 'clr_help_value_fg'), 'Help value fg']
        self.colors['help_value_bg'] = \
                [parser.get(cfg_sec, 'clr_help_value_bg'), 'Help value bg']
        self.colors['help_descr_fg'] = \
                [
                        parser.get(cfg_sec, 'clr_help_descr_fg'),
                        'Help description fg'
                ]
        self.colors['help_descr_bg'] = \
                [
                        parser.get(cfg_sec, 'clr_help_descr_bg'),
                        'Help description bg'
                ]

    def _create_configs_dict(self, parser, cfg_sec):
        """Create an OrderedDict object with the configs"""

        # special handling for password so we can retrieve it by
        # running a command
        nn_password = parser.get(cfg_sec, 'cfg_nn_password', raw=True)
        if not nn_password:
            command = parser.get(cfg_sec, 'cfg_nn_password_eval', raw=True)
            if command:
                try:
                    nn_password = subprocess.check_output(
                            command,
                            shell=True,
                            universal_newlines=True
                            )
                    # remove trailing newlines to avoid requiring
                    # butchering shell commands (they can't usually be
                    # in passwords anyway)
                    nn_password = nn_password.rstrip('\n')
                except subprocess.CalledProcessError as ex:
                    print('Error evaluating command for password: %s' % ex)
                    sys.exit(1)

        self.configs = collections.OrderedDict()
        self.configs['nn_username'] = \
                [
                        parser.get(cfg_sec, 'cfg_nn_username', raw=True),
                        'NextCloud Username'
                ]
        self.configs['nn_password'] = [nn_password, 'NextCloud Password']
        self.configs['nn_host'] = \
                [
                        parser.get(cfg_sec, 'cfg_nn_host', raw=True),
                        'NextCloud server hostname'
                ]
        self.configs['db_path'] = \
                [parser.get(cfg_sec, 'cfg_db_path'), 'Note storage path']
        self.configs['search_categories'] = \
                [
                        parser.get(cfg_sec, 'cfg_search_categories'),
                        'Search categories as well'
                ]
        self.configs['sort_mode'] = \
                [parser.get(cfg_sec, 'cfg_sort_mode'), 'Sort mode']
        self.configs['favorite_ontop'] = \
                [
                        parser.get(cfg_sec, 'cfg_favorite_ontop'),
                        'Favorite at top of list'
                ]
        self.configs['tabstop'] = \
                [parser.get(cfg_sec, 'cfg_tabstop'), 'Tabstop spaces']
        self.configs['format_strftime'] = \
                [
                        parser.get(cfg_sec, 'cfg_format_strftime', raw=True),
                        'Date strftime format'
                ]
        self.configs['format_note_title'] = \
                [
                        parser.get(cfg_sec, 'cfg_format_note_title', raw=True),
                        'Note title format'
                ]
        self.configs['status_bar'] = \
                [parser.get(cfg_sec, 'cfg_status_bar'), 'Show the status bar']
        self.configs['editor'] = \
                [parser.get(cfg_sec, 'cfg_editor'), 'Editor command']
        self.configs['pager'] = \
                [parser.get(cfg_sec, 'cfg_pager'), 'External pager command']
        self.configs['max_logs'] = \
                [parser.get(cfg_sec, 'cfg_max_logs'), 'Max logs in footer']
        self.configs['log_timeout'] = \
                [parser.get(cfg_sec, 'cfg_log_timeout'), 'Log timeout']
        self.configs['log_reversed'] = \
                [parser.get(cfg_sec, 'cfg_log_reversed'), 'Log file reversed']
        self.configs['tempdir'] = \
                [
                        None if parser.get(cfg_sec, 'cfg_tempdir') == '' \
                                else parser.get(cfg_sec, 'cfg_tempdir'),
                        'Temporary directory for note storage'
                ]

    def get_config(self, name):
        """Get a config value"""
        return self.configs[name][0]

    def get_config_descr(self, name):
        """Get a config description"""
        return self.configs[name][1]

    def get_keybind(self, name):
        """Get a keybinding value"""
        return self.keybinds[name][0]

    def get_keybind_use(self, name):
        """Get the context(s) where a keybinding is valid"""
        return self.keybinds[name][1]

    def get_keybind_descr(self, name):
        """Get a keybinding description"""
        return self.keybinds[name][2]

    def get_color(self, name):
        """Get a color value"""
        return self.colors[name][0]

    def get_color_descr(self, name):
        """Get a color description"""
        return self.colors[name][1]
