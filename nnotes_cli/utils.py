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

import datetime, random, re

def generate_random_key():
    """Generate random 30 digit (15 byte) hex string.

    stackoverflow question 2782229
    """
    return '%030x' % (random.randrange(256**15),)

def get_note_category(note):
    if 'category' in note:
        category = note['category'] if note['category'] is not None else ''
    else:
        category = ''
    return category

# Returns a fixed length string:
#   'X' - needs sync
#   '*' - favorite
def get_note_flags(note):
    flags = ''
    flags += 'X' if float(note['modified']) > float(note['syncdate']) else ' '
    if 'favorite' in note:
        flags += '*' if note['favorite'] else ' '
    else:
        flags += '  '
    return flags

def get_note_title(note):
    if 'title' in note:
        return note['title']
    else:
        return ''

def get_note_title_file(note):
    mo = note_title_re.match(note.get('content', ''))
    if mo:
        fn = mo.groups()[0]
        fn = fn.replace(' ', '_')
        fn = fn.replace('/', '_')
        if not fn:
            return ''

        if isinstance(fn, str):
            fn = str(fn, 'utf-8')
        else:
            fn = str(fn)

        fn += '.mkdn'
        return fn
    else:
        return ''

def human_date(timestamp):
    """
    Given a timestamp, return pretty human format representation.

    For example, if timestamp is:
    * today, then do "15:11"
    * else if it is this year, then do "Aug 4"
    * else do "Dec 11, 2011"
    """

    # this will also give us timestamp in the local timezone
    dt = datetime.datetime.fromtimestamp(timestamp)
    # this returns localtime
    now = datetime.datetime.now()

    if dt.date() == now.date():
        # today: 15:11
        return dt.strftime('%H:%M')

    elif dt.year == now.year:
        # this year: Aug 6
        # format code %d unfortunately 0-pads
        return dt.strftime('%b') + ' ' + str(dt.day)

    else:
        # not today or this year, so we do "Dec 11, 2011"
        return '%s %d, %d' % (dt.strftime('%b'), dt.day, dt.year)

def note_favorite(n):
    if 'favorite' in n:
        return n['favorite']
    else:
        return False

def sort_by_title_favorite(a):
    return (not note_favorite(a.note), get_note_title(a.note))

def sort_notes_by_categories(notes, favorite_ontop=False):
    notes.sort(key=lambda i: (favorite_ontop and not note_favorite(i.note),
                              i.note.get('category'),
                              get_note_title(i.note)))

def sort_by_modify_date_favorite(a):
    if note_favorite(a.note):
        return 100.0 * float(a.note.get('modified', 0))
    else:
        return float(a.note.get('modified', 0))

class KeyValueObject:
    """Store key=value pairs in this object and retrieve with o.key.

    You should also be able to do MiscObject(**your_dict) for the same effect.
    """

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def build_regex_search(search_string):
    """
    Build up a compiled regular expression from the search string.

    Supports the use of flags - ie. search for `nothing/i` will perform a
    case-insensitive regex for `nothing`
    """

    sspat = None
    valid_flags = {
            'i': re.IGNORECASE
    }
    if search_string:
        try:
            search_string, flag_letters = re.match(r'^(.+?)(?:/([a-z]+))?$', search_string).groups()
            flags = 0
            # if flags are given, OR together all the valid flags
            # see https://docs.python.org/3/library/re.html#re.compile
            if flag_letters:
                for letter in flag_letters:
                    if letter in valid_flags:
                        flags = flags | valid_flags[letter]
            sspat = re.compile(search_string, flags)
        except re.error:
            sspat = None

    return sspat
