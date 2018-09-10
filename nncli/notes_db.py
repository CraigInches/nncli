# -*- coding: utf-8 -*-
"""notes_db module"""
import copy
import glob
import json
import os
import re
import threading
import time
from requests.exceptions import RequestException

from . import utils
from .nextcloud_note import NextcloudNote

# pylint: disable=too-many-instance-attributes, too-many-locals
# pylint: disable=too-many-branches, too-many-statements
class ReadError(RuntimeError):
    """Exception thrown on a read error"""
    pass

class WriteError(RuntimeError):
    """Exception thrown on a write error"""
    pass

class NotesDB():
    """
    NotesDB will take care of the local notes database and syncing with
    NextCloud Notes
    """
    def __init__(self, config, log, update_view=None):
        self.config = config
        self.log = log
        self.update_view = update_view

        self.last_sync = 0 # set to zero to trigger a full sync
        self.sync_lock = threading.Lock()
        self.go_cond = threading.Condition()

        # create db dir if it does not exist
        if not os.path.exists(self.config.get_config('db_path')):
            os.mkdir(self.config.get_config('db_path'))

        now = int(time.time())
        # now read all .json files from disk
        fnlist = glob.glob(self._helper_key_to_fname('*'))

        self.notes = {}

        for func in fnlist:
            try:
                note = json.load(open(func, 'r'))
            except IOError as ex:
                raise ReadError('Error opening {0}: {1}'.format(func, str(ex)))
            except ValueError as ex:
                raise ReadError('Error reading {0}: {1}'.format(func, str(ex)))
            else:
                # we always have a localkey, also when we don't have a
                # note['id'] yet (no sync)
                localkey = note.get(
                        'localkey',
                        os.path.splitext(os.path.basename(func))[0]
                        )
                # we maintain in memory a timestamp of the last save
                # these notes have just been read, so at this moment
                # they're in sync with the disc.
                note['savedate'] = now
                # set a localkey to each note in memory
                # Note: 'id' is used only for syncing with server - 'localkey'
                #       is used for everything else in nncli
                note['localkey'] = localkey

                # add the note to our database
                self.notes[localkey] = note

        # initialise the NextCloud instance we're going to use
        # this does not yet need network access
        self.note = NextcloudNote(self.config.get_config('nn_username'),
                                  self.config.get_config('nn_password'),
                                  self.config.get_config('nn_host'))

    def set_update_view(self, update_view):
        """Set the update_view method"""
        self.update_view = update_view

    def _filtered_notes_sort(self, filtered_notes, sort_mode='date'):
        """Sort filtered note set"""
        if sort_mode == 'date':
            if self.config.get_config('favorite_ontop') == 'yes':
                filtered_notes.sort(key=utils.sort_by_modify_date_favorite,
                                    reverse=True)
            else:
                filtered_notes.sort(
                        key=lambda o: -float(o.note.get('modified', 0))
                        )
        elif sort_mode == 'alpha':
            if self.config.get_config('favorite_ontop') == 'yes':
                filtered_notes.sort(key=utils.sort_by_title_favorite)
            else:
                filtered_notes.sort(key=lambda o: utils.get_note_title(o.note))
        elif sort_mode == 'categories':
            favorite = self.config.get_config('favorite_ontop')
            utils.sort_notes_by_categories(filtered_notes, \
                    favorite_ontop=favorite)

    def filter_notes(self, search_string=None, search_mode='gstyle',
                     sort_mode='date'):
        """Return list of notes filtered with search string.

        Based on the search mode that has been selected in self.config,
        this method will call the appropriate helper method to do the
        actual work of filtering the notes.

        Returns a list of filtered notes with selected search mode and sorted
        according to configuration. Two more elements in tuple: a regular
        expression that can be used for highlighting strings in the text widget
        and the total number of notes in memory.
        """

        if search_mode == 'gstyle':
            filtered_notes, match_regexp, active_notes = \
                self._filter_notes_gstyle(search_string)
        else:
            filtered_notes, match_regexp, active_notes = \
                self._filter_notes_regex(search_string)

        self._filtered_notes_sort(filtered_notes, sort_mode)

        return filtered_notes, match_regexp, active_notes

    @staticmethod
    def _helper_gstyle_categorymatch(cat_pats, note):
        """Match categories using a Google-style search string"""
        # Returns:
        #  2 = match    - no category patterns specified
        #  1 = match    - all category patterns match a category on this
        #                 note
        #  0 = no match - note has no category or not all category
        #                 patterns match

        if not cat_pats:
            # match because no category patterns were specified
            return 2

        note_category = note.get('category')

        if not note_category:
            # category patterns specified but note has no categories,
            # so no match
            return 0

        # for each cat_pat, we have to find a matching category
        # .lower() used for case-insensitive search
        cat_pats_matched = 0
        for cat_pat in cat_pats:
            cat_pat = cat_pat.lower()
            for pat in note_category:
                if cat_pat in pat.lower():
                    cat_pats_matched += 1
                    break

        if cat_pats_matched == len(cat_pats):
            # all category patterns specified matched a category on this note
            return 1

        # note doesn't match
        return 0

    @staticmethod
    def _helper_gstyle_wordmatch(word_pats, content):
        """Match note contents based no a Google-style search string"""
        if not word_pats:
            return True

        word_pats_matched = 0
        lowercase_content = content.lower() # case insensitive search
        for word_pat in word_pats:
            word_pat = word_pat.lower() # case insensitive search
            if word_pat in lowercase_content:
                word_pats_matched += 1

        if word_pats_matched == len(word_pats):
            return True

        return False

    def _filter_notes_gstyle(self, search_string=None):
        """Filter the notes based of a Google-style search string"""
        filtered_notes = []
        active_notes = 0

        if not search_string:
            for key in self.notes:
                note = self.notes[key]
                active_notes += 1
                filtered_notes.append(
                        utils.KeyValueObject(key=key, note=note, catfound=0)
                        )

            return filtered_notes, [], active_notes

        # group0: category:([^\s]+)
        # group1: multiple words in quotes
        # group2: single words

        # example result for: 'category:category1 category:category2
        # word1 "word2 word3" category:category3'
        # [ ('category1', '',            ''),
        #   ('category2', '',            ''),
        #   ('',     '',            'word1'),
        #   ('',     'word2 word3', ''),
        #   ('category3', '',            '') ]

        groups = re.findall(
                r'category:([^\s]+)|"([^"]+)"|([^\s]+)', search_string
                )
        all_pats = [[] for _ in range(3)]

        # we end up with [[cat_pats],[multi_word_pats],[single_word_pats]]
        for group in groups:
            for i in range(3):
                if group[i]:
                    all_pats[i].append(group[i])

        for key in self.notes:
            note = self.notes[key]

            active_notes += 1

            catmatch = self._helper_gstyle_categorymatch(all_pats[0],
                                                         note)

            word_pats = all_pats[1] + all_pats[2]

            if catmatch and \
               self._helper_gstyle_wordmatch(word_pats, note.get('content')):
                # we have a note that can go through!
                filtered_notes.append(
                        utils.KeyValueObject(key=key,
                                             note=note,
                                             catfound=1 \
                                                     if catmatch == 1 \
                                                     else 0))

        return filtered_notes, '|'.join(all_pats[1] + all_pats[2]), active_notes

    def _filter_notes_regex(self, search_string=None):
        """
        Return a list of notes filtered using the regex search_string.
        Each element in the list is a tuple (local_key, note).
        """
        sspat = utils.build_regex_search(search_string)

        filtered_notes = []
        active_notes = 0 # total number of notes, including deleted ones

        for key in self.notes:
            note = self.notes[key]

            active_notes += 1

            if not sspat:
                filtered_notes.append(
                        utils.KeyValueObject(key=key, note=note, catfound=0)
                        )
                continue

            if self.config.get_config('search_categories') == 'yes':
                cat_matched = False
                for cat in note.get('category'):
                    if sspat.search(cat):
                        cat_matched = True
                        filtered_notes.append(
                                utils.KeyValueObject(key=key,
                                                     note=note, catfound=1)
                                )
                        break
                if cat_matched:
                    continue

            if sspat.search(note.get('content')):
                filtered_notes.append(
                        utils.KeyValueObject(key=key, note=note, catfound=0)
                        )

        match_regexp = search_string if sspat else ''
        return filtered_notes, match_regexp, active_notes

    def import_note(self, note):
        """Import a note into the database"""
        # need to get a key unique to this database. not really important
        # what it is, as long as it's unique.
        new_key = note['id'] if note.get('id') else utils.generate_random_key()
        while new_key in self.notes:
            new_key = utils.generate_random_key()

        timestamp = int(time.time())

        try:
            modified = float(note.get('modified', timestamp))
        except ValueError:
            raise ValueError('date fields must be numbers or string'
                             'representations of numbers')

        # note has no internal key yet.
        new_note = \
                {
                        'content'  : note.get('content', ''),
                        'modified' : modified,
                        'title'    : note.get('title'),
                        'category' : note.get('category') \
                                if note.get('category') is not None \
                                else '',
                        'savedate'   : 0, # never been written to disc
                        'syncdate'   : 0, # never been synced with server
                        'favorite' : False,
                        'deleted'  : False
                }

        # sanity check all note values
        if not isinstance(new_note['content'], str):
            raise ValueError('"content" must be a string')

        if not 0 <= new_note['modified'] <= timestamp:
            raise ValueError('"modified" field must be real')

        if not isinstance(new_note['category'], str) or \
                new_note['category'] is None:
            raise ValueError('"category" must be an string')

        if not isinstance(new_note['favorite'], bool):
            raise ValueError('"favorite" must be a boolean')

        self.notes[new_key] = new_note

        return new_key

    def create_note(self, content):
        """Create a new note in the database"""
        # need to get a key unique to this database. not really important
        # what it is, as long as it's unique.
        new_key = utils.generate_random_key()
        while new_key in self.notes:
            new_key = utils.generate_random_key()

        timestamp = int(time.time())
        title = content.split('\n')[0]

        # note has no internal key yet.
        new_note = \
                {
                        'localkey' : new_key,
                        'content'  : content,
                        'modified' : timestamp,
                        'category' : '',
                        'savedate' : 0, # never been written to disc
                        'syncdate' : 0, # never been synced with server
                        'favorite' : False,
                        'deleted'  : False,
                        'title'    : title
                }

        self.notes[new_key] = new_note

        return new_key

    def get_note(self, key):
        """Get a note from the database"""
        return self.notes[key]

    @staticmethod
    def _flag_what_changed(note, what_changed):
        """Flag a note field as changed"""
        if 'what_changed' not in note:
            note['what_changed'] = []
        if what_changed not in note['what_changed']:
            note['what_changed'].append(what_changed)

    def set_note_deleted(self, key, deleted):
        """Mark a note for deletion"""
        note = self.notes[key]
        old_deleted = note['deleted'] if 'deleted' in note else 0
        if old_deleted != deleted:
            note['deleted'] = deleted
            note['modified'] = int(time.time())
            self._flag_what_changed(note, 'deleted')
            self.log('Note marked for deletion (key={0})'.format(key))

    def set_note_content(self, key, content):
        """Set the content of a note in the database"""
        note = self.notes[key]
        old_content = note.get('content')
        if content != old_content:
            note['content'] = content
            note['modified'] = int(time.time())
            self._flag_what_changed(note, 'content')
            self.log('Note content updated (key={0})'.format(key))

    def set_note_category(self, key, category):
        """Set the category of a note in the database"""
        note = self.notes[key]
        old_category = note.get('category')
        if category != old_category:
            note['category'] = category
            note['modified'] = int(time.time())
            self._flag_what_changed(note, 'category')
            self.log('Note category updated (key={0})'.format(key))

    def set_note_favorite(self, key, favorite):
        """Mark a note in the database as a favorite"""
        note = self.notes[key]
        old_favorite = utils.note_favorite(note)
        if favorite != old_favorite:
            note['favorite'] = favorite
            note['modified'] = int(time.time())
            self._flag_what_changed(note, 'favorite')
            self.log('Note {0} (key={1})'. \
                    format('favorite' if favorite else \
                    'unfavorited', key))

    def _helper_key_to_fname(self, k):
        """Convert a note key into a file name"""
        return os.path.join(self.config.get_config('db_path'), str(k)) + '.json'

    def _helper_save_note(self, k, note):
        """Save a note to the file system"""
        # Save a single note to disc.
        func = self._helper_key_to_fname(k)
        json.dump(note, open(func, 'w'), indent=2)

        # record that we saved this to disc.
        note['savedate'] = int(time.time())

    def _sync_notes(self, server_sync=True, full_sync=True):
        """Perform a full bi-directional sync with server.

        Psuedo-code algorithm for syncing:

            1. for any note changed locally, including new notes:
                   save note to server, update note with response
                   (new title, modified, title, category, content,
                    favorite)

            2. get all notes

            3. for each remote note
                   if remote modified > local modified ||
                      a new note and key is not in local store
                       retrieve note, update note with response

            4. for each local note not in the index
                   PERMANENT DELETE, remove note from local store
        """

        local_updates = {}
        local_deletes = {}
        server_keys = {}
        now = int(time.time())

        sync_start_time = int(time.time())
        sync_errors = 0
        skip_remote_syncing = False

        if server_sync and full_sync:
            self.log("Starting full sync")

        # 1. for any note changed locally, including new notes:
        #        save note to server, update note with response
        for _, local_key in enumerate(self.notes.keys()):
            note = self.notes[local_key]

            if not note.get('id') or \
               float(note.get('modified')) > float(note.get('syncdate')):

                savedate = float(note.get('savedate'))
                if float(note.get('modified')) > savedate or \
                   float(note.get('syncdate')) > savedate:
                    # this will trigger a save to disk after sync algorithm
                    # we want this note saved even if offline or sync fails
                    local_updates[local_key] = True

                if not server_sync:
                    # the 'what_changed' field will be written to disk and
                    # picked up whenever the next full server sync occurs
                    continue

                # only send required fields
                cnote = copy.deepcopy(note)
                if 'what_changed' in note:
                    del note['what_changed']

                if 'localkey' in cnote:
                    del cnote['localkey']

                if 'minversion' in cnote:
                    del cnote['minversion']
                del cnote['syncdate']
                del cnote['savedate']
                del cnote['deleted']
                if 'etag' in cnote:
                    del cnote['etag']
                if 'title' in cnote:
                    del cnote['title']

                if 'what_changed' in cnote:
                    if 'content' not in cnote['what_changed'] \
                            and 'category' not in cnote['what_changed']:
                        del cnote['content']
                    if 'category' not in cnote['what_changed']:
                        del cnote['category']
                    if 'favorite' not in cnote['what_changed']:
                        del cnote['favorite']
                    del cnote['what_changed']

                try:
                    if note['deleted']:
                        uret = self.note.delete_note(cnote)
                    else:
                        uret = self.note.update_note(cnote)

                    # if this is a new note our local key is not valid anymore
                    # merge the note we got back (content could be empty)
                    # record syncdate and save the note at the assigned key
                    del self.notes[local_key]
                    key = uret[0].get('id')
                    category = uret[0].get('category')
                    category = category if category is not None else ''
                    note.update(uret[0])
                    note['syncdate'] = now
                    note['localkey'] = key
                    note['category'] = category
                    self.notes[key] = note

                    local_updates[key] = True
                    if local_key != key:
                        # if local_key was a different key it should be deleted
                        local_deletes[local_key] = True
                        if local_key in local_updates:
                            del local_updates[local_key]

                    self.log(
                            'Synced note to server (key={0})'.format(local_key)
                            )
                except (ConnectionError, RequestException, ValueError):
                    self.log(
                            'ERROR: Failed to sync note to server (key={0})'.
                            format(local_key)
                            )
                    sync_errors += 1

        # 2. get the note index
        if not server_sync:
            note_list = []
        else:
            note_list = self.note.get_note_list()

            if note_list[1] == 0:  # success
                note_list = note_list[0]
            else:
                self.log('ERROR: Failed to get note list from server')
                sync_errors += 1
                note_list = []
                skip_remote_syncing = True

        # 3. for each remote note
        #        if remote modified > local modified ||
        #           a new note and key is not in local store
        #            retrieve note, update note with response
        if not skip_remote_syncing:
            for _, note in enumerate(note_list):
                key = note.get('id')
                category = note.get('category') \
                        if note.get('category') is not None \
                        else ''
                server_keys[key] = True
                # this works because in the prior step we rewrite local keys to
                # server keys when we get an updated note back from the server
                if key in self.notes:
                    # we already have this note
                    # if the server note has a newer syncnum we need to get it
                    if int(note.get('modified')) > \
                            int(self.notes[key].get('modified')):
                        gret = self.note.get_note(key)
                        if gret[1] == 0:
                            self.notes[key].update(gret[0])
                            local_updates[key] = True
                            self.notes[key]['syncdate'] = now
                            self.notes[key]['localkey'] = key
                            self.notes[key]['category'] = category
                            self.notes[key]['deleted'] = False

                            self.log(
                                    'Synced newer note from server (key={0})'.
                                    format(key)
                                    )
                        else:
                            self.log(
                                    'ERROR: Failed to sync newer note '
                                    'from server (key={0})'.format(key)
                                    )
                            sync_errors += 1
                else:
                    # this is a new note
                    gret = self.note.get_note(key)
                    if gret[1] == 0:
                        self.notes[key] = gret[0]
                        local_updates[key] = True
                        self.notes[key]['syncdate'] = now
                        self.notes[key]['localkey'] = key
                        self.notes[key]['category'] = category
                        self.notes[key]['deleted'] = False

                        self.log(
                                'Synced new note from server (key={0})'.
                                format(key)
                                )
                    else:
                        self.log(
                                'ERROR: Failed syncing new note from'
                                'server (key={0})'.format(key)
                                )
                        sync_errors += 1

        # 4. for each local note not in the index
        #        PERMANENT DELETE, remove note from local store
        # Only do this when a full sync (i.e. entire index) is performed!
        if server_sync and full_sync and not skip_remote_syncing:
            for local_key in list(self.notes.keys()):
                if local_key not in server_keys:
                    del self.notes[local_key]
                    local_deletes[local_key] = True

        # sync done, now write changes to db_path

        for k in list(local_updates.keys()):
            try:
                self._helper_save_note(k, self.notes[k])
            except WriteError as ex:
                raise WriteError(str(ex))
            self.log("Saved note to disk (key={0})".format(key))

        for k in list(local_deletes.keys()):
            fnote = self._helper_key_to_fname(k)
            if os.path.exists(fnote):
                os.unlink(fnote)
                self.log("Deleted note from disk (key={0})".format(key))

        if not sync_errors:
            self.last_sync = sync_start_time

        # if there were any changes then update the current view
        if local_updates or local_deletes:
            self.update_view()

        if server_sync and full_sync:
            self.log("Full sync completed")

        return sync_errors

    def _get_note_status(self, key):
        """Get the note status"""
        note = self.notes[key]
        obj = utils.KeyValueObject(saved=False, synced=False, modified=False)
        modified = float(note['modified'])
        savedate = float(note['savedate'])

        if savedate > modified:
            obj.saved = True
        return obj

    def verify_all_saved(self):
        """
        Verify all notes in the local database are saved to the
        server
        """
        all_saved = True
        self.sync_lock.acquire()
        for k in list(self.notes.keys()):
            obj = self._get_note_status(k)
            if not obj.saved:
                all_saved = False
                break
        self.sync_lock.release()
        return all_saved

    def sync_now(self, do_server_sync=True):
        """Sync the notes to the server"""
        self.sync_lock.acquire()
        self._sync_notes(server_sync=do_server_sync,
                         full_sync=True if not self.last_sync else False)
        self.sync_lock.release()

    def sync_worker(self, do_server_sync):
        """The sync worker thread"""
        time.sleep(1) # give some time to wait for GUI initialization
        self.log('Sync worker: started')
        self.sync_now(do_server_sync)
        while True:
            self.go_cond.acquire()
            self.go_cond.wait(15)
            self.sync_now(do_server_sync)
            self.go_cond.release()

    def sync_worker_go(self):
        """Start the sync worker"""
        self.go_cond.acquire()
        self.go_cond.notify()
        self.go_cond.release()
