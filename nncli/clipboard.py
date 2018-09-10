# -*- coding: utf-8 -*-
"""clipboard module"""
import os
import subprocess
from subprocess import CalledProcessError

class Clipboard:
    """Class implements copying note content to the clipboard"""
    def __init__(self):
        self.copy_command = self.get_copy_command()

    @staticmethod
    def get_copy_command():
        """Defines the copy command based on the contents of $PATH"""

        try:
            subprocess.check_output(['which', 'xsel'])
            return 'echo "%s" | xsel -ib'
        except CalledProcessError:
            pass

        try:
            subprocess.check_output(['which', 'pbcopy'])
            return 'echo "%s" | pbcopy'
        except CalledProcessError:
            pass

        return None

    def copy(self, text):
        """Copies text to the system clipboard"""
        if self.copy_command:
            os.system(self.copy_command % text)
