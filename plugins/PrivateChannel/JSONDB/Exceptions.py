__author__ = 'Riley Flynn (nint8835)'


class SelectionReuseException(Exception):

    def __init__(self):
        super(SelectionReuseException, self).__init__("An attempt was made to reuse a selection after it had been modified.")
