# -*- coding: utf-8 -*-

import datetime
import random
import re
import shlex

import subprocess
from subprocess import CalledProcessError

from . import temp

def get_editor(config, logger):
    """Get the editor"""
    editor = config.get_config('editor')
    if not editor:
        logger.log('No editor configured!')
        return None
    return editor

def get_pager(config, logger):
    """Get the pager"""
    pager = config.get_config('pager')
    if not pager:
        logger.log('No pager configured!')
        return None
    return pager

def exec_cmd_on_note(note, config, gui, logger, cmd=None, raw=False):
    """Execute an external command to operate on the note"""

    if not cmd:
        cmd = get_editor(config, logger)
    if not cmd:
        return None

    tfile = temp.tempfile_create(
            note if note else None,
            raw=raw,
            tempdir=config.get_config('tempdir')
            )
    fname = temp.tempfile_name(tfile)

    if config.state.do_gui:
        focus_position = 0
        try:
            focus_position = gui.gui_body_get().focus_position
        except IndexError:
            pass

    subs = {'fname': fname, 'line': focus_position + 1}
    cmd_list = [c.format(**subs) for c in shlex.split(cmd)]

    # if the filename wasn't able to be subbed, append it
    # this makes it fully backwards compatible with previous configs
    if '{fname}' not in cmd:
        cmd_list.append(fname)

    logger.log("EXECUTING: {}".format(cmd_list))

    try:
        subprocess.check_call(cmd_list)
    except CalledProcessError as ex:
        logger.log('Command error: %s' % ex)
        temp.tempfile_delete(tfile)
        return None

    content = None
    if not raw:
        content = temp.tempfile_content(tfile)
        if not content or content == '\n':
            content = None

    temp.tempfile_delete(tfile)

    if config.state.do_gui:
        gui.nncli_loop.screen.clear()
        gui.nncli_loop.draw_screen()

    return content

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
