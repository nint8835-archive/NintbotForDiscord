from enum import Enum
__author__ = 'Riley Flynn (nint8835)'


class EventTypes(Enum):
    ChannelMessage = "channel_message"
    PrivateMessage = "private_message"
    GenericMessage = "message"
