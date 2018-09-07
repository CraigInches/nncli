# -*- coding: utf-8 -*-
"""clipboard module"""
import os
from distutils import spawn

class Clipboard:
    """Class implements copying note content to the clipboard"""
    def __init__(self):
        self.copy_command = self.get_copy_command()

    @staticmethod
    def get_copy_command():
        """Defines the copy command based on the contents of $PATH"""
        if spawn.find_executable('xsel'):
            return 'echo "%s" | xsel -ib'
        if spawn.find_executable('pbcopy'):
            return 'echo "%s" | pbcopy'
        return None

    def copy(self, text):
        """Copies text to the system clipboard"""
        if self.copy_command:
            os.system(self.copy_command % text)
