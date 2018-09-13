# -*- coding: utf-8 -*-

import os
import subprocess
import sys

from nncli.config import Config
from pytest import raises

def mock_config_file(mocker, file_contents):
    """mock the file and configparser 'enumerate' iterator"""
    mock_cfg = mocker.mock_open(
            read_data='\n'.join(file_contents)
            )
    mocker.patch('configparser.open', mock_cfg)
    mocker.patch('configparser.enumerate', new=mocker.Mock(
        return_value=enumerate(file_contents, start=1)
        ))
    return mock_cfg

def test_init(mocker):
    """test nominal initialization"""
    mock_cfg = mock_config_file(
            mocker,
            [
                    '[nncli]',
                    'cfg_nn_username=user',
                    'cfg_nn_password_eval=password_cmd',
                    'cfg_nn_host=nextcloud.example.org'
            ])
    mocker.patch('subprocess.check_output',
                 new=mocker.Mock(return_value='yes\n'))

    config = Config()

    mock_cfg.assert_called_once()
    subprocess.check_output.assert_called_once()
    assert config.get_config('nn_password') == 'yes'

def test_custom_file(mocker):
    """test with a supplied (custom) config file"""
    mock_cfg = mock_config_file(mocker,
            [
                    '[nncli]',
                    'cfg_nn_username=user',
                    'cfg_nn_password=password',
                    'cfg_nn_host=nextcloud.example.org'
            ])

    config = Config('test_cfg')
    mock_cfg.assert_called_once_with('test_cfg', encoding=None)
    assert config.get_config('nn_username') == 'user'
    assert config.get_config('nn_password') == 'password'

def test_bad_password_eval(mocker):
    """test failed call to password eval"""
    mock_cfg = mock_config_file(mocker,
            [
                    '[nncli]',
                    'cfg_nn_username=user',
                    'cfg_nn_password_eval=password',
                    'cfg_nn_host=nextcloud.example.org'
            ])

    with raises(SystemExit):
        config = Config('test_cfg')

def test_empty_config(mocker):
    mock_cfg = mock_config_file(mocker, [])

    config = Config('test_cfg')

def test_get_config(mocker):
    mock_cfg = mock_config_file(mocker, [])
    config = Config('test_cfg')
    assert config.get_config('sort_mode') == 'date'

def test_get_config_descr(mocker):
    mock_cfg = mock_config_file(mocker, [])
    config = Config('test_cfg')
    assert config.get_config_descr('sort_mode') == 'Sort mode'

def test_get_keybind(mocker):
    mock_cfg = mock_config_file(mocker, [])
    config = Config('test_cfg')
    assert config.get_keybind('help') == 'h'

def test_get_keybind_use(mocker):
    mock_cfg = mock_config_file(mocker, [])
    config = Config('test_cfg')
    assert config.get_keybind_use('help') == [ 'common' ]

def test_get_keybind_descr(mocker):
    mock_cfg = mock_config_file(mocker, [])
    config = Config('test_cfg')
    assert config.get_keybind_descr('help') == 'Help'

def test_get_color(mocker):
    mock_cfg = mock_config_file(mocker, [])
    config = Config('test_cfg')
    assert config.get_color('default_fg') == 'default'

def test_get_color_descr(mocker):
    mock_cfg = mock_config_file(mocker, [])
    config = Config('test_cfg')
    assert config.get_color_descr('default_fg') == 'Default fg'
