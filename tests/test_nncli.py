# -*- coding: utf-8 -*-
"""tests for nncli module"""
from io import StringIO
import logging
import os
import pytest
import shutil

import nncli.nncli
from nncli.notes_db import ReadError
import nncli.utils

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
    os.path.exists.assert_called_once()

def test_gui(mocker, mock_nncli):
    """test starting the gui"""
    nn_obj = nncli.nncli.Nncli(False)
    nn_obj.gui(0)
    assert nn_obj.config.state.do_gui == True
    assert nn_obj.ndb.log == nn_obj.nncli_gui.log
    nn_obj.nncli_gui.run.assert_called_once()

def test_cli_list_notes(mocker, mock_nncli):
    """test listing notes from the command line"""
    test_note = (
            [nncli.utils.KeyValueObject(key='test_key',
             note='test_note')],
            [],
            []
            )
    mocker.patch('nncli.utils.get_note_flags',
                 new=mocker.Mock(return_value='flg'))
    mocker.patch('nncli.utils.get_note_title',
                 new=mocker.Mock(return_value='test_title'))
    mocker.patch('nncli.nncli.print')
    nn_obj = nncli.nncli.Nncli(False)
    mocker.patch.object(nn_obj.ndb, 'filter_notes',
                        new=mocker.Mock(return_value=test_note))
    nn_obj.cli_list_notes(False, 'test_search_string')
    nncli.nncli.print.assert_called_once_with('test_key [flg] test_title')
    nncli.utils.get_note_flags.assert_called_once()
    nncli.utils.get_note_title.assert_called_once()

def test_cli_note_dump(mocker, mock_nncli):
    """test dumping a note to the command line"""
    test_note = {'modified': 12345,
                 'id': 1,
                 'localkey': 1,
                 'content': 'test_content'}
    mocker.patch('nncli.utils.get_note_flags',
                 new=mocker.Mock(return_value='flg'))
    mocker.patch('nncli.utils.get_note_title',
                 new=mocker.Mock(return_value='test_title'))
    mocker.patch('nncli.utils.get_note_category',
                 new=mocker.Mock(return_value='test_category'))
    mocker.patch('nncli.nncli.print')
    nn_obj = nncli.nncli.Nncli(False)
    mocker.patch.object(nn_obj.ndb, 'get_note',
                        new=mocker.Mock(return_value=test_note))
    nn_obj.cli_note_dump(1)
    assert nncli.nncli.print.call_count == 8
    nn_obj.ndb.get_note.assert_called_once_with(1)
    nncli.utils.get_note_flags.assert_called_once_with(test_note)
    nncli.utils.get_note_title.assert_called_once_with(test_note)
    nncli.utils.get_note_category.assert_called_once_with(test_note)

def test_failed_cli_note_dump(mocker, mock_nncli):
    """test failed note dump to the command line"""
    mocker.patch('nncli.utils.get_note_flags',
                 new=mocker.Mock(return_value='flg'))
    mocker.patch('nncli.utils.get_note_title',
                 new=mocker.Mock(return_value='test_title'))
    mocker.patch('nncli.utils.get_note_category',
                 new=mocker.Mock(return_value='test_category'))
    mocker.patch('nncli.nncli.print')
    nn_obj = nncli.nncli.Nncli(False)
    mocker.patch.object(nn_obj.ndb, 'get_note',
                        new=mocker.Mock(return_value = None))
    nn_obj.cli_note_dump(1)
    nncli.nncli.print.assert_not_called()
    nn_obj.ndb.get_note.assert_called_once_with(1)
    nncli.utils.get_note_flags.assert_not_called()
    nncli.utils.get_note_title.assert_not_called()
    nncli.utils.get_note_category.assert_not_called()

def test_cli_dump_notes(mocker, mock_nncli):
    """test cli_dump_notes"""
    test_notes = (
            [nncli.utils.KeyValueObject(key=1,
             note={'key': 1})],
            [],
            []
            )
    nn_obj = nncli.nncli.Nncli(False)
    mocker.patch.object(nn_obj.ndb, 'filter_notes',
                        new=mocker.Mock(return_value=test_notes))
    mocker.patch.object(nn_obj, 'cli_note_dump')
    nn_obj.cli_dump_notes(False, 'test_search_string')
    nn_obj.cli_note_dump.assert_called_once_with(1)

def test_cli_note_create(mocker, mock_nncli):
    """test cli_note_create"""
    mocker.patch('nncli.nncli.exec_cmd_on_note',
                 new=mocker.Mock(return_value='test content'))
    nn_obj = nncli.nncli.Nncli(False)
    mocker.patch.object(nn_obj.ndb, 'create_note')
    mocker.patch.object(nn_obj.ndb, 'sync_now')
    nn_obj.cli_note_create(False, 'test title')
    nncli.nncli.exec_cmd_on_note.assert_called_once()
    nn_obj.ndb.create_note.assert_called_once_with('test title\n\ntest content')
    nn_obj.ndb.sync_now.assert_called_once()

