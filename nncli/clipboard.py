# -*- coding: utf-8 -*-
"""clipboard module"""
import os
import subprocess
from subprocess import CalledProcessError, DEVNULL

class Clipboard:
    """Class implements copying note content to the clipboard"""
    def __init__(self):
        self.copy_command = self.get_copy_command()

    @staticmethod
    def get_copy_command():
        """Defines the copy command based on the contents of $PATH"""

        try:
            subprocess.check_call(['which', 'xsel'], stdout=DEVNULL, \
                    stderr=DEVNULL)
            return 'echo "%s" | xsel -ib'
        except CalledProcessError:
            pass

        try:
            subprocess.check_call(['which', 'pbcopy'], stdout=DEVNULL, \
                    stderr=DEVNULL)
            return 'echo "%s" | pbcopy'
        except CalledProcessError:
            pass

        try:
            subprocess.check_call(['which', 'xclip'], stdout=DEVNULL, \
                    stderr=DEVNULL)
            return 'echo "%s" | xclip -selection clipboard'
        except CalledProcessError:
            pass

        return None

    def copy(self, text):
        """Copies text to the system clipboard"""
        if self.copy_command:
            os.system(self.copy_command % text)
