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

# first line with non-whitespace should be the title
note_title_re = re.compile('\s*(.*)\n?')

def generate_random_key():
    """Generate random 30 digit (15 byte) hex string.

    stackoverflow question 2782229
    """
    return '%030x' % (random.randrange(256**15),)

def get_note_tags(note):
    if 'tags' in note:
        tags = '%s' % ','.join(note['tags'])
        if 'deleted' in note and note['deleted']:
            if tags: tags += ',trash'
            else:    tags = 'trash'
    else:
        tags = ''
    return tags

# Returns a fixed length string:
#   'X' - needs sync
#   'T' - trashed
#   '*' - pinned
#   'S' - published/shared
#   'm' - markdown
def get_note_flags(note):
    flags = ''
    flags += 'X' if float(note['modifydate']) > float(note['syncdate']) else ' '
    flags += 'T' if 'deleted' in note and note['deleted'] else ' '
    if 'systemtags' in note:
        flags += '*' if 'pinned'    in note['systemtags'] else ' '
        flags += 'S' if 'published' in note['systemtags'] else ' '
        flags += 'm' if 'markdown'  in note['systemtags'] else ' '
    else:
        flags += '   '
    return flags

def get_note_title(note):
    mo = note_title_re.match(note.get('content', ''))
    if mo:
        return mo.groups()[0]
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

        if note_markdown(note):
            fn += '.mkdn'
        else:
            fn += '.txt'

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

def note_published(n):
    asystags = n.get('systemtags', 0)
    if not asystags:
        return 0
    return 1 if 'published' in asystags else 0

def note_pinned(n):
    asystags = n.get('systemtags', 0)
    if not asystags:
        return 0
    return 1 if 'pinned' in asystags else 0

def note_markdown(n):
    asystags = n.get('systemtags', 0)
    if not asystags:
        return 0
    return 1 if 'markdown' in asystags else 0

# TODO: NextCloud notes doesn't have a concept of tags, but it does
# allow assignment of notes to a single category. Refactor to take this
# into account
tags_illegal_chars = re.compile(r'[\s]')
def sanitise_tags(tags):
    """
    Given a string containing comma-separated tags, sanitise and return a list of string tags.

    The NextCloud API doesn't allow for spaces, so we strip those out.

    @param tags: Comma-separated tags, one string.
    @returns: List of strings.
    """
    # hack out all kinds of whitespace, then split on ,
    # if you run into more illegal characters (NextCloud does not want to sync them)
    # add them to the regular expression above.
    illegals_removed = tags_illegal_chars.sub('', tags)
    if len(illegals_removed) == 0:
        # special case for empty string ''
        # split turns that into [''], which is not valid
        return []

    else:
        return illegals_removed.split(',')

def sort_by_title_pinned(a):
    return (not note_pinned(a.note), get_note_title(a.note))

def sort_notes_by_tags(notes, pinned_ontop=False):
    notes.sort(key=lambda i: (pinned_ontop and not note_pinned(i.note),
                              i.note.get('tags'),
                              get_note_title(i.note)))

def sort_by_modify_date_pinned(a):
    if note_pinned(a.note):
        return 100.0 * float(a.note.get('modifydate', 0))
    else:
        return float(a.note.get('modifydate', 0))

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
