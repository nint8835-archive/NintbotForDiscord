from enum import Enum
__author__ = 'Riley Flynn (nint8835)'


class SelectionMode(Enum):
    """An enum containing all of the possible selection modes"""

    VALUE_GREATER_THAN = ">"
    VALUE_LESS_THAN = "<"
    VALUE_EQUALS = "="
    VALUE_GREATER_THAN_OR_EQUAL = ">="
    VALUE_LESS_THAN_OR_EQUAL = "<="
    VALUE_NOT_EQUAL = "!="
    REGEX_MATCH = "RE_MATCH"
    ALL = "*"
