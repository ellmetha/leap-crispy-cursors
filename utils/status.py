# -*- coding: utf-8 -*-

# Standard library imports
import sys

# Third party imports
# Local application / specific library imports


class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    ORANGE = '\033[93m'
    NO = '\033[0m'

    def disable(self):
        self.RED = ''
        self.GREEN = ''
        self.BLUE = ''
        self.ORANGE = ''
        self.NO = ''


class Status:
    RUNNING = "Running"
    SUCCESS = "OK"
    WARNING = "Warning"
    ERROR = "Error"


def showmessage(message, status, color, update=False, newline=False):
    if update:
        sys.stdout.write(Colors.NO + "\r{0}".format(message) + color + "%s" % '[{0}]'.format(status).rjust(79-len(message)) + Colors.NO)
    else:
        sys.stdout.write(Colors.NO + "{0}".format(message) + color + "%s" % '[{0}]'.format(status).rjust(79-len(message)) + Colors.NO)
        sys.stdout.flush()
    if newline:
        sys.stdout.write("\n")