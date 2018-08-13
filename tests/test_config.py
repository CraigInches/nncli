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
import os
import sys

from nnotes_cli.config import Config
from pytest import raises

def test_init():
    config = Config()

    if sys.platform == 'linux':
        assert config.config_home == os.path.join(os.path.expanduser('~'), \
                '.config', 'nncli')
        assert config.cache_home == os.path.join(os.path.expanduser('~'), \
                '.cache', 'nncli')
    if sys.platform == 'darwin':
        assert config.config_home == os.path.join(os.path.expanduser('~'), \
                'Library', 'Preferences', 'nncli')
        assert config.cache_home == os.path.join(os.path.expanduser('~'), \
                'Library', 'Caches', 'nncli')


def test_custom_file():
    with open('test_cfg', 'w') as config_file:
        config_file.write('[nncli]\n')
        config_file.write('cfg_nn_username=user\n')
        config_file.write('cfg_nn_password=password\n')
        config_file.write('cfg_nn_host=nextcloud.example.org\n')

    config = Config('test_cfg')
    os.remove('test_cfg')

def test_bad_password_eval():
    with open('test_cfg', 'w') as config_file:
        config_file.write('[nncli]\n')
        config_file.write('cfg_nn_username=user\n')
        config_file.write('cfg_nn_password_eval=password\n')
        config_file.write('cfg_nn_host=nextcloud.example.org\n')

    with raises(SystemExit):
        config = Config('test_cfg')
    os.remove('test_cfg')

def test_empty_config():
    with open('test_cfg', 'w') as config_file:
        config_file.write('\n')

    config = Config('test_cfg')
    os.remove('test_cfg')

def test_get_config():
    config = Config('test_cfg')
    assert config.get_config('sort_mode') == 'date'

def test_get_config_descr():
    config = Config('test_cfg')
    assert config.get_config_descr('sort_mode') == 'Sort mode'

def test_get_keybind():
    config = Config('test_cfg')
    assert config.get_keybind('help') == 'h'

def test_get_keybind_use():
    config = Config('test_cfg')
    assert config.get_keybind_use('help') == [ 'common' ]

def test_get_keybind_descr():
    config = Config('test_cfg')
    assert config.get_keybind_descr('help') == 'Help'

def test_get_color():
    config = Config('test_cfg')
    assert config.get_color('default_fg') == 'default'

def test_get_color_descr():
    config = Config('test_cfg')
    assert config.get_color_descr('default_fg') == 'Default fg'
