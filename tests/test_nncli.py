# -*- coding: utf-8 -*-
"""tests for nncli module"""
import logging
import os
import pytest
import shutil

import nncli.nncli
from nncli.notes_db import ReadError

@pytest.fixture
def mock_nncli(mocker):
    """mock the major interfaces for the Nncli class"""
    mocker.patch('nncli.nncli.NotesDB')
    mocker.patch('nncli.nncli.NncliGui')
    mocker.patch('nncli.nncli.Config')
    mocker.patch('nncli.nncli.Logger')
    mocker.patch('os.mkdir')
    mocker.patch('subprocess.check_output')
    mocker.patch('os.path.exists',
                 new=mocker.MagicMock(return_value=True))

def test_init_no_local_db(mocker, mock_nncli):
    """test initialization when there is no local notes database"""
    mocker.patch('os.path.exists',
                 new=mocker.MagicMock(return_value=False))
    mocker.patch.object(nncli.nncli.NotesDB, 'sync_now')
    nn_obj = nncli.nncli.Nncli(False)
    assert nn_obj.config.get_config.call_count == 2
    nn_obj.ndb.set_update_view.assert_called_once()
    os.mkdir.assert_called_once()
    nn_obj.ndb.sync_now.assert_called_once()

def test_init(mocker, mock_nncli):
    """test nominal initialization"""
    nn_obj = nncli.nncli.Nncli(False)
    nn_obj.config.get_config.assert_called_once()
    nn_obj.ndb.set_update_view.assert_called_once()
    assert os.mkdir.call_count == 0

def test_init_notesdb_fail(mocker, mock_nncli):
    """test init when there is a notes database failure"""
    mocker.patch('os.path.exists',
                 new=mocker.MagicMock(return_value=True))
    mocker.patch('nncli.nncli.NotesDB',
                 new=mocker.MagicMock(side_effect=ReadError)
                )
    with pytest.raises(SystemExit):
        nn = nncli.nncli.Nncli(False)

def test_gui(mocker, mock_nncli):
    """test starting the gui"""
    nn_obj = nncli.nncli.Nncli(False)
    nn_obj.gui(0)
    assert nn_obj.config.state.do_gui == True
    assert nn_obj.ndb.log == nn_obj.nncli_gui.log
    nn_obj.nncli_gui.run.assert_called_once()

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
