import traceback

from .Enums import EventTypes
from .Plugin import BasePlugin
import asyncio
__author__ = 'Riley Flynn (nint8835)'


class EventManager:

    def __init__(self, bot_instance):
        self._handlers = []
        self._bot = bot_instance
        self.loop = asyncio.get_event_loop()
        self.queue = asyncio.Queue(loop = self.loop)
        self.loop.create_task(self.event_handle_loop())

    async def event_handle_loop(self):
        while not self._bot.is_closed:
            handler = await self.queue.get()
            try:
                await asyncio.wait_for(handler["handler"](handler["args"]), timeout = self._bot.config["event_timeout"], loop = self.loop)
            except asyncio.TimeoutError:
                self._bot.logger.warning("Handling of {} event from plugin {} timed out.".format(handler["type"], handler["plugin"].plugin_data["plugin_name"]))

    def register_handler(self, event_type: EventTypes, event_handler, plugin: BasePlugin):
        self._handlers.append({"type": event_type, "handler": event_handler, "plugin": plugin})

    async def dispatch_event(self, event_type: EventTypes, **kwargs):
        for handler in self._handlers:
            if handler["type"] == event_type:
                new_args = kwargs
                new_args["bot"] = self._bot
                new_args["event_type"] = event_type
                try:
                    await self.queue.put({"handler": handler["handler"], "type": event_type, "args": new_args, "plugin": handler["plugin"]})
                except:
                    traceback.print_exc(5)
                # asyncio.ensure_future(handler["handler"](new_args), loop = self.loop)
