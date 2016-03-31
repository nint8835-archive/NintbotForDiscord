import re

from .Enums import SelectionMode
from .Exceptions import SelectionReuseException
__author__ = 'Riley Flynn (nint8835)'


class DatabaseSelection:

    """
    Represents a selection of items from a JSON DB.
    Can have items retrieved from it, or can be modified.
    Upon modification the selection object becomes unusable and must be recreated by performing the selection again.
    """

    def __init__(self, data: list, db):
        """
        Creates a new instance of DatabaseSelection
        :param data: A list of rows from a db.
        :param db: The JSONDatabase instance that the rows came from. Used to perform modifications.
        """
        self.db = db
        self.rows = data
        self._selection_modified = False

    def __getitem__(self, item):
        if not self._selection_modified:
            return self.rows[item]
        else:
            raise SelectionReuseException()

    def __len__(self):
        if not self._selection_modified:
            return len(self.rows)
        else:
            raise SelectionReuseException()

    def __str__(self):
        if not self._selection_modified:
            return "DatabaseSelection from database at {}, containing the following rows: {}".format(self.db.path, self.rows)
        else:
            return "Unusable DatabaseSelection object. Perform a new selection to get a usable one."

    def __repr__(self):
        if not self._selection_modified:
            return "DatabaseSelection({}, {})".format(self.rows, self.db)
        else:
            return ""

    def remove(self):
        """
        Removes all rows contained in this selection from the DB
        """
        if not self._selection_modified:
            for row in self.rows:
                self.db.data.remove(row)
            self.db.save_db()
            self._selection_modified = True
            self.rows = []
        else:
            raise SelectionReuseException()

    def update(self, key, value):
        """
        Updates the value of a certain key of all rows contained in this selection
        :param key: The key you wish to update
        :param value: The new value
        """
        if not self._selection_modified:
            for row in self.rows:
                self.db.data[self.db.data.index(row)][key] = value
            self.db.save_db()
            self._selection_modified = True
            self.rows = []
        else:
            raise SelectionReuseException()

    def select(self, mode: SelectionMode, key="", selection_var=""):
        """
        Further refines this selection
        :param mode: The mode of selection used to refine the selection
        :param key: The key to perform the selection on
        :param selection_var: The variable to be used for the selection
        :return: A DatabaseSelection object containing the refined selection
        """
        if not self._selection_modified:
            if mode == SelectionMode.VALUE_LESS_THAN:
                return DatabaseSelection([row for row in self.rows if row[key] < selection_var], self.db)

            if mode == SelectionMode.VALUE_GREATER_THAN:
                return DatabaseSelection([row for row in self.rows if row[key] > selection_var], self.db)

            if mode == SelectionMode.VALUE_EQUALS:
                return DatabaseSelection([row for row in self.rows if row[key] == selection_var], self.db)

            if mode == SelectionMode.VALUE_GREATER_THAN_OR_EQUAL:
                return DatabaseSelection([row for row in self.rows if row[key] >= selection_var], self.db)

            if mode == SelectionMode.VALUE_LESS_THAN_OR_EQUAL:
                return DatabaseSelection([row for row in self.rows if row[key] <= selection_var], self.db)

            if mode == SelectionMode.VALUE_NOT_EQUAL:
                return DatabaseSelection([row for row in self.rows if row[key] != selection_var], self.db)

            if mode == SelectionMode.REGEX_MATCH:
                regex = re.compile(selection_var)
                return DatabaseSelection([row for row in self.rows if regex.match(row["key"])], self.db)

            if mode == SelectionMode.ALL:
                return DatabaseSelection(self.rows, self)
        else:
            raise SelectionReuseException()
