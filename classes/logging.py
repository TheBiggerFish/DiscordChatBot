"""Module to handle logging and logging configuration"""

import logging
import logging.handlers
import socket
import sys
from typing import Optional


class Logger(logging.Logger):
    """Class to handle logging for chatbot"""

    def __init__(self, name:str, host:Optional[str], port:str='514', level:str='INFO'):
        """Perform formatting and handling configuration and return logging.Logger"""

        super().__init__(name)

        if host is None:
            handler = logging.StreamHandler(sys.stdout)
        else:
            handler = logging.handlers.SysLogHandler(address=(host,int(port)))

        formatter = logging.Formatter(fmt=f'{socket.gethostname()} '\
            '[%(levelname)s] %(process)s {%(name)s} %(message)s')
        handler.setFormatter(formatter)
        self.addHandler(handler)
        self.setLevel(level)
