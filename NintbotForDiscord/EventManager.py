from .Enums import EventTypes
import asyncio
__author__ = 'Riley Flynn (nint8835)'


class EventManager:

    def __init__(self, bot_instance):
        self._handlers = []
        self._bot = bot_instance

    def register_handler(self, event_type: EventTypes, event_handler):
        self._handlers.append({"type": event_type, "handler": event_handler})

    def dispatch_event(self, event_type: EventTypes, **kwargs):
        for handler in self._handlers:
            if handler["type"] == event_type:
                new_args = kwargs
                new_args["bot"] = self._bot
                new_args["event_type"] = event_type
                asyncio.Task(handler["handler"](new_args))
