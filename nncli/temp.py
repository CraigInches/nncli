# -*- coding: utf-8 -*-
"""temp module"""
import json
import os
import tempfile

def tempfile_create(note, raw=False, tempdir=None):
    """create a temp file"""
    if raw:
        # dump the raw json of the note
        tfile = tempfile.NamedTemporaryFile(suffix='.json',
                                            delete=False, dir=tempdir)

        contents = json.dumps(note, indent=2)
        tfile.write(contents.encode('utf-8'))
        tfile.flush()
    else:
        ext = '.mkd'
        tfile = tempfile.NamedTemporaryFile(suffix=ext, delete=False,
                                            dir=tempdir)
        if note:
            contents = note['content']
            tfile.write(contents.encode('utf-8'))
        tfile.flush()
    return tfile

def tempfile_delete(tfile):
    """delete a temp file"""
    if tfile:
        tfile.close()
        os.unlink(tfile.name)

def tempfile_name(tfile):
    """get the name of a temp file"""
    if tfile:
        return tfile.name
    return ''

def tempfile_content(tfile):
    """read the contents of the temp file"""
    # This 'hack' is needed because some editors use an intermediate temporary
    # file, and rename it to that of the correct file, overwriting it. This
    # means that the tf file handle won't be updated with the new contents, and
    # the tempfile must be re-opened and read
    if not tfile:
        return None

    with open(tfile.name, 'rb') as temp:
        updated_tf_contents = temp.read()
        return updated_tf_contents.decode('utf-8')
