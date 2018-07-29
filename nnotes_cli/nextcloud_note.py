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
# This file is *slightly* modified from simplynote.py.

# -*- coding: utf-8 -*-
"""
    nextcloud_note.py
    ~~~~~~~~~~~~~~

    Python library for accessing the NextCloud Notes API (v0.2)

    Modified from simplnote.py
    :copyright: (c) 2011 by Daniel Schauenberg
    :license: MIT, see LICENSE for more details.
"""

import urllib.parse
from requests.exceptions import RequestException, ConnectionError
import base64
import time
import datetime
import logging
import requests
import traceback

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        # For Google AppEngine
        from django.utils import simplejson as json

NOTE_FETCH_LENGTH = 100

class NextcloudLoginFailed(Exception):
    pass

class NextcloudNote(object):
    """ Class for interacting with the NextCloud Notes web service """

    def __init__(self, username, password, host):
        """ object constructor """
        self.username = urllib.parse.quote(username)
        self.password = urllib.parse.quote(password)
        self.api_url = \
            'https://{}:{}@{}/index.php/apps/notes/api/v0.2/notes'. \
                format(username, password, host)
        self.sanitized_url = \
            'https://{}:****@{}/index.php/apps/notes/api/v0.2/notes'. \
                format(username, host)
        self.status = 'offline'

    def get_note(self, noteid):
        """ method to get a specific note

        Arguments:
            - noteid (string): ID of the note to get

        Returns:
            A tuple `(note, status)`

            - note (dict): note object
            - status (int): 0 on sucesss and -1 otherwise

        """
        # request note
        url = '{}/{}'.format(self.api_url, str(noteid))
        #logging.debug('REQUEST: ' + self.sanitized_url+params)
        try:
            res = requests.get(url)
            res.raise_for_status()
            note = res.json()
            self.status = 'online'
        except ConnectionError as e:
            self.status = 'offline, connection error'
            return e, -1
        except RequestException as e:
            # logging.debug('RESPONSE ERROR: ' + str(e))
            return e, -1
        except ValueError as e:
            return e, -1

        # # use UTF-8 encoding
        # note["content"] = note["content"].encode('utf-8')
        # # For early versions of notes, category is not always available
        # if "category" in note:
        #     note["category"] = [t.encode('utf-8') for t in note["category"]]
        #logging.debug('RESPONSE OK: ' + str(note))
        return note, 0

    def update_note(self, note):
        """ function to update a specific note object, if the note
        object does not have a "key" field, a new note is created

        Arguments
            - note (dict): note object to update

        Returns:
            A tuple `(note, status)`

            - note (dict): note object
            - status (int): 0 on sucesss and -1 otherwise

        """
        # Note: all strings in notes stored as type str
        # - use s.encode('utf-8') when bytes type needed

        # determine whether to create a new note or updated an existing one
        if "id" in note:
            # set modification timestamp if not set by client
            if 'modified' not in note:
                note["modified"] = int(time.time())

            url = '{}/{}'.format(self.api_url, note["id"])
            del note["id"]
        else:
            url = self.api_url

        #logging.debug('REQUEST: ' + url + ' - ' + str(note))
        try:
            logging.debug('NOTE: ' + str(note))
            if url != self.api_url:
                res = requests.put(url, data=note)
            else:
                res = requests.post(url, data=note)
            note = res.json()
            res.raise_for_status()
            logging.debug('NOTE (from response): ' + str(res.json()))
            self.status = 'online'
        except ConnectionError as e:
            self.status = 'offline, connection error'
            return e, -1
        except RequestException as e:
            logging.debug('RESPONSE ERROR: ' + str(e))
            logging.debug(traceback.print_exc())
            self.status = 'error updating note, check log'
            return e, -1
        except ValueError as e:
            return e, -1
        #logging.debug('RESPONSE OK: ' + str(note))
        return note, 0

    def add_note(self, note):
        """wrapper function to add a note

        The function can be passed the note as a dict with the `content`
        property set, which is then directly send to the web service for
        creation. Alternatively, only the body as string can also be passed. In
        this case the parameter is used as `content` for the new note.

        Arguments:
            - note (dict or string): the note to add

        Returns:
            A tuple `(note, status)`

            - note (dict): the newly created note
            - status (int): 0 on sucesss and -1 otherwise

        """
        if type(note) == str:
            return self.update_note({"content": note})
        elif (type(note) == dict) and "content" in note:
            return self.update_note(note)
        else:
            return "No string or valid note.", -1

    def get_note_list(self, category=None):
        """ function to get the note list

        The function can be passed optional arguments to limit the
        date range of the list returned and/or limit the list to notes
        containing a certain category. If omitted a list of all notes
        is returned.

        Arguments:
            - category=None category as string: return notes tagged to
              this category

        Returns:
            A tuple `(notes, status)`

            - notes (list): A list of note objects with all properties
              set except `content`.
            - status (int): 0 on sucesss and -1 otherwise

        """
        # initialize data
        status = 0
        note_list = {}

        # get the note index
        params = {'exclude': 'content'}

        # perform initial HTTP request
        try:
            logging.debug('REQUEST: ' + self.sanitized_url + \
                '?exclude=content')
            res = requests.get(self.api_url, params=params)
            res.raise_for_status()
            #logging.debug('RESPONSE OK: ' + str(res))
            note_list = res.json()
            self.status = 'online'
        except ConnectionError as e:
            self.status = 'offline, connection error'
            status = -1
        except RequestException as e:
            # if problem with network request/response
            status = -1
        except ValueError as e:
            # if invalid json data
            status = -1

        # Can only filter for category at end, once all notes have been
        # retrieved. Below based on simplenote.vim, except we return
        # deleted notes as well
        if category is not None:
            note_list = \
                [n for n in note_list if n["category"] == category]

        return note_list, status

    def delete_note(self, note):
        """ method to permanently delete a note

        Arguments:
            - note_id (string): key of the note to delete

        Returns:
            A tuple `(note, status)`

            - note (dict): an empty dict or an error message
            - status (int): 0 on sucesss and -1 otherwise

        """
        url = '{}/{}'.format(self.api_url, str(note['id']))
        logurl = '{}/{}'.format(self.sanitized_url, str(note['id']))

        try:
            logging.debug('REQUEST DELETE: ' + logurl)
            res = requests.delete(url)
            res.raise_for_status()
            self.status = 'online'
        except ConnectionError as e:
            self.status = 'offline, connection error'
            return e, -1
        except RequestException as e:
            return e, -1
        return {}, 0
