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
sncli_to_nn.py

Simplenote to NextCloud Notes

This script imports a folder of json-formatted sncli notes and uploads
them to the specified NextCloud Notes account.

NOTE: Tags are ignored in the conversion.
"""
import json
import logging
import os
import requests
import sys

API_URL = 'https://{}:{}@{}/index.php/apps/notes/api/v0.2/notes'

def convert(sn):
    nn = {}
    nn['content'] = sn['content']
    nn['modified'] = int(sn['modifydate'].split('.')[0])
    nn['favorite'] = 'true' if 'pinned' in sn['systemtags'] else 'false'
    if len(sn['tags']) != 0:
        print("WARNING: Ignoring tags in note " + sn['key'] + '.json')
    return nn

def upload(nn, url):
    res = requests.post(url, data=nn)

def sncli_to_nn(sndb_path, nn_host, nn_user, nn_pw):
    sndb_path = os.path.expanduser(sndb_path)
    url = API_URL.format(nn_user, nn_pw, nn_host)
    if not os.path.isdir(sndb_path):
        usage("Provided sndb_path does not exist or is not a directory")

    for filename in os.listdir(sndb_path):
        if filename.endswith('.json'):
            with open(os.path.join(sndb_path, filename), 'r') as notefile:
                nn = convert(json.load(notefile))

            upload(nn, url)

def usage(message=None):
    if message is not None:
        print("ERROR: " + message)

    print("""
Usage:
 python3 sncli_to_nn.py sndb_path nn_host nn_user nn_pw

 sndb_path - sncli notes database path
 nn_host   - NextCloud host
 nn_user   - NextCloud account username
 nn_pw     - NextCloud account password
""")
    exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 5:
        usage("Wrong number of arguments")

    sncli_to_nn(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