def test_cli_note_create_from_stdin(mocker, mock_nncli):
    """test cli_note_create reading from stdin"""
    mocker.patch('sys.stdin', new=StringIO('test content'))
    nn_obj = nncli.nncli.Nncli(False)
    mocker.patch.object(nn_obj.ndb, 'create_note')
    mocker.patch.object(nn_obj.ndb, 'sync_now')
    nn_obj.cli_note_create(True, 'test title')
    nn_obj.ndb.create_note.assert_called_once_with('test title\n\ntest content')
    nn_obj.ndb.sync_now.assert_called_once()

def test_cli_note_create_no_title(mocker, mock_nncli):
    """test cli_note_create without a title"""
    mocker.patch('sys.stdin', new=StringIO('test content'))
    nn_obj = nncli.nncli.Nncli(False)
    mocker.patch.object(nn_obj.ndb, 'create_note')
    mocker.patch.object(nn_obj.ndb, 'sync_now')
    nn_obj.cli_note_create(True, None)
    nn_obj.ndb.create_note.assert_called_once_with('test content')
    nn_obj.ndb.sync_now.assert_called_once()

def test_cli_note_create_no_content(mocker, mock_nncli):
    """test failed cli_note_create without content"""
    mocker.patch('sys.stdin', new=StringIO(None))
    nn_obj = nncli.nncli.Nncli(False)
    mocker.patch.object(nn_obj.ndb, 'create_note')
    mocker.patch.object(nn_obj.ndb, 'sync_now')
    nn_obj.cli_note_create(True, None)
    nn_obj.ndb.create_note.assert_not_called()
    nn_obj.ndb.sync_now.assert_not_called()

def test_cli_note_import(mocker, mock_nncli):
    """test cli_note_import"""
    mocker.patch('nncli.nncli.exec_cmd_on_note',
                 new=mocker.Mock(return_value='{"content": "test"}'))
    nn_obj = nncli.nncli.Nncli(False)
    mocker.patch.object(nn_obj.ndb, 'import_note')
    mocker.patch.object(nn_obj.ndb, 'sync_now')
    nn_obj.cli_note_import(False)
    nncli.nncli.exec_cmd_on_note.assert_called_once()
    nn_obj.ndb.import_note.assert_called_once_with({'content': 'test'})
    nn_obj.ndb.sync_now.assert_called_once()

def test_cli_note_import_from_stdin(mocker, mock_nncli):
    """test cli_note_import"""
    mocker.patch('sys.stdin',
                 new=StringIO('{"content": "test"}'))
    nn_obj = nncli.nncli.Nncli(False)
    mocker.patch.object(nn_obj.ndb, 'import_note')
    mocker.patch.object(nn_obj.ndb, 'sync_now')
    nn_obj.cli_note_import(True)
    nn_obj.ndb.import_note.assert_called_once_with({'content': 'test'})
    nn_obj.ndb.sync_now.assert_called_once()

def test_cli_note_import_json_error(mocker, mock_nncli):
    """test cli_note_import failure at json decode"""
    mocker.patch('nncli.nncli.exec_cmd_on_note',
                 new=mocker.Mock(return_value='{"content", "test"}'))
    nn_obj = nncli.nncli.Nncli(False)
    mocker.patch.object(nn_obj.ndb, 'import_note')
    mocker.patch.object(nn_obj.ndb, 'sync_now')
    with pytest.raises(SystemExit):
        nn_obj.cli_note_import(False)
    nncli.nncli.exec_cmd_on_note.assert_called_once()
    nn_obj.logger.log.assert_called_once()
    nn_obj.ndb.import_note.assert_not_called()
    nn_obj.ndb.sync_now.assert_not_called()

def test_cli_note_import_value_error(mocker, mock_nncli):
    """test cli_note_import failure"""
    mocker.patch('nncli.nncli.exec_cmd_on_note',
                 new=mocker.Mock(return_value='{"content": "test"}'))
    nn_obj = nncli.nncli.Nncli(False)
    mocker.patch.object(nn_obj.ndb, 'import_note',
                        new=mocker.Mock(side_effect=ValueError))
    mocker.patch.object(nn_obj.ndb, 'sync_now')
    with pytest.raises(SystemExit):
        nn_obj.cli_note_import(False)
    nncli.nncli.exec_cmd_on_note.assert_called_once()
    assert nn_obj.logger.log.call_count == 2
    nn_obj.ndb.import_note.assert_called_once()
    nn_obj.ndb.sync_now.assert_not_called()

def test_cli_note_export(mocker, mock_nncli):
    """test exporting a note as raw JSON"""
    mocker.patch('nncli.nncli.print')
    nn_obj = nncli.nncli.Nncli(False)
    mocker.patch.object(nn_obj.ndb, 'get_note',
                        new=mocker.Mock(return_value={'content': 'test'}))
    nn_obj.cli_note_export(1)
    nn_obj.ndb.get_note.assert_called_once_with(1)
    nncli.nncli.print.assert_called_once()

def test_cli_note_export_no_note(mocker, mock_nncli):
    """test failed note export (key not in DB)"""
    mocker.patch('nncli.nncli.print')
    nn_obj = nncli.nncli.Nncli(False)
    mocker.patch.object(nn_obj.ndb, 'get_note',
                        new=mocker.Mock(return_value=None))
    nn_obj.cli_note_export(1)
    nn_obj.ndb.get_note.assert_called_once_with(1)
    nn_obj.logger.log.assert_called_once()
    nncli.nncli.print.assert_not_called()

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
