try:
    from . import version
    __version__ = version.version
except ImportError:
    try:
        from setuptools_scm import get_version
        __version__ = get_version(root='..', relative_to=__file__)
    except:
        __version__ = '??-dev'

__productname__ = 'nncli'
__copyright__ = "Copyright (c) 2018 Daniel Moch"
__author__ = "Daniel Moch"
__author_email__ = "daniel@danielmoch.com"
__description__ = "NextCloud Notes Command Line Interface"
__url__ = "https://github.com/djmoch/nncli"
__license__ = "MIT"
