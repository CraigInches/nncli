#
# The MIT License (MIT)
#
# Copyright (c) 2018 Daniel Moch
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

# Copyright (c) 2014 Eric Davis
# Licensed under the MIT License

import os, sys, getopt, re, signal, time, datetime, shlex, hashlib
import subprocess, threading, logging
import copy, json, urwid, datetime
from . import view_titles, view_note, view_help, view_log, user_input
from . import utils, temp
from .config import Config
from .nextcloud_note import NextcloudNote
from .notes_db import NotesDB, ReadError, WriteError
from logging.handlers import RotatingFileHandler

class nncli:

    def __init__(self, do_server_sync, verbose=False, config_file=None):
        self.config         = Config(config_file)
        self.do_server_sync = do_server_sync
        self.verbose        = verbose
        self.do_gui         = False
        force_full_sync     = False
        self.current_sort_mode = self.config.get_config('sort_mode')

        self.tempdir = self.config.get_config('tempdir')
        if self.tempdir == '':
            self.tempdir = None

        if not os.path.exists(self.config.get_config('db_path')):
            os.mkdir(self.config.get_config('db_path'))
            force_full_sync = True

        # configure the logging module
        self.logfile = os.path.join(self.config.get_config('db_path'), 'nncli.log')
        self.loghandler = RotatingFileHandler(self.logfile, maxBytes=100000, backupCount=1)
        self.loghandler.setLevel(logging.DEBUG)
        self.loghandler.setFormatter(logging.Formatter(fmt='%(asctime)s [%(levelname)s] %(message)s'))
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.loghandler)
        self.config.logfile = self.logfile

        logging.debug('nncli logging initialized')

        self.logs = []

        try:
            self.ndb = NotesDB(self.config, self.log, self.gui_update_view)
        except Exception as e:
            self.log(str(e))
            sys.exit(1)

        if force_full_sync:
            # The note database doesn't exist so force a full sync. It is
            # important to do this outside of the gui because an account
            # with hundreds of notes will cause a recursion panic under
            # urwid. This simple workaround gets the job done. :-)
            self.verbose = True
            self.log('nncli database doesn\'t exist, forcing full sync...')
            self.sync_notes()
            self.verbose = verbose

    def sync_notes(self):
        self.ndb.sync_now(self.do_server_sync)

    def get_editor(self):
        editor = self.config.get_config('editor')
        if not editor:
            self.log('No editor configured!')
            return None
        return editor

    def get_pager(self):
        pager = self.config.get_config('pager')
        if not pager:
            self.log('No pager configured!')
            return None
        return pager

    def get_diff(self):
        diff = self.config.get_config('diff')
        if not diff:
            self.log('No diff command configured!')
            return None
        return diff

    def exec_cmd_on_note(self, note, cmd=None, raw=False):

        if not cmd:
            cmd = self.get_editor()
        if not cmd:
            return None

        tf = temp.tempfile_create(note if note else None, raw=raw, tempdir=self.tempdir)
        fname = temp.tempfile_name(tf)

        focus_position = 0
        try:
            focus_position = self.gui_body_get().focus_position
        except IndexError:
            # focus position will fail if no notes available (listbox empty)
            # TODO: find a neater way to check than try/except
            pass
        except AttributeError:
            # we're running in CLI mode
            pass

        subs = {
            'fname': fname,
            'line': focus_position + 1,
        }
        cmd_list = [c.format(**subs) for c in shlex.split(cmd)]

        # if the filename wasn't able to be subbed, append it
        # this makes it fully backwards compatible with previous configs
        if '{fname}' not in cmd:
            cmd_list.append(fname)

        self.log("EXECUTING: {}".format(cmd_list))

        try:
            subprocess.check_call(cmd_list)
        except Exception as e:
            self.log('Command error: ' + str(e))
            temp.tempfile_delete(tf)
            return None

        content = None
        if not raw:
            content = temp.tempfile_content(tf)
            if not content or content == '\n':
                content = None

        temp.tempfile_delete(tf)
        return content

    def exec_diff_on_note(self, note, old_note):

        diff = self.get_diff()
        if not diff:
            return None

        pager = self.get_pager()
        if not pager:
            return None

        ltf = temp.tempfile_create(note, tempdir=self.tempdir)
        otf = temp.tempfile_create(old_note, tempdir=self.tempdir)
        out = temp.tempfile_create(None, tempdir=self.tempdir)

        try:
            subprocess.call(diff + ' ' +
                            temp.tempfile_name(ltf) + ' ' +
                            temp.tempfile_name(otf) + ' > ' +
                            temp.tempfile_name(out),
                            shell=True)
            subprocess.check_call(pager + ' ' +
                                  temp.tempfile_name(out),
                                  shell=True)
        except Exception as e:
            self.log('Command error: ' + str(e))
            temp.tempfile_delete(ltf)
            temp.tempfile_delete(otf)
            temp.tempfile_delete(out)
            return None

        temp.tempfile_delete(ltf)
        temp.tempfile_delete(otf)
        temp.tempfile_delete(out)
        return None

    def gui_header_clear(self):
        self.master_frame.contents['header'] = ( None, None )
        self.nncli_loop.draw_screen()

    def gui_header_set(self, w):
        self.master_frame.contents['header'] = ( w, None )
        self.nncli_loop.draw_screen()

    def gui_header_get(self):
        return self.master_frame.contents['header'][0]

    def gui_header_focus(self):
        self.master_frame.focus_position = 'header'

    def gui_footer_log_clear(self):
        ui = self.gui_footer_input_get()
        self.master_frame.contents['footer'] = \
                (urwid.Pile([ urwid.Pile([]), urwid.Pile([ui]) ]), None)
        self.nncli_loop.draw_screen()

    def gui_footer_log_set(self, pl):
        ui = self.gui_footer_input_get()
        self.master_frame.contents['footer'] = \
                (urwid.Pile([ urwid.Pile(pl), urwid.Pile([ui]) ]), None)
        self.nncli_loop.draw_screen()

    def gui_footer_log_get(self):
        return self.master_frame.contents['footer'][0].contents[0][0]

    def gui_footer_input_clear(self):
        pl = self.gui_footer_log_get()
        self.master_frame.contents['footer'] = \
                (urwid.Pile([ urwid.Pile([pl]), urwid.Pile([]) ]), None)
        self.nncli_loop.draw_screen()

    def gui_footer_input_set(self, ui):
        pl = self.gui_footer_log_get()
        self.master_frame.contents['footer'] = \
                (urwid.Pile([ urwid.Pile([pl]), urwid.Pile([ui]) ]), None)
        self.nncli_loop.draw_screen()

    def gui_footer_input_get(self):
        return self.master_frame.contents['footer'][0].contents[1][0]

    def gui_footer_focus_input(self):
        self.master_frame.focus_position = 'footer'
        self.master_frame.contents['footer'][0].focus_position = 1

    def gui_body_clear(self):
        self.master_frame.contents['body'] = ( None, None )
        self.nncli_loop.draw_screen()

    def gui_body_set(self, w):
        self.master_frame.contents['body'] = ( w, None )
        self.gui_update_status_bar()
        self.nncli_loop.draw_screen()

    def gui_body_get(self):
        return self.master_frame.contents['body'][0]

    def gui_body_focus(self):
        self.master_frame.focus_position = 'body'

    def log_timeout(self, loop, arg):
        self.log_lock.acquire()

        self.log_alarms -= 1

        if self.log_alarms == 0:
            self.gui_footer_log_clear()
            self.logs = []
        else:
            # for some reason having problems with this being empty?
            if len(self.logs) > 0:
                self.logs.pop(0)

            log_pile = []

            for l in self.logs:
                log_pile.append(urwid.AttrMap(urwid.Text(l), 'log'))

            if self.verbose:
                self.gui_footer_log_set(log_pile)

        self.log_lock.release()

    def log(self, msg):
        logging.debug(msg)

        if not self.do_gui:
            if self.verbose:
                print(msg)
            return

        self.log_lock.acquire()

        self.log_alarms += 1
        self.logs.append(msg)

        if len(self.logs) > int(self.config.get_config('max_logs')):
            self.log_alarms -= 1
            self.logs.pop(0)

        log_pile = []
        for l in self.logs:
            log_pile.append(urwid.AttrMap(urwid.Text(l), 'log'))

        if self.verbose:
            self.gui_footer_log_set(log_pile)

        self.nncli_loop.set_alarm_in(
                int(self.config.get_config('log_timeout')),
                self.log_timeout, None)

        self.log_lock.release()

    def gui_update_view(self):
        if not self.do_gui:
            return

        try:
            cur_key = self.view_titles.note_list[self.view_titles.focus_position].note['localkey']
        except IndexError as e:
            cur_key = None
            pass

        self.view_titles.update_note_list(self.view_titles.search_string, sort_mode=self.current_sort_mode)
        self.view_titles.focus_note(cur_key)

        if self.gui_body_get().__class__ == view_note.ViewNote:
            self.view_note.update_note_view()

        self.gui_update_status_bar()

    def gui_update_status_bar(self):
        if self.status_bar != 'yes':
            self.gui_header_clear()
        else:
            self.gui_header_set(self.gui_body_get().get_status_bar())

    def gui_switch_frame_body(self, new_view, save_current_view=True):
        if new_view == None:
            if len(self.last_view) == 0:
                # XXX verify all notes saved...
                self.gui_stop()
            else:
                self.gui_body_set(self.last_view.pop())
        else:
            if self.gui_body_get().__class__ != new_view.__class__:
                if save_current_view:
                    self.last_view.append(self.gui_body_get())
                self.gui_body_set(new_view)

    def delete_note_callback(self, key, delete):
        if not delete:
            return
        note = self.ndb.get_note(key)
        self.ndb.set_note_deleted(key, True)

        if self.gui_body_get().__class__ == view_titles.ViewTitles:
            self.view_titles.update_note_title()

        self.gui_update_status_bar()
        self.ndb.sync_worker_go()

    def gui_yes_no_input(self, args, yes_no):
        self.gui_footer_input_clear()
        self.gui_body_focus()
        self.master_frame.keypress = self.gui_frame_keypress
        args[0](args[1],
                True if yes_no in [ 'YES', 'Yes', 'yes', 'Y', 'y' ]
                     else False)

    def gui_search_input(self, args, search_string):
        self.gui_footer_input_clear()
        self.gui_body_focus()
        self.master_frame.keypress = self.gui_frame_keypress
        if search_string:
            if (self.gui_body_get() == self.view_note):
                self.search_direction = args[1]
                self.view_note.search_note_view_next(search_string=search_string, search_mode=args[0])
            else:
                self.view_titles.update_note_list(search_string, args[0], sort_mode=self.current_sort_mode)
                self.gui_body_set(self.view_titles)

    def gui_category_input(self, args, category):
        self.gui_footer_input_clear()
        self.gui_body_focus()
        self.master_frame.keypress = self.gui_frame_keypress
        if category != None:
            if self.gui_body_get().__class__ == view_titles.ViewTitles:
                note = self.view_titles.note_list[self.view_titles.focus_position].note
            else: # self.gui_body_get().__class__ == view_note.ViewNote:
                note = self.view_note.note

            self.ndb.set_note_category(note['localkey'], category)

            if self.gui_body_get().__class__ == view_titles.ViewTitles:
                self.view_titles.update_note_title()
            else: # self.gui_body_get().__class__ == view_note.ViewNote:
                self.view_note.update_note_view()

            self.gui_update_status_bar()
            self.ndb.sync_worker_go()

    def gui_pipe_input(self, args, cmd):
        self.gui_footer_input_clear()
        self.gui_body_focus()
        self.master_frame.keypress = self.gui_frame_keypress
        if cmd != None:
            if self.gui_body_get().__class__ == view_titles.ViewTitles:
                note = self.view_titles.note_list[self.view_titles.focus_position].note
            else: # self.gui_body_get().__class__ == view_note.ViewNote:
                note = self.view_note.old_note if self.view_note.old_note \
                                               else self.view_note.note
            args = shlex.split(cmd)
            try:
                self.gui_clear()
                pipe = subprocess.Popen(cmd, stdin=subprocess.PIPE, shell=True)
                pipe.communicate(note['content'].encode('utf-8'))
                pipe.stdin.close()
                pipe.wait()
            except OSError as e:
                self.log('Pipe error: ' + str(e))
            finally:
                self.gui_reset()

    def gui_frame_keypress(self, size, key):
        # convert space character into name
        if key == ' ':
            key = 'space'

        lb = self.gui_body_get()

        if key == self.config.get_keybind('quit'):
            self.gui_switch_frame_body(None)

        elif key == self.config.get_keybind('help'):
            self.gui_switch_frame_body(self.view_help)

        elif key == self.config.get_keybind('sync'):
            self.ndb.last_sync = 0
            self.ndb.sync_worker_go()

        elif key == self.config.get_keybind('view_log'):
            self.view_log.update_log()
            self.gui_switch_frame_body(self.view_log)

        elif key == self.config.get_keybind('down'):
            if len(lb.body.positions()) <= 0:
                return None
            last = len(lb.body.positions())
            if lb.focus_position == (last - 1):
                return None
            lb.focus_position += 1
            lb.render(size)

        elif key == self.config.get_keybind('up'):
            if len(lb.body.positions()) <= 0:
                return None
            if lb.focus_position == 0:
                return None
            lb.focus_position -= 1
            lb.render(size)

        elif key == self.config.get_keybind('page_down'):
            if len(lb.body.positions()) <= 0:
                return None
            last = len(lb.body.positions())
            next_focus = lb.focus_position + size[1]
            if next_focus >= last:
                next_focus = last - 1
            lb.change_focus(size, next_focus,
                            offset_inset=0,
                            coming_from='above')

        elif key == self.config.get_keybind('page_up'):
            if len(lb.body.positions()) <= 0:
                return None
            if 'bottom' in lb.ends_visible(size):
                last = len(lb.body.positions())
                next_focus = last - size[1] - size[1]
            else:
                next_focus = lb.focus_position - size[1]
            if next_focus < 0:
                next_focus = 0
            lb.change_focus(size, next_focus,
                            offset_inset=0,
                            coming_from='below')

        elif key == self.config.get_keybind('half_page_down'):
            if len(lb.body.positions()) <= 0:
                return None
            last = len(lb.body.positions())
            next_focus = lb.focus_position + (size[1] // 2)
            if next_focus >= last:
                next_focus = last - 1
            lb.change_focus(size, next_focus,
                            offset_inset=0,
                            coming_from='above')

        elif key == self.config.get_keybind('half_page_up'):
            if len(lb.body.positions()) <= 0:
                return None
            if 'bottom' in lb.ends_visible(size):
                last = len(lb.body.positions())
                next_focus = last - size[1] - (size[1] // 2)
            else:
                next_focus = lb.focus_position - (size[1] // 2)
            if next_focus < 0:
                next_focus = 0
            lb.change_focus(size, next_focus,
                            offset_inset=0,
                            coming_from='below')

        elif key == self.config.get_keybind('bottom'):
            if len(lb.body.positions()) <= 0:
                return None
            lb.change_focus(size, (len(lb.body.positions()) - 1),
                            offset_inset=0,
                            coming_from='above')

        elif key == self.config.get_keybind('top'):
            if len(lb.body.positions()) <= 0:
                return None
            lb.change_focus(size, 0,
                            offset_inset=0,
                            coming_from='below')

        elif key == self.config.get_keybind('view_next_note'):
            if self.gui_body_get().__class__ != view_note.ViewNote:
                return key

            if len(self.view_titles.body.positions()) <= 0:
                return None
            last = len(self.view_titles.body.positions())
            if self.view_titles.focus_position == (last - 1):
                return None
            self.view_titles.focus_position += 1
            lb.update_note_view(
                self.view_titles.note_list[self.view_titles.focus_position].note['localkey'])
            self.gui_switch_frame_body(self.view_note)

        elif key == self.config.get_keybind('view_prev_note'):
            if self.gui_body_get().__class__ != view_note.ViewNote:
                return key

            if len(self.view_titles.body.positions()) <= 0:
                return None
            if self.view_titles.focus_position == 0:
                return None
            self.view_titles.focus_position -= 1
            lb.update_note_view(
                self.view_titles.note_list[self.view_titles.focus_position].note['localkey'])
            self.gui_switch_frame_body(self.view_note)

        elif key == self.config.get_keybind('status'):
            if self.status_bar == 'yes':
                self.status_bar = 'no'
            else:
                self.status_bar = self.config.get_config('status_bar')

        elif key == self.config.get_keybind('create_note'):
            if self.gui_body_get().__class__ != view_titles.ViewTitles:
                return key

            self.gui_clear()
            content = self.exec_cmd_on_note(None)
            self.gui_reset()

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
                if len(lb.body.positions()) <= 0:
                    return None
                note = lb.note_list[lb.focus_position].note
            else: # self.gui_body_get().__class__ == view_note.ViewNote:
                if key == self.config.get_keybind('edit_note'):
                    note = lb.note
                else:
                    note = lb.old_note if lb.old_note else lb.note

            self.gui_clear()
            if key == self.config.get_keybind('edit_note'):
                content = self.exec_cmd_on_note(note)
            elif key == self.config.get_keybind('view_note_ext'):
                content = self.exec_cmd_on_note(note, cmd=self.get_pager())
            else: # key == self.config.get_keybind('view_note_json')
                content = self.exec_cmd_on_note(note, cmd=self.get_pager(), raw=True)

            self.gui_reset()

            if not content:
                return None

            md5_old = hashlib.md5(note['content'].encode('utf-8')).digest()
            md5_new = hashlib.md5(content.encode('utf-8')).digest()

            if md5_old != md5_new:
                self.log('Note updated')
                self.ndb.set_note_content(note['localkey'], content)
                if self.gui_body_get().__class__ == view_titles.ViewTitles:
                    lb.update_note_title()
                else: # self.gui_body_get().__class__ == view_note.ViewNote:
                    lb.update_note_view()
                self.ndb.sync_worker_go()
            else:
                self.log('Note unchanged')

        elif key == self.config.get_keybind('view_note'):
            if self.gui_body_get().__class__ != view_titles.ViewTitles:
                return key

            if len(lb.body.positions()) <= 0:
                return None
            self.view_note.update_note_view(
                    lb.note_list[lb.focus_position].note['localkey'])
            self.gui_switch_frame_body(self.view_note)

        elif key == self.config.get_keybind('pipe_note'):
            if self.gui_body_get().__class__ != view_titles.ViewTitles and \
               self.gui_body_get().__class__ != view_note.ViewNote:
                return key

            if self.gui_body_get().__class__ == view_titles.ViewTitles:
                if len(lb.body.positions()) <= 0:
                    return None
                note = lb.note_list[lb.focus_position].note
            else: # self.gui_body_get().__class__ == view_note.ViewNote:
                note = lb.old_note if lb.old_note else lb.note

            self.gui_footer_input_set(
                urwid.AttrMap(
                    user_input.UserInput(
                        self.config,
                        key,
                        '',
                        self.gui_pipe_input,
                        None),
                    'user_input_bar'))
            self.gui_footer_focus_input()
            self.master_frame.keypress = self.gui_footer_input_get().keypress

        elif key == self.config.get_keybind('note_delete'):
            if self.gui_body_get().__class__ != view_titles.ViewTitles and \
               self.gui_body_get().__class__ != view_note.ViewNote:
                return key

            if self.gui_body_get().__class__ == view_titles.ViewTitles:
                if len(lb.body.positions()) <= 0:
                    return None
                note = lb.note_list[lb.focus_position].note
            else: # self.gui_body_get().__class__ == view_note.ViewNote:
                note = lb.note

            self.gui_footer_input_set(
                urwid.AttrMap(
                    user_input.UserInput(
                        self.config,
                        'Delete (y/n): ',
                        '',
                        self.gui_yes_no_input,
                        [ self.delete_note_callback, note['localkey'] ]),
                    'user_input_bar'))
            self.gui_footer_focus_input()
            self.master_frame.keypress = self.gui_footer_input_get().keypress

        elif key == self.config.get_keybind('note_favorite'):
            if self.gui_body_get().__class__ != view_titles.ViewTitles and \
               self.gui_body_get().__class__ != view_note.ViewNote:
                return key

            if self.gui_body_get().__class__ == view_titles.ViewTitles:
                if len(lb.body.positions()) <= 0:
                    return None
                note = lb.note_list[lb.focus_position].note
            else: # self.gui_body_get().__class__ == view_note.ViewNote:
                note = lb.note

            favorite = not note['favorite']

            self.ndb.set_note_favorite(note['localkey'], favorite)

            if self.gui_body_get().__class__ == view_titles.ViewTitles:
                lb.update_note_title()

            self.ndb.sync_worker_go()

        elif key == self.config.get_keybind('note_category'):
            if self.gui_body_get().__class__ != view_titles.ViewTitles and \
               self.gui_body_get().__class__ != view_note.ViewNote:
                return key

            if self.gui_body_get().__class__ == view_titles.ViewTitles:
                if len(lb.body.positions()) <= 0:
                    return None
                note = lb.note_list[lb.focus_position].note
            else: # self.gui_body_get().__class__ == view_note.ViewNote:
                note = lb.note

            self.gui_footer_input_set(
                urwid.AttrMap(
                    user_input.UserInput(
                        self.config,
                        'Category: ',
                        note['category'],
                        self.gui_category_input,
                        None),
                    'user_input_bar'))
            self.gui_footer_focus_input()
            self.master_frame.keypress = self.gui_footer_input_get().keypress

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
                    'backward' if key == self.config.get_keybind('search_prev_gstyle')
                    or key == self.config.get_keybind('search_prev_regex')
                    else 'forward'
            ]

            caption = '{}{}'.format('(regex) ' if options[0] == 'regex' else '', '/' if options[1] == 'forward' else '?')

            self.gui_footer_input_set(
                urwid.AttrMap(
                    user_input.UserInput(
                        self.config,
                        caption,
                        '',
                        self.gui_search_input,
                        options),
                    'user_input_bar'))
            self.gui_footer_focus_input()
            self.master_frame.keypress = self.gui_footer_input_get().keypress

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

            self.view_titles.update_note_list(None, sort_mode=self.current_sort_mode)
            self.gui_body_set(self.view_titles)

        elif key == self.config.get_keybind('sort_date'):
            if self.gui_body_get().__class__ != view_titles.ViewTitles:
                return key

            self.current_sort_mode = 'date'
            self.view_titles.sort_note_list('date')

        elif key == self.config.get_keybind('sort_alpha'):
            if self.gui_body_get().__class__ != view_titles.ViewTitles:
                return key

            self.current_sort_mode = 'alpha'
            self.view_titles.sort_note_list('alpha')

        elif key == self.config.get_keybind('sort_categories'):
            if self.gui_body_get().__class__ != view_titles.ViewTitles:
                return key

            self.current_sort_mode = 'categories'
            self.view_titles.sort_note_list('categories')

        elif key == self.config.get_keybind('copy_note_text'):
            if self.gui_body_get().__class__ != view_note.ViewNote:
                return key

            self.view_note.copy_note_text()

        else:
            return lb.keypress(size, key)

        self.gui_update_status_bar()
        return None

    def gui_init_view(self, loop, view_note):
        self.master_frame.keypress = self.gui_frame_keypress
        self.gui_body_set(self.view_titles)

        if view_note:
            # note that title view set first to prime the view stack
            self.gui_switch_frame_body(self.view_note)

        self.thread_sync.start()

    def gui_clear(self):
        self.nncli_loop.widget = urwid.Filler(urwid.Text(''))
        self.nncli_loop.draw_screen()

    def gui_reset(self):
        self.nncli_loop.widget = self.master_frame
        self.nncli_loop.draw_screen()

    def gui_stop(self):
        # don't exit if there are any notes not yet saved to the disk

        # NOTE: this was originally causing hangs on exit with urllib2
        # should not be a problem now since using the requests library
        # ref https://github.com/insanum/sncli/issues/18#issuecomment-105517773
        if self.ndb.verify_all_saved():
            # clear the screen and exit the urwid run loop
            self.gui_clear()
            raise urwid.ExitMainLoop()
        else:
            self.log(u'WARNING: Not all notes saved to disk (wait for sync worker)')

    def gui(self, key):

        self.do_gui = True

        self.last_view = []
        self.status_bar = self.config.get_config('status_bar')

        self.log_alarms = 0
        self.log_lock = threading.Lock()

        self.thread_sync = threading.Thread(target=self.ndb.sync_worker,
                                            args=[self.do_server_sync])
        self.thread_sync.setDaemon(True)

        self.view_titles = \
            view_titles.ViewTitles(self.config,
                                   {
                                    'ndb'           : self.ndb,
                                    'search_string' : None,
                                    'log'           : self.log
                                   })
        self.view_note = \
            view_note.ViewNote(self.config,
                               {
                                'ndb' : self.ndb,
                                'id' : key, # initial key to view or None
                                'log' : self.log
                               })

        self.view_log  = view_log.ViewLog(self.config)
        self.view_help = view_help.ViewHelp(self.config)

        palette = \
          [
            ('default',
                self.config.get_color('default_fg'),
                self.config.get_color('default_bg') ),
            ('status_bar',
                self.config.get_color('status_bar_fg'),
                self.config.get_color('status_bar_bg') ),
            ('log',
                self.config.get_color('log_fg'),
                self.config.get_color('log_bg') ),
            ('user_input_bar',
                self.config.get_color('user_input_bar_fg'),
                self.config.get_color('user_input_bar_bg') ),
            ('note_focus',
                self.config.get_color('note_focus_fg'),
                self.config.get_color('note_focus_bg') ),
            ('note_title_day',
                self.config.get_color('note_title_day_fg'),
                self.config.get_color('note_title_day_bg') ),
            ('note_title_week',
                self.config.get_color('note_title_week_fg'),
                self.config.get_color('note_title_week_bg') ),
            ('note_title_month',
                self.config.get_color('note_title_month_fg'),
                self.config.get_color('note_title_month_bg') ),
            ('note_title_year',
                self.config.get_color('note_title_year_fg'),
                self.config.get_color('note_title_year_bg') ),
            ('note_title_ancient',
                self.config.get_color('note_title_ancient_fg'),
                self.config.get_color('note_title_ancient_bg') ),
            ('note_date',
                self.config.get_color('note_date_fg'),
                self.config.get_color('note_date_bg') ),
            ('note_flags',
                self.config.get_color('note_flags_fg'),
                self.config.get_color('note_flags_bg') ),
            ('note_category',
                self.config.get_color('note_category_fg'),
                self.config.get_color('note_category_bg') ),
            ('note_content',
                self.config.get_color('note_content_fg'),
                self.config.get_color('note_content_bg') ),
            ('note_content_focus',
                self.config.get_color('note_content_focus_fg'),
                self.config.get_color('note_content_focus_bg') ),
            ('note_content_old',
                self.config.get_color('note_content_old_fg'),
                self.config.get_color('note_content_old_bg') ),
            ('note_content_old_focus',
                self.config.get_color('note_content_old_focus_fg'),
                self.config.get_color('note_content_old_focus_bg') ),
            ('help_focus',
                self.config.get_color('help_focus_fg'),
                self.config.get_color('help_focus_bg') ),
            ('help_header',
                self.config.get_color('help_header_fg'),
                self.config.get_color('help_header_bg') ),
            ('help_config',
                self.config.get_color('help_config_fg'),
                self.config.get_color('help_config_bg') ),
            ('help_value',
                self.config.get_color('help_value_fg'),
                self.config.get_color('help_value_bg') ),
            ('help_descr',
                self.config.get_color('help_descr_fg'),
                self.config.get_color('help_descr_bg') )
          ]

        self.master_frame = urwid.Frame(body=urwid.Filler(urwid.Text('')),
                                        header=None,
                                        footer=urwid.Pile([ urwid.Pile([]),
                                                            urwid.Pile([]) ]),
                                        focus_part='body')

        self.nncli_loop = urwid.MainLoop(self.master_frame,
                                         palette,
                                         handle_mouse=False)

        self.nncli_loop.set_alarm_in(0, self.gui_init_view,
                                     True if key else False)

        self.nncli_loop.run()

    def cli_list_notes(self, regex, search_string):

        note_list, match_regex, all_notes_cnt = \
            self.ndb.filter_notes(
                    search_string,
                    search_mode='regex' if regex else 'gstyle',
                    sort_mode=self.config.get_config('sort_mode'))
        for n in note_list:
            flags = utils.get_note_flags(n.note)
            print((str(n.key) + \
                  ' [' + flags + '] ' + \
                  utils.get_note_title(n.note)))

    def cli_note_dump(self, key):

        note = self.ndb.get_note(key)
        if not note:
            self.log('ERROR: Key does not exist')
            return

        w = 60
        sep = '+' + '-'*(w+2) + '+'
        t = time.localtime(float(note['modified']))
        mod_time = time.strftime('%a, %d %b %Y %H:%M:%S', t)
        title = utils.get_note_title(note)
        flags = utils.get_note_flags(note)
        category  = utils.get_note_category(note)

        print(sep)
        print(('| {:<' + str(w) + '} |').format(('    Title: ' + title)[:w]))
        print(('| {:<' + str(w) + '} |').format(('      Key: ' + str(note.get('id', 'Localkey: {}'.format(note.get('localkey'))))[:w])))
        print(('| {:<' + str(w) + '} |').format(('     Date: ' + mod_time)[:w]))
        print(('| {:<' + str(w) + '} |').format(('     Category: ' + category)[:w]))
        print(('| {:<' + str(w) + '} |').format(('    Flags: [' + flags + ']')[:w]))
        print(sep)
        print((note['content']))

    def cli_dump_notes(self, regex, search_string):

        note_list, match_regex, all_notes_cnt = \
            self.ndb.filter_notes(
                    search_string,
                    search_mode='regex' if regex else 'gstyle',
                    sort_mode=self.config.get_config('sort_mode'))
        for n in note_list:
            self.cli_note_dump(n.key)

    def cli_note_create(self, from_stdin, title):

        if from_stdin:
            content = ''.join(sys.stdin)
        else:
            content = self.exec_cmd_on_note(None)

        if title:
            content = title + '\n\n' + content if content else ''

        if content:
            self.log('New note created')
            self.ndb.create_note(content)
            self.sync_notes()

    def cli_note_import(self, from_stdin):

        if from_stdin:
            raw = ''.join(sys.stdin)
        else:
            raw = self.exec_cmd_on_note(None)

        if raw:
            try:
                note = json.loads(raw)
                self.log('New note created')
                self.ndb.import_note(note)
                self.sync_notes()
            except json.decoder.JSONDecodeError as e:
                self.log('(IMPORT) Decoding JSON has failed: {}'.format(e))
                sys.exit(1)
            except ValueError as e:
                self.log('(IMPORT) ValueError: {}'.format(e))
                sys.exit(1)

    def cli_note_export(self, key):

        note = self.ndb.get_note(key)
        if not note:
            self.log('ERROR: Key does not exist')
            return

        print(json.dumps(note, indent=2))

    def cli_export_notes(self, regex, search_string):

        note_list, match_regex, all_notes_cnt = \
            self.ndb.filter_notes(
                    search_string,
                    search_mode='regex' if regex else 'gstyle',
                    sort_mode=self.config.get_config('sort_mode'))

        notes_data = [n.note for n in note_list]
        print(json.dumps(notes_data, indent=2))

    def cli_note_edit(self, key):

        note = self.ndb.get_note(key)
        if not note:
            self.log('ERROR: Key does not exist')
            return

        content = self.exec_cmd_on_note(note)
        if not content:
            return

        md5_old = hashlib.md5(note['content'].encode('utf-8')).digest()
        md5_new = hashlib.md5(content.encode('utf-8')).digest()

        if md5_old != md5_new:
            self.log('Note updated')
            self.ndb.set_note_content(note['localkey'], content)
            self.sync_notes()
        else:
            self.log('Note unchanged')

    def cli_note_delete(self, key, delete):

        note = self.ndb.get_note(key)
        if not note:
            self.log('ERROR: Key does not exist')
            return

        self.ndb.set_note_deleted(key, delete)
        self.sync_notes()

    def cli_note_favorite(self, key, favorite):

        note = self.ndb.get_note(key)
        if not note:
            self.log('ERROR: Key does not exist')
            return

        self.ndb.set_note_favorite(key, favorite)
        self.sync_notes()

    def cli_note_category_get(self, key):

        note = self.ndb.get_note(key)
        if not note:
            self.log('ERROR: Key does not exist')
            return

        category = utils.get_note_category(note)
        return category

    def cli_note_category_set(self, key, category):

        note = self.ndb.get_note(key)
        if not note:
            self.log('Error: Key does not exist')
            return

        self.ndb.set_note_category(key, category.lower())
        self.sync_notes()

    def cli_note_category_rm(self, key):

        note = self.ndb.get_note(key)
        if not note:
            self.log('Error: Key does not exist')
            return

        old_category = self.cli_note_category_get(key)
        if old_category:
            self.cli_note_category_set(key, '')

def SIGINT_handler(signum, frame):
    print('\nSignal caught, bye!')
    sys.exit(1)

signal.signal(signal.SIGINT, SIGINT_handler)

def usage():
    print ('''
Usage:
 nncli [OPTIONS] [COMMAND] [COMMAND_ARGS]

 OPTIONS:
  -h, --help                  - usage help
  -v, --verbose               - verbose output
  -n, --nosync                - don't perform a server sync
  -r, --regex                 - search string is a regular expression
  -k <key>, --key=<key>       - note key
  -t <title>, --title=<title> - title of note for create (cli mode)
  -c <file>, --config=<file>  - config file to read from (defaults to
                                ~/.config/nncli/config)

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
''')
    sys.exit(0)


def main(argv=sys.argv[1:]):
    verbose = False
    sync    = True
    regex   = False
    key     = None
    title   = None
    config  = None

    try:
        opts, args = getopt.getopt(argv,
            'hvnrk:t:c:',
            [ 'help', 'verbose', 'nosync', 'regex', 'key=', 'title=', 'config=' ])
    except:
        usage()

    for opt, arg in opts:
        if opt in [ '-h', '--help']:
            usage()
        elif opt in [ '-v', '--verbose']:
            verbose = True
        elif opt in [ '-n', '--nosync']:
            sync = False
        elif opt in [ '-r', '--regex']:
            regex = True
        elif opt in [ '-k', '--key']:
            try:
                key = int(arg)
            except:
                print('ERROR: Key specified with -k must be an integer')
        elif opt in [ '-t', '--title']:
            title = arg
        elif opt in [ '-c', '--config']:
            config = arg
        else:
            print('ERROR: Unhandled option')
            usage()

    if not args:
        nncli(sync, verbose, config).gui(key)
        return

    def nncli_start(sync=sync, verbose=verbose, config=config):
        sn = nncli(sync, verbose, config)
        if sync: sn.sync_notes()
        return sn

    if args[0] == 'sync':
        sn = nncli_start(True)

    elif args[0] == 'list':

        sn = nncli_start()
        sn.cli_list_notes(regex, ' '.join(args[1:]))

    elif args[0] == 'dump':

        sn = nncli_start()
        if key:
            sn.cli_note_dump(key)
        else:
            sn.cli_dump_notes(regex, ' '.join(args[1:]))

    elif args[0] == 'create':

        if len(args) == 1:
            sn = nncli_start()
            sn.cli_note_create(False, title)
        elif len(args) == 2 and args[1] == '-':
            sn = nncli_start()
            sn.cli_note_create(True, title)
        else:
            usage()

    elif args[0] == 'import':

        if len(args) == 1:
            sn = nncli_start()
            sn.cli_note_import(False)
        elif len(args) == 2 and args[1] == '-':
            sn = nncli_start()
            sn.cli_note_import(True)
        else:
            usage()

    elif args[0] == 'export':

        sn = nncli_start()
        if key:
            sn.cli_note_export(key)
        else:
            sn.cli_export_notes(regex, ' '.join(args[1:]))

    elif args[0] == 'edit':

        if not key:
            usage()

        sn = nncli_start()
        sn.cli_note_edit(key)

    elif args[0] == 'delete':

        if not key:
            usage()

        sn = nncli_start()
        sn.cli_note_delete(key, True)

    elif args[0] == 'favorite' or args[0] == 'unfavorite':

        if not key:
            usage()

        sn = nncli_start()
        sn.cli_note_favorite(key, 1 if args[0] == 'favorite' else 0)

    # Category API
    elif args[0] == 'cat':

        if not key:
            usage()

        nargs = len(args)
        correct_other = (args[1] in ['get', 'rm'] and nargs == 2)
        correct_set = (args[1] == 'set' and nargs == 3)
        if not (correct_set or correct_other):
            usage()

        if args[1] == 'get':

            sn = nncli_start()
            category = sn.cli_note_category_get(key)
            if category:
                print(category)

        elif args[1] == 'set':

            category = args[2]
            sn = nncli_start()
            sn.cli_note_category_set(key, category)

        elif args[1] == 'rm':

            sn = nncli_start()
            sn.cli_note_category_rm(key)

    else:
        usage()

