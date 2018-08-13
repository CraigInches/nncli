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
import logging
import os
import pytest
import shutil

from logging.handlers import RotatingFileHandler
from nnotes_cli.nncli import nncli

def mock_nncli(mocker):
    mocker.patch('logging.getLogger')
    mocker.patch('nnotes_cli.config.Config')
    mocker.patch('nnotes_cli.notes_db.NotesDB')
    mocker.patch('os.mkdir')
    mocker.patch.object(RotatingFileHandler, '_open')

def assert_initialized():
    logging.getLogger.assert_called_once()
    RotatingFileHandler._open.assert_called_once()
    assert os.mkdir.call_count == 2

@pytest.mark.parametrize('mock_nncli', [mock_nncli])
def test_init_no_tempdir(mocker, mock_nncli):
    mock_nncli(mocker)

    with open('test_cfg', 'w') as config_file:
        config_file.write('[nncli]\n')
        config_file.write('cfg_db_path=duh')

    nn = nncli(False, config_file='test_cfg')
    assert_initialized()
    assert nn.tempdir == None
    os.mkdir.assert_called_with('duh')

    os.remove('test_cfg')

@pytest.mark.parametrize('mock_nncli', [mock_nncli])
def test_init(mocker, mock_nncli):
    mock_nncli(mocker)

    with open('test_cfg', 'w') as config_file:
        config_file.write('[nncli]\n')
        config_file.write('cfg_tempdir=blah\n')
        config_file.write('cfg_db_path=duh')

    nn = nncli(False, config_file='test_cfg')
    assert_initialized()
    assert nn.tempdir == 'blah'

    os.remove('test_cfg')

@pytest.mark.parametrize('mock_nncli', [mock_nncli])
def test_init_notesdb_fail(mocker, mock_nncli):
    os.mkdir('duh')
    mock_nncli(mocker)

    with open('duh/1.json', 'w') as bad_file:
        bad_file.write('bad_json_data')

    with open('test_cfg', 'w') as config_file:
        config_file.write('[nncli]\n')
        config_file.write('cfg_db_path=duh')

    with pytest.raises(SystemExit):
        nn = nncli(False, config_file='test_cfg')

    shutil.rmtree('duh')

@pytest.mark.parametrize('mock_nncli', [mock_nncli])
def test_get_editor(mocker, mock_nncli):
    mock_nncli(mocker)

    with open('test_cfg', 'w') as config_file:
        config_file.write('[nncli]\n')
        config_file.write('cfg_db_path=duh')
        config_file.write('cfg_editor=vim')

    nn = nncli(False, config_file='test_cfg')
    assert_initialized()
    assert nn.get_editor() == 'vim'

    os.remove('test_cfg')

@pytest.mark.parametrize('mock_nncli', [mock_nncli])
def test_no_editor(mocker, mock_nncli):
    mock_nncli(mocker)

    with open('test_cfg', 'w') as config_file:
        config_file.write('[nncli]\n')
        config_file.write('cfg_db_path=duh')

    nn = nncli(False, config_file='test_cfg')
    nn.config.configs['editor'] = ['']
    assert_initialized()
    assert nn.get_editor() == None

    os.remove('test_cfg')

def test_get_pager():
    pass

def test_get_diff():
    pass

def test_exec_cmd_on_note():
    pass

def test_exec_diff_on_note():
    pass

def test_gui_header_clear():
    pass

def test_gui_header_set():
    pass

def test_gui_header_get():
    pass

def test_gui_header_focus():
    pass

def test_gui_footer_log_clear():
    pass

def test_gui_footer_log_set():
    pass

def test_gui_footer_log_get():
    pass

def test_gui_footer_input_clear():
    pass

def test_gui_footer_input_set():
    pass

def test_gui_footer_input_get():
    pass

def test_gui_footer_focus_input():
    pass

def test_gui_body_clear():
    pass

def test_gui_body_set():
    pass

def test_gui_body_get():
    pass

def test_gui_body_focus():
    pass

def test_log_timeout():
    pass

def test_log():
    pass

def test_gui_update_view():
    pass

def test_gui_update_status_bar():
    pass

def test_gui_switch_frame_body():
    pass

def test_delete_note_callback():
    pass

def test_gui_yes_no_input():
    pass

def test_gui_search_input():
    pass

def test_gui_category_input():
    pass

def test_gui_pipe_input():
    pass

def test_gui_frame_keypress():
    pass

def test_gui_init_view():
    pass

def test_gui_clear():
    pass

def test_gui_reset():
    pass

def test_gui_stop():
    pass

def test_gui():
    pass

def test_cli_list_notes():
    pass

def test_cli_note_dump():
    pass

def test_cli_dump_notes():
    pass

def test_cli_note_create():
    pass

def test_cli_note_import():
    pass

def test_cli_note_export():
    pass

def test_cli_export_notes():
    pass

def test_cli_note_edit():
    pass

def test_cli_note_delete():
    pass

def test_cli_note_favorite():
    pass

def test_cli_note_category_get():
    pass

def test_cli_note_category_set():
    pass

def test_cli_note_category_rm():
    pass

def test_SIGINT_handler():
    pass

def test_usage():
    pass

def test_version():
    pass

def test_main():
    pass

def test_nncli_start():
    pass
