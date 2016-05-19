import json
import os
import re
from .Selection import DatabaseSelection
from .Enums import SelectionMode
__author__ = 'Riley Flynn (nint8835)'


class JSONDatabase:

    def __init__(self, path):
        self.path = path
        if os.path.isfile(path):
            with open(path) as f:
                self.data = json.load(f)
        else:
            # If the file doesn't exist, write blank data to the file.
            self.data = []
            self.save_db()

    def save_db(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f)

    def select(self, mode: SelectionMode, key="", selection_var=""):
        """
        Selects rows from the database that match certain criteria
        :param mode: The mode of selection used to perform the selection
        :param key: The key to perform the selection on
        :param selection_var: The variable to be used for the selection
        :return: A DatabaseSelection object containing the selection
        """
        if mode == SelectionMode.VALUE_LESS_THAN:
            return DatabaseSelection([row for row in self.data if row[key] < selection_var], self)

        if mode == SelectionMode.VALUE_GREATER_THAN:
            return DatabaseSelection([row for row in self.data if row[key] > selection_var], self)

        if mode == SelectionMode.VALUE_EQUALS:
            return DatabaseSelection([row for row in self.data if row[key] == selection_var], self)

        if mode == SelectionMode.VALUE_GREATER_THAN_OR_EQUAL:
            return DatabaseSelection([row for row in self.data if row[key] >= selection_var], self)

        if mode == SelectionMode.VALUE_LESS_THAN_OR_EQUAL:
            return DatabaseSelection([row for row in self.data if row[key] <= selection_var], self)

        if mode == SelectionMode.VALUE_NOT_EQUAL:
            return DatabaseSelection([row for row in self.data if row[key] != selection_var], self)

        if mode == SelectionMode.VALUE_IN:
            return DatabaseSelection([row for row in self.data if selection_var in row[key]], self)

        if mode == SelectionMode.REGEX_MATCH:
            regex = re.compile(selection_var)
            return DatabaseSelection([row for row in self.data if regex.match(row[key])], self)

        if mode == SelectionMode.ALL:
            return DatabaseSelection(self.data[:], self)

    def insert(self, row: dict, save_after: bool=True):
        """
        Inserts a new row into the database
        :param row: The row you wish to insert
        :param save_after: Whether to write the database to disk after inserting the row
        """
        self.data.append(row)
        if save_after:
            self.save_db()
