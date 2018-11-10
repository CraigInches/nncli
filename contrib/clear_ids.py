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
"""
clear_ids.py

Remove ID's from all local notes. Use this script to force a full
re-upload to NextCloud.
"""
import json
import os
import sys

def clear_ids(sndb_path):
    sndb_path = os.path.expanduser(sndb_path)
    if not os.path.isdir(sndb_path):
        usage("Provided sndb_path does not exist or is not a directory")

    for filename in os.listdir(sndb_path):
        if filename.endswith('.json'):
            with open(os.path.join(sndb_path, filename), 'r') as notefile:
                note = json.load(notefile)
            del note['id']
            with open(os.path.join(sndb_path, filename), 'w') as notefile:
                json.dump(note, notefile)

def usage(message=None):
    if message is not None:
        print("ERROR: " + message)

    print("""
Usage:
 python3 clear_ids.py sndb_path

 sndb_path - sncli notes database path
""")
    exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage("Wrong number of arguments")

    clear_ids(sys.argv[1])
