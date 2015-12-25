from discord import Game
from NintbotForDiscord.Enums import EventTypes
from NintbotForDiscord.EventManager import event_handler, register_handler
from NintbotForDiscord.Plugin import BasePlugin
import asyncio
__author__ = 'Riley Flynn (nint8835)'


class Plugin(BasePlugin):

    def __init__(self, bot):
        super(Plugin, self).__init__(bot)
        for eventtype in EventTypes:
            register_handler(eventtype, self.event_test)

    @asyncio.coroutine
    @event_handler(EventTypes.Message)
    def channel_message(self, args):
        if args["message"].content.startswith("!setgame "):
            game = args["message"].content.split("!setgame ")[1]
            yield from args["bot"].change_status(game=Game(name=game))

    @asyncio.coroutine
    def event_test(self, args):
        print(str(args))
