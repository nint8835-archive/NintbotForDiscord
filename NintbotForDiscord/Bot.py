import discord
import asyncio
import json
from .EventManager import EventManager
from .Enums import EventTypes
__author__ = 'Riley Flynn (nint8835)'


class Bot(discord.Client):

    def __init__(self, config: dict, loop: asyncio.BaseEventLoop=None):
        super(Bot, self).__init__(loop=loop)
        self._config = config
        self._EventManager = EventManager(self)
        self._EventManager.register_handler(EventTypes.GenericMessage, self.log_message)
        self.run(config["email"], config["password"])

    @asyncio.coroutine
    def on_message(self, message: discord.Message):
        self._EventManager.throw_event(EventTypes.GenericMessage,
                                       message=message,
                                       author=message.author,
                                       channel=message.channel)
        if message.channel.is_private:
            self._EventManager.throw_event(EventTypes.PrivateMessage,
                                           message=message,
                                           author=message.author,
                                           channel=message.channel)
        else:
            self._EventManager.throw_event(EventTypes.ChannelMessage,
                                           message=message,
                                           author=message.author,
                                           channel=message.channel)

    @staticmethod
    def log_message(**kwargs):
        print("{}: {}".format(kwargs["author"].name, kwargs["message"].content))

