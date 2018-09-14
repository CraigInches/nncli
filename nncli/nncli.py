# -*- coding: utf-8 -*-
"""nncli module"""
import hashlib
import json
import os
import signal
import sys
import time

from . import utils, __version__
from .config import Config
from .gui import NncliGui
from .log import Logger
from .notes_db import NotesDB, ReadError, WriteError
from .utils import exec_cmd_on_note

# pylint: disable=unused-argument
class Nncli:
    """Nncli class. Responsible for most of the application logic"""
    def __init__(self, do_server_sync, verbose=False, config_file=None):
        self.config = Config(config_file)
        self.config.state.do_server_sync = do_server_sync
        self.config.state.verbose = verbose
        force_full_sync = False

        if not os.path.exists(self.config.get_config('db_path')):
            os.mkdir(self.config.get_config('db_path'))
            force_full_sync = True

        self.logger = Logger(self.config)

        try:
            self.ndb = NotesDB(
                    self.config,
                    self.logger.log
                    )
        except (ReadError, WriteError) as ex:
            self.logger.log(str(ex))
            sys.exit(1)

        self.nncli_gui = NncliGui(self.config, self.logger, self.ndb)
        self.ndb.set_update_view(self.nncli_gui.gui_update_view)

        if force_full_sync:
            # The note database doesn't exist so force a full sync. It is
            # important to do this outside of the gui because an account
            # with hundreds of notes will cause a recursion panic under
            # urwid. This simple workaround gets the job done. :-)
            self.config.state.verbose = True
            self.logger.log('nncli database doesn\'t exist,'
                            ' forcing full sync...')
            self.ndb.sync_now()
            self.config.state.verbose = verbose

    def gui(self, key):
        """Method to initialize and display the GUI"""
        self.config.state.do_gui = True
        self.ndb.log = self.nncli_gui.log
        self.nncli_gui.run()

    def cli_list_notes(self, regex, search_string):
        """List the notes on the command line"""
        note_list, _, _ = \
            self.ndb.filter_notes(
                    search_string,
                    search_mode='regex' if regex else 'gstyle',
                    sort_mode=self.config.get_config('sort_mode'))
        for nnote in note_list:
            flags = utils.get_note_flags(nnote.note)
            print((str(nnote.key) + \
                  ' [' + flags + '] ' + \
                  utils.get_note_title(nnote.note)))

    def cli_note_dump(self, key):
        """Dump a note to the command line"""
        note = self.ndb.get_note(key)
        if not note:
            self.logger.log('ERROR: Key does not exist')
            return

        width = 60
        sep = '+' + '-' * (width + 2) + '+'
        localtime = time.localtime(float(note['modified']))
        mod_time = time.strftime('%a, %d %b %Y %H:%M:%S', localtime)
        title = utils.get_note_title(note)
        flags = utils.get_note_flags(note)
        category = utils.get_note_category(note)

        print(sep)
        print(('| {:<' + str(width) + '} |').format(
                ('    Title: ' + title)[:width]))
        print(('| {:<' + str(width) + '} |').format(
                ('      Key: ' +
                 str(note.get(
                         'id',
                         'Localkey: {}'.format(note.get('localkey'))
                         )
                    )[:width]
                )))
        print(('| {:<' + str(width) + '} |').format(
                ('     Date: ' + mod_time)[:width]))
        print(('| {:<' + str(width) + '} |').format(
                ('     Category: ' + category)[:width]))
        print(('| {:<' + str(width) + '} |').format(
                ('    Flags: [' + flags + ']')[:width]))
        print(sep)
        print((note['content']))

    def cli_dump_notes(self, regex, search_string):
        """Dump multiple notes to the command line"""
        note_list, _, _ = \
            self.ndb.filter_notes(
                    search_string,
                    search_mode='regex' if regex else 'gstyle',
                    sort_mode=self.config.get_config('sort_mode'))
        for note in note_list:
            self.cli_note_dump(note.key)

    def cli_note_create(self, from_stdin, title):
        """Create a new note from the command line"""
        if from_stdin:
            content = ''.join(sys.stdin)
        else:
            content = exec_cmd_on_note(None, self.config, self.nncli_gui,
                                       self.logger)

        if title:
            content = title + '\n\n' + content if content else ''

        if content:
            self.logger.log('New note created')
            self.ndb.create_note(content)
            self.ndb.sync_now()

    def cli_note_import(self, from_stdin):
        """Import a note from the command line"""
        if from_stdin:
            raw = ''.join(sys.stdin)
        else:
            raw = exec_cmd_on_note(None, self.config, self.nncli_gui,
                                   self.logger)

        if raw:
            try:
                note = json.loads(raw)
                self.logger.log('New note created')
                self.ndb.import_note(note)
                self.ndb.sync_now()
            except ValueError as ex:
                self.logger.log('(IMPORT) ValueError: {}'.format(ex))
                sys.exit(1)

    def cli_note_export(self, key):
        """Export a note to the command line"""
        note = self.ndb.get_note(key)
        if not note:
            self.logger.log('ERROR: Key does not exist')
            return

        print(json.dumps(note, indent=2))

    def cli_export_notes(self, regex, search_string):
        """Export multiple notes to the command line"""
        note_list, _, _ = \
            self.ndb.filter_notes(
                    search_string,
                    search_mode='regex' if regex else 'gstyle',
                    sort_mode=self.config.get_config('sort_mode'))

        notes_data = [n.note for n in note_list]
        print(json.dumps(notes_data, indent=2))

    def cli_note_edit(self, key):
        """Edit a note from the command line"""
        note = self.ndb.get_note(key)
        if not note:
            self.logger.log('ERROR: Key does not exist')
            return

        content = exec_cmd_on_note(note, self.config, self.nncli_gui,
                                   self.logger)
        if not content:
            return

        md5_old = hashlib.md5(note['content'].encode('utf-8')).digest()
        md5_new = hashlib.md5(content.encode('utf-8')).digest()

        if md5_old != md5_new:
            self.logger.log('Note updated')
            self.ndb.set_note_content(note['localkey'], content)
            self.ndb.sync_now()
        else:
            self.logger.log('Note unchanged')

    def cli_note_delete(self, key, delete):
        """Delete a note from the command line"""
        note = self.ndb.get_note(key)
        if not note:
            self.logger.log('ERROR: Key does not exist')
            return

        self.ndb.set_note_deleted(key, delete)
        self.ndb.sync_now()

    def cli_note_favorite(self, key, favorite):
        """Favorite a note from the command line"""
        note = self.ndb.get_note(key)
        if not note:
            self.logger.log('ERROR: Key does not exist')
            return

        self.ndb.set_note_favorite(key, favorite)
        self.ndb.sync_now()

    def cli_note_category_get(self, key):
        """Get a note category from the command line"""
        note = self.ndb.get_note(key)
        if not note:
            self.logger.log('ERROR: Key does not exist')
            return ''

        category = utils.get_note_category(note)
        return category

    def cli_note_category_set(self, key, category):
        """Set a note category from the command line"""
        note = self.ndb.get_note(key)
        if not note:
            self.logger.log('Error: Key does not exist')
            return

        self.ndb.set_note_category(key, category.lower())
        self.ndb.sync_now()

    def cli_note_category_rm(self, key):
        """Remove a note category from the command line"""
        note = self.ndb.get_note(key)
        if not note:
            self.logger.log('Error: Key does not exist')
            return

        old_category = self.cli_note_category_get(key)
        if old_category:
            self.cli_note_category_set(key, '')

def sigint_handler(signum, frame):
    """Handle sigint"""
    print('\nSignal caught, bye!')
    sys.exit(1)

signal.signal(signal.SIGINT, sigint_handler)
