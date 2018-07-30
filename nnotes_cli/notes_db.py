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
# This file is *heavily* modified from nvpy.

# nvPY: cross-platform note-taking app with simplenote syncing
# copyright 2012 by Charl P. Botha <cpbotha@vxlabs.com>
# new BSD license

import os, time, re, glob, json, copy, threading
from . import utils
from . import nextcloud_note
nextcloud_note.NOTE_FETCH_LENGTH=100
from .nextcloud_note import NextcloudNote
import logging

class ReadError(RuntimeError):
    pass

class WriteError(RuntimeError):
    pass

class NotesDB():
    """NotesDB will take care of the local notes database and syncing with SN.
    """
    def __init__(self, config, log, update_view):
        self.config      = config
        self.log         = log
        self.update_view = update_view

        self.last_sync = 0 # set to zero to trigger a full sync
        self.sync_lock = threading.Lock()
        self.go_cond   = threading.Condition()

        # create db dir if it does not exist
        if not os.path.exists(self.config.get_config('db_path')):
            os.mkdir(self.config.get_config('db_path'))

        now = int(time.time())
        # now read all .json files from disk
        fnlist = glob.glob(self.helper_key_to_fname('*'))

        self.notes = {}

        for fn in fnlist:
            try:
                n = json.load(open(fn, 'r'))
            except IOError as e:
                raise ReadError ('Error opening {0}: {1}'.format(fn, str(e)))
            except ValueError as e:
                raise ReadError ('Error reading {0}: {1}'.format(fn, str(e)))
            else:
                # we always have a localkey, also when we don't have a
                # note['id'] yet (no sync)
                localkey = n.get('localkey', os.path.splitext(os.path.basename(fn))[0])
                # we maintain in memory a timestamp of the last save
                # these notes have just been read, so at this moment
                # they're in sync with the disc.
                n['savedate'] = now
                # set a localkey to each note in memory
                # Note: 'id' is used only for syncing with server - 'localkey'
                #       is used for everything else in nncli
                n['localkey'] = localkey

                # add the note to our database
                self.notes[localkey] = n

        # initialise the NextCloud instance we're going to use
        # this does not yet need network access
        self.note = NextcloudNote(self.config.get_config('nn_username'),
                                  self.config.get_config('nn_password'),
                                  self.config.get_config('nn_host'))

        # we'll use this to store which notes are currently being synced by
        # the background thread, so we don't add them anew if they're still
        # in progress. This variable is only used by the background thread.
        self.threaded_syncing_keys = {}

    def filtered_notes_sort(self, filtered_notes, sort_mode='date'):
        if sort_mode == 'date':
            if self.config.get_config('favorite_ontop') == 'yes':
                filtered_notes.sort(key=utils.sort_by_modify_date_favorite, reverse=True)
            else:
                filtered_notes.sort(key=lambda o: -float(o.note.get('modified', 0)))
        elif sort_mode == 'alpha':
            if self.config.get_config('favorite_ontop') == 'yes':
                filtered_notes.sort(key=utils.sort_by_title_favorite)
            else:
                filtered_notes.sort(key=lambda o: utils.get_note_title(o.note))
        elif sort_mode == 'categories':
            favorite = self.config.get_config('favorite_ontop')
            utils.sort_notes_by_categories(filtered_notes, \
                    favorite_ontop=favorite)

    def filter_notes(self, search_string=None, search_mode='gstyle', sort_mode='date'):
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
                self.filter_notes_gstyle(search_string)
        else:
            filtered_notes, match_regexp, active_notes = \
                self.filter_notes_regex(search_string)

        self.filtered_notes_sort(filtered_notes, sort_mode)

        return filtered_notes, match_regexp, active_notes

    def _helper_gstyle_categorymatch(self, cat_pats, note):
        # Returns:
        #  2 = match    - no category patterns specified
        #  1 = match    - all category patterns match a category on this
        #                 note
        #  0 = no match - note has no category or not all category patterns match

        if not cat_pats:
            # match because no category patterns were specified
            return 2

        note_category = note.get('category')

        if not note_category:
            # category patterns specified but note has no categories, so no match
            return 0

        # for each cat_pat, we have to find a matching category
        # .lower() used for case-insensitive search
        cat_pats_matched = 0
        for tp in cat_pats:
            tp = tp.lower()
            for t in note_category:
                if tp in t.lower():
                    cat_pats_matched += 1
                    break

        if cat_pats_matched == len(cat_pats):
            # all category patterns specified matched a category on this note
            return 1

        # note doesn't match
        return 0

    def _helper_gstyle_wordmatch(self, word_pats, content):
        if not word_pats:
            return True

        word_pats_matched = 0
        lowercase_content = content.lower() # case insensitive search
        for wp in word_pats:
            wp = wp.lower() # case insensitive search
            if wp in lowercase_content:
                word_pats_matched += 1

        if word_pats_matched == len(word_pats):
            return True;

        return False

    def filter_notes_gstyle(self, search_string=None):

        filtered_notes = []
        active_notes = 0

        if not search_string:
            for k in self.notes:
                n = self.notes[k]
                active_notes += 1
                filtered_notes.append(utils.KeyValueObject(key=k, note=n, catfound=0))

            return filtered_notes, [], active_notes

        # group0: category:([^\s]+)
        # group1: multiple words in quotes
        # group2: single words

        # example result for: 'category:category1 category:category2 word1 "word2 word3" category:category3'
        # [ ('category1', '',            ''),
        #   ('category2', '',            ''),
        #   ('',     '',            'word1'),
        #   ('',     'word2 word3', ''),
        #   ('category3', '',            '') ]

        groups = re.findall('category:([^\s]+)|"([^"]+)"|([^\s]+)', search_string)
        all_pats = [[] for _ in range(3)]

        # we end up with [[cat_pats],[multi_word_pats],[single_word_pats]]
        for g in groups:
            for i in range(3):
                if g[i]: all_pats[i].append(g[i])

        for k in self.notes:
            n = self.notes[k]

            active_notes += 1

            catmatch = self._helper_gstyle_categorymatch(all_pats[0], n)

            word_pats = all_pats[1] + all_pats[2]

            if catmatch and \
               self._helper_gstyle_wordmatch(word_pats, n.get('content')):
                # we have a note that can go through!
                filtered_notes.append(
                    utils.KeyValueObject(key=k,
                                         note=n,
                                         catfound=1 if catmatch == 1 else 0))

        return filtered_notes, '|'.join(all_pats[1] + all_pats[2]), active_notes

    def filter_notes_regex(self, search_string=None):
        """
        Return a list of notes filtered using the regex search_string.
        Each element in the list is a tuple (local_key, note).
        """
        sspat = utils.build_regex_search(search_string)

        filtered_notes = []
        active_notes = 0 # total number of notes, including deleted ones

        for k in self.notes:
            n = self.notes[k]

            active_notes += 1

            if not sspat:
                filtered_notes.append(utils.KeyValueObject(key=k, note=n, catfound=0))
                continue

            if self.config.get_config('search_categories') == 'yes':
                cat_matched = False
                for t in n.get('category'):
                    if sspat.search(t):
                        cat_matched = True
                        filtered_notes.append(utils.KeyValueObject(key=k, note=n, catfound=1))
                        break
                if cat_matched:
                    continue

            if sspat.search(n.get('content')):
                filtered_notes.append(utils.KeyValueObject(key=k, note=n, catfound=0))

        match_regexp = search_string if sspat else ''
        return filtered_notes, match_regexp, active_notes

    def import_note(self, note):
        # need to get a key unique to this database. not really important
        # what it is, as long as it's unique.
        new_key = note['id'] if note.get('id') else utils.generate_random_key()
        while new_key in self.notes:
            new_key = utils.generate_random_key()

        timestamp = int(time.time())

        try:
            modified = float(note.get('modified', timestamp))
        except ValueError:
            raise ValueError('date fields must be numbers or string representations of numbers')

        # note has no internal key yet.
        new_note = {
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

        for n in (new_note['modified']):
            if not 0 <= n <= timestamp:
                raise ValueError('date fields must be real')

        if not isinstance(new_note['category'], str) or \
                new_note['category'] is None:
            raise ValueError('"category" must be an string')

        if not isinstance(new_note['favorite'], bool):
            raise ValueError('"favorite" must be a boolean')

        self.notes[new_key] = new_note

        return new_key

    def create_note(self, content):
        # need to get a key unique to this database. not really important
        # what it is, as long as it's unique.
        new_key = utils.generate_random_key()
        while new_key in self.notes:
            new_key = utils.generate_random_key()

        timestamp = int(time.time())
        title = content.split('\n')[0]

        # note has no internal key yet.
        new_note = {
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
        return self.notes[key]

    def get_note_favorite(self, key):
        return self.notes[key].get('favorite')

    def get_note_category(self, key):
        return self.notes[key].get('category')

    def get_note_content(self, key):
        return self.notes[key].get('content')

    def flag_what_changed(self, note, what_changed):
        if 'what_changed' not in note:
            note['what_changed'] = []
        if what_changed not in note['what_changed']:
            note['what_changed'].append(what_changed)

    def set_note_deleted(self, key, deleted):
        n = self.notes[key]
        old_deleted = n['deleted'] if 'deleted' in n else 0
        if old_deleted != deleted:
            n['deleted'] = deleted
            n['modified'] = int(time.time())
            self.flag_what_changed(n, 'deleted')
            self.log('Note marked for deletion (key={0})'.format(key))

    def set_note_content(self, key, content):
        n = self.notes[key]
        old_content = n.get('content')
        if content != old_content:
            n['content'] = content
            n['modified'] = int(time.time())
            self.flag_what_changed(n, 'content')
            self.log('Note content updated (key={0})'.format(key))

    def set_note_category(self, key, category):
        n = self.notes[key]
        old_category = n.get('category')
        if category != old_category:
            n['category'] = category
            n['modified'] = int(time.time())
            self.flag_what_changed(n, 'category')
            self.log('Note category updated (key={0})'.format(key))

    def set_note_favorite(self, key, favorite):
        n = self.notes[key]
        old_favorite = utils.note_favorite(n)
        if favorite != old_favorite:
            n['favorite'] = favorite
            n['modified'] = int(time.time())
            self.flag_what_changed(n, 'favorite')
            self.log('Note {0} (key={1})'. \
                    format('favorite' if favorite else \
                    'unfavorited', key))

    def helper_key_to_fname(self, k):
        return os.path.join(self.config.get_config('db_path'), str(k)) + '.json'

    def helper_save_note(self, k, note):
        # Save a single note to disc.
        fn = self.helper_key_to_fname(k)
        json.dump(note, open(fn, 'w'), indent=2)

        # record that we saved this to disc.
        note['savedate'] = int(time.time())

    def sync_notes(self, server_sync=True, full_sync=True):
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
        for note_index, local_key in enumerate(self.notes.keys()):
            n = self.notes[local_key]

            if not n.get('id') or \
               float(n.get('modified')) > float(n.get('syncdate')):

                savedate = float(n.get('savedate'))
                if float(n.get('modified')) > savedate or \
                   float(n.get('syncdate')) > savedate:
                    # this will trigger a save to disk after sync algorithm
                    # we want this note saved even if offline or sync fails
                    local_updates[local_key] = True

                if not server_sync:
                    # the 'what_changed' field will be written to disk and
                    # picked up whenever the next full server sync occurs
                    continue

                # only send required fields
                cn = copy.deepcopy(n)
                if 'what_changed' in n:
                    del n['what_changed']

                if 'localkey' in cn:
                    del cn['localkey']

                if 'minversion' in cn:
                    del cn['minversion']
                del cn['syncdate']
                del cn['savedate']
                del cn['deleted']
                if 'etag' in cn:
                    del cn['etag']
                if 'title' in cn:
                    del cn['title']

                if 'what_changed' in cn:
                    if 'content' not in cn['what_changed'] \
                            and 'category' not in cn['what_changed']:
                        del cn['content']
                    if 'category' not in cn['what_changed']:
                        del cn['category']
                    if 'favorite' not in cn['what_changed']:
                        del cn['favorite']
                    del cn['what_changed']

                if 'favorite' in cn:
                    cn['favorite'] = str.lower(str(cn['favorite']))

                if n['deleted']:
                    uret = self.note.delete_note(cn)
                else:
                    uret = self.note.update_note(cn)

                if uret[1] == 0: # success
                    # if this is a new note our local key is not valid anymore
                    # merge the note we got back (content could be empty)
                    # record syncdate and save the note at the assigned key
                    del self.notes[local_key]
                    k = uret[0].get('id')
                    t = uret[0].get('title')
                    c = uret[0].get('category')
                    c = c if c is not None else ''
                    n.update(uret[0])
                    n['syncdate'] = now
                    n['localkey'] = k
                    n['category'] = c
                    self.notes[k] = n

                    local_updates[k] = True
                    if local_key != k:
                        # if local_key was a different key it should be deleted
                        local_deletes[local_key] = True
                        if local_key in local_updates:
                            del local_updates[local_key]

                    self.log('Synced note to server (key={0})'.format(local_key))
                else:
                    self.log('ERROR: Failed to sync note to server (key={0})'.format(local_key))
                    sync_errors += 1

        # 2. get the note index
        if not server_sync:
            nl = []
        else:
            nl = self.note.get_note_list()

            if nl[1] == 0:  # success
                nl = nl[0]
            else:
                self.log('ERROR: Failed to get note list from server')
                sync_errors += 1
                nl = []
                skip_remote_syncing = True

        # 3. for each remote note
        #        if remote modified > local modified ||
        #           a new note and key is not in local store
        #            retrieve note, update note with response
        if not skip_remote_syncing:
            len_nl = len(nl)
            for note_index, n in enumerate(nl):
                k = n.get('id')
                c = n.get('category') if n.get('category') is not None \
                        else ''
                server_keys[k] = True
                # this works because in the prior step we rewrite local keys to
                # server keys when we get an updated note back from the server
                if k in self.notes:
                    # we already have this note
                    # if the server note has a newer syncnum we need to get it
                    if int(n.get('modified')) > int(self.notes[k].get('modified')):
                        gret = self.note.get_note(k)
                        if gret[1] == 0:
                            self.notes[k].update(gret[0])
                            local_updates[k] = True
                            self.notes[k]['syncdate'] = now
                            self.notes[k]['localkey'] = k
                            self.notes[k]['category'] = c
                            self.notes[k]['deleted'] = False

                            self.log('Synced newer note from server (key={0})'.format(k))
                        else:
                            self.log('ERROR: Failed to sync newer note from server (key={0})'.format(k))
                            sync_errors += 1
                else:
                    # this is a new note
                    gret = self.note.get_note(k)
                    if gret[1] == 0:
                        self.notes[k] = gret[0]
                        local_updates[k] = True
                        self.notes[k]['syncdate'] = now
                        self.notes[k]['localkey'] = k
                        self.notes[k]['category'] = c
                        self.notes[k]['deleted'] = False

                        self.log('Synced new note from server (key={0})'.format(k))
                    else:
                        self.log('ERROR: Failed syncing new note from server (key={0})'.format(k))
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
                self.helper_save_note(k, self.notes[k])
            except WriteError as e:
                raise WriteError (str(e))
            self.log("Saved note to disk (key={0})".format(k))

        for k in list(local_deletes.keys()):
            fn = self.helper_key_to_fname(k)
            if os.path.exists(fn):
                os.unlink(fn)
                self.log("Deleted note from disk (key={0})".format(k))

        if not sync_errors:
            self.last_sync = sync_start_time

        # if there were any changes then update the current view
        if len(local_updates) > 0 or len(local_deletes) > 0:
            self.update_view()

        if server_sync and full_sync:
            self.log("Full sync completed")

        return sync_errors

    def get_note_status(self, key):
        n = self.notes[key]
        o = utils.KeyValueObject(saved=False, synced=False, modified=False)
        modified = float(n['modified'])
        savedate   = float(n['savedate'])
        syncdate   = float(n['syncdate'])

        if savedate > modified:
            o.saved = True
        else:
            o.modified = True

        if syncdate > modified:
            o.synced = True

        return o

    def verify_all_saved(self):
        all_saved = True
        self.sync_lock.acquire()
        for k in list(self.notes.keys()):
            o = self.get_note_status(k)
            if not o.saved:
                all_saved = False
                break
        self.sync_lock.release()
        return all_saved

    def sync_now(self, do_server_sync=True):
        self.sync_lock.acquire()
        self.sync_notes(server_sync=do_server_sync,
                        full_sync=True if not self.last_sync else False)
        self.sync_lock.release()

    # sync worker thread...
    def sync_worker(self, do_server_sync):
        time.sleep(1) # give some time to wait for GUI initialization
        self.log('Sync worker: started')
        self.sync_now(do_server_sync)
        while True:
            self.go_cond.acquire()
            self.go_cond.wait(15)
            self.sync_now(do_server_sync)
            self.go_cond.release()

    def sync_worker_go(self):
        self.go_cond.acquire()
        self.go_cond.notify()
        self.go_cond.release()

