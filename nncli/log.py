# -*- coding: utf-8 -*-
"""log module"""
import logging
from logging.handlers import RotatingFileHandler

import os

# pylint: disable=unused-argument, too-few-public-methods
class Logger:
    """Handles logging for the application"""
    def __init__(self, config):
        self.config = config
        self.logfile = os.path.join(
                config.get_config('db_path'),
                'nncli.log'
                )
        self.loghandler = RotatingFileHandler(
                self.logfile,
                maxBytes=100000,
                backupCount=1
                )
        self.loghandler.setLevel(logging.DEBUG)
        self.loghandler.setFormatter(
                logging.Formatter(
                        fmt='%(asctime)s [%(levelname)s] %(message)s'
                        )
                )
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.loghandler)

        logging.debug('nncli logging initialized')

    def log(self, msg):
        """Log as message, displaying to the user as appropriate"""
        logging.debug(msg)

        if not self.config.state.do_gui:
            if self.config.state.verbose:
                print(msg)
