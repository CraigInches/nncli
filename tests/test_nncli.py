# -*- encoding: utf-8 -*-

import logging
import os
import pytest
import shutil

from logging.handlers import RotatingFileHandler
import nncli.nncli

@pytest.fixture
def mock_nncli(mocker):
    mocker.patch('logging.getLogger')
    mocker.patch('nncli.nncli.NotesDB')
    mocker.patch('os.mkdir')
    mocker.patch.object(RotatingFileHandler, '_open')
    mocker.patch('subprocess.check_output')

def mock_get_config(mocker, return_list):
    mocker.patch.object(
            nncli.nncli.Config,
            'get_config',
            new=mocker.MagicMock(side_effect=return_list)
            )

def assert_initialized():
    assert logging.getLogger.call_count == 2
    RotatingFileHandler._open.assert_called_once()
    os.mkdir.assert_called_once()

def test_init_no_tempdir(mocker, mock_nncli):
    mock_get_config(mocker, ['what', '', 'duh', 'duh', 'duh'])
    nn = nncli.nncli.nncli(False)
    assert_initialized()
    assert nn.tempdir == None
    os.mkdir.assert_called_with('duh')

def test_init(mocker, mock_nncli):
    mock_get_config(mocker, ['what', 'blah', 'duh', 'duh', 'duh'])
    nn = nncli.nncli.nncli(False)
    assert_initialized()
    assert nn.tempdir == 'blah'

def test_init_notesdb_fail(mocker, mock_nncli):
    mock_get_config(mocker, ['what', 'blah', 'duh', 'duh', 'duh'])
    mocker.patch('nncli.nncli.NotesDB',
            new=mocker.MagicMock(side_effect=SystemExit)
            )
    with pytest.raises(SystemExit):
        nn = nncli.nncli.nncli(False)

def test_get_editor(mocker, mock_nncli):
    mock_get_config(mocker, ['what', 'blah', 'duh', 'duh', 'duh', 'vim', ''])
    nn = nncli.nncli.nncli(False)
    assert_initialized()
    assert nn.get_editor() == 'vim'
    assert nn.get_editor() == None

def test_get_pager(mocker, mock_nncli):
    mock_get_config(mocker, ['what', 'blah', 'duh', 'duh', 'duh', 'less', ''])
    nn = nncli.nncli.nncli(False)
    assert_initialized()
    assert nn.get_editor() == 'less'
    assert nn.get_editor() == None

def test_get_diff(mocker, mock_nncli):
    mock_get_config(mocker, ['what', 'blah', 'duh', 'duh', 'duh', 'diff', ''])
    nn = nncli.nncli.nncli(False)
    assert_initialized()
    assert nn.get_editor() == 'diff'
    assert nn.get_editor() == None

@pytest.mark.skip
def test_exec_cmd_on_note(mocker, mock_nncli):
    mocker.patch.object(
            'nncli.nncli.nncli',
            get_editor,
            new=mocker.MagicMock(return_value='vim'))
    mocker.patch('nncli.temp.tempfile_create')

@pytest.mark.skip
def test_exec_diff_on_note():
    pass

@pytest.mark.skip
def test_gui_header_clear():
    pass

@pytest.mark.skip
def test_gui_header_set():
    pass

@pytest.mark.skip
def test_gui_header_get():
    pass

@pytest.mark.skip
def test_gui_header_focus():
    pass

@pytest.mark.skip
def test_gui_footer_log_clear():
    pass

@pytest.mark.skip
def test_gui_footer_log_set():
    pass

@pytest.mark.skip
def test_gui_footer_log_get():
    pass

@pytest.mark.skip
def test_gui_footer_input_clear():
    pass

@pytest.mark.skip
def test_gui_footer_input_set():
    pass

@pytest.mark.skip
def test_gui_footer_input_get():
    pass

@pytest.mark.skip
def test_gui_footer_focus_input():
    pass

@pytest.mark.skip
def test_gui_body_clear():
    pass

@pytest.mark.skip
def test_gui_body_set():
    pass

@pytest.mark.skip
def test_gui_body_get():
    pass

@pytest.mark.skip
def test_gui_body_focus():
    pass

@pytest.mark.skip
def test_log_timeout():
    pass

@pytest.mark.skip
def test_log():
    pass

@pytest.mark.skip
def test_gui_update_view():
    pass

@pytest.mark.skip
def test_gui_update_status_bar():
    pass

@pytest.mark.skip
def test_gui_switch_frame_body():
    pass

@pytest.mark.skip
def test_delete_note_callback():
    pass

@pytest.mark.skip
def test_gui_yes_no_input():
    pass

@pytest.mark.skip
def test_gui_search_input():
    pass

@pytest.mark.skip
def test_gui_category_input():
    pass

@pytest.mark.skip
def test_gui_pipe_input():
    pass

@pytest.mark.skip
def test_gui_frame_keypress():
    pass

@pytest.mark.skip
def test_gui_init_view():
    pass

@pytest.mark.skip
def test_gui_clear():
    pass

@pytest.mark.skip
def test_gui_reset():
    pass

@pytest.mark.skip
def test_gui_stop():
    pass

@pytest.mark.skip
def test_gui():
    pass

@pytest.mark.skip
def test_cli_list_notes():
    pass

@pytest.mark.skip
def test_cli_note_dump():
    pass

@pytest.mark.skip
def test_cli_dump_notes():
    pass

@pytest.mark.skip
def test_cli_note_create():
    pass

@pytest.mark.skip
def test_cli_note_import():
    pass

@pytest.mark.skip
def test_cli_note_export():
    pass

@pytest.mark.skip
def test_cli_export_notes():
    pass

@pytest.mark.skip
def test_cli_note_edit():
    pass

@pytest.mark.skip
def test_cli_note_delete():
    pass

@pytest.mark.skip
def test_cli_note_favorite():
    pass

@pytest.mark.skip
def test_cli_note_category_get():
    pass

@pytest.mark.skip
def test_cli_note_category_set():
    pass

@pytest.mark.skip
def test_cli_note_category_rm():
    pass

@pytest.mark.skip
def test_SIGINT_handler():
    pass

@pytest.mark.skip
def test_usage():
    pass

@pytest.mark.skip
def test_version():
    pass

@pytest.mark.skip
def test_main():
    pass

@pytest.mark.skip
def test_nncli_start():
    pass
