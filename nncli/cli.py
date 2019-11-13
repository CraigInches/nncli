# -*- coding: utf-8 -*-
"""Command line interface module"""
import click

from . import __version__
from .nncli import Nncli

# pylint: disable=unnecessary-pass

class StdinFlag(click.ParamType):
    """StdinFlag Click Parameter Type"""
    name = "stdin_flag"

    def convert(self, value, param, ctx):
        if value == '-':
            return True
        return self.fail('%s is not a valid stdin_flag')

STDIN_FLAG = StdinFlag()

@click.command()
@click.pass_obj
def rm_category(ctx_obj):
    """Remove note category."""
    nncli = ctx_obj['nncli']
    key = ctx_obj['key']
    nncli.cli_note_category_rm(key)

@click.command()
@click.argument('category', required=True)
@click.pass_obj
def set_category(ctx_obj, category):
    """Set the note category."""
    nncli = ctx_obj['nncli']
    key = ctx_obj['key']
    nncli.cli_note_category_set(key, category)

@click.command(short_help="Print the note category.")
@click.pass_obj
def get_category(ctx_obj):
    """Print the category for the given note on stdout."""
    nncli = ctx_obj['nncli']
    key = ctx_obj['key']
    category = nncli.cli_note_category_get(key)
    if category:
        print(category)

@click.group()
@click.option(
        '-k',
        '--key',
        required=True,
        type=click.INT,
        help="Specify the note key."
        )
@click.pass_context
def cat(ctx, key):
    """Operate on the note category."""
    nncli = ctx.obj
    ctx.obj = {}
    ctx.obj['nncli'] = nncli
    ctx.obj['key'] = key

cat.add_command(get_category, 'get')
cat.add_command(set_category, 'set')
cat.add_command(rm_category, 'rm')

@click.command()
@click.option(
        '-k',
        '--key',
        required=True,
        type=click.INT,
        help="Specify the note key.")
@click.pass_obj
def favorite(nncli, key):
    """Mark as note as a favorite."""
    nncli.cli_note_favorite(key, 1)

@click.command()
@click.option(
        '-k',
        '--key',
        required=True,
        type=click.INT,
        help="Specify the note key."
        )
@click.pass_obj
def unfavorite(nncli, key):
    """Remove favorite flag from a note."""
    nncli.cli_note_favorite(key, 0)

@click.command(short_help="Print JSON-formatted note to stdout.")
@click.option('-k', '--key', type=click.INT, help="Specify the note key.")
@click.option(
        '-r',
        '--regex',
        is_flag=True,
        help="Treat search term(s) as regular expressions."
        )
@click.argument('search_terms', nargs=-1)
@click.pass_obj
def export(nncli, key, regex, search_terms):
    """
    Print JSON-formatted note to stdout. If a key is specified, then regex
    and search_terms are ignored.
    """
    if key:
        nncli.cli_note_export(key)
    else:
        nncli.cli_export_notes(regex, ' '.join(search_terms))

@click.command(short_help="Print note contents to stdout.")
@click.option('-k', '--key', type=click.INT, help="Specify the note key.")
@click.option(
        '-r',
        '--regex',
        is_flag=True,
        help="Treat search term(s) as regular expressions."
        )
@click.argument('search_terms', nargs=-1)
@click.pass_obj
def dump(nncli, key, regex, search_terms):
    """
    Print note contents to stdout. If a key is specified, then regex
    and search_terms are ignored.
    """
    if key:
        nncli.cli_note_dump(key)
    else:
        nncli.cli_dump_notes(regex, ' '.join(search_terms))

@click.command(short_help="List notes.")
@click.option(
        '-r',
        '--regex',
        is_flag=True,
        help="Treat search term(s) as regular expressions."
        )
@click.argument('search_terms', nargs=-1)
@click.pass_obj
def list_notes(nncli, regex, search_terms):
    """
    List notes, optionally providing search terms to narrow the
    results.
    """
    nncli.cli_list_notes(regex, ' '.join(search_terms))

@click.command(short_help="Sync notes to server.")
def sync():
    """
    Perform a full, bi-directional sync of your notes between the
    server and the local cache.
    """
    pass

@click.command()
@click.option(
        '-k',
        '--key',
        required=True,
        type=click.INT,
        help="Specify the note key."
        )
@click.pass_obj
def delete(nncli, key):
    """Delete an existing note."""
    nncli.cli_note_delete(key, True)

@click.command()
@click.option(
        '-k',
        '--key',
        required=True,
        type=click.INT,
        help="Specify the note key."
        )
@click.pass_obj
def edit(nncli, key):
    """Edit an existing note."""
    nncli.cli_note_edit(key)

@click.command(short_help="Import a JSON note.")
@click.argument('from_stdin', metavar='[-]', type=STDIN_FLAG)
@click.pass_obj
def json_import(nncli, from_stdin):
    """
    Import a JSON-formatted note file into your account. The expected
    JSON format is the same format used internally by nncli. If - is
    specified, the note is read from stdin, otherwise the editor will
    open.
    """
    nncli.cli_note_import(from_stdin)

@click.command(short_help="Add a new note.")
@click.option('-t', '--title', help="Specify the title of note for create.")
@click.argument('from_stdin', metavar='[-]', type=STDIN_FLAG, required=False)
@click.pass_obj
def create(nncli, title, from_stdin):
    """
    Create a new note, either opening the editor or, if - is specified,
    reading from stdin.
    """
    nncli.cli_note_create(from_stdin, title)

@click.group(invoke_without_command=True)
@click.option(
        '-n',
        '--nosync',
        is_flag=True,
        help="Don't perform a server sync."
        )
@click.option('-v', '--verbose', is_flag=True, help="Print verbose output.")
@click.option(
        '-c',
        '--config',
        type=click.Path(exists=True),
        help="Specify the config file to read from."
        )
@click.option('-k', '--key', type=click.INT, help="Specify the note key.")
@click.version_option(version=__version__, message='%(prog)s %(version)s')
@click.pass_context
def main(ctx, nosync, verbose, config, key):
    """
    Run the NextClound Note Command Line Interface. No COMMAND means
    to open the console GUI.
    """
    ctx.obj = Nncli(not nosync, verbose, config)
    if ctx.invoked_subcommand is None:
        ctx.obj.gui(key)
    elif not nosync:
        ctx.obj.ndb.sync_notes()

main.add_command(create)
main.add_command(edit)
main.add_command(delete)
main.add_command(sync)
main.add_command(json_import, name='import')
main.add_command(list_notes, name='list')
main.add_command(dump)
main.add_command(export)
main.add_command(favorite)
main.add_command(unfavorite)
main.add_command(cat)
