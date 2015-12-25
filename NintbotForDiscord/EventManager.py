from .Enums import EventTypes
import asyncio
__author__ = 'Riley Flynn (nint8835)'

handlers = []
bot = None

def update_bot(bot_instance):
    global bot
    bot = bot_instance


def register_handler(event_type: EventTypes, event_handler):
    handlers.append({"type": event_type, "handler": event_handler})


def dispatch_event(event_type: EventTypes, **kwargs):
    for handler in handlers:
        if handler["type"] == event_type:
            new_args = kwargs
            new_args["bot"] = bot
            new_args["event_type"] = event_type
            asyncio.Task(handler["handler"](new_args))


def event_handler(event_type: EventTypes):
    def wrap(f):
        register_handler(event_type, f)

        def wrapped_f(self, args):
            f(self, args)
        return wrapped_f
    return wrap
