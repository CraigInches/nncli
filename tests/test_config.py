# -*- encoding: utf-8 -*-

import os
import sys

from nncli.config import Config
from pytest import raises

def test_init(mocker):
    mocker.patch('subprocess.check_output')
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
