from discord import Game
from NintbotForDiscord.Enums import EventTypes
from NintbotForDiscord.Plugin import BasePlugin
import asyncio
__author__ = 'Riley Flynn (nint8835)'


class Plugin(BasePlugin):

    def __init__(self, bot):
        super(Plugin, self).__init__(bot)
        print("Registering event")
        self.bot = bot
        bot._EventManager.register_handler(EventTypes.ChannelMessage, self.channel_message)
        for eventtype in EventTypes:
            bot._EventManager.register_handler(eventtype, self.event_test)
        print("Event registered")

    @asyncio.coroutine
    def channel_message(self, args):
        if args["message"].content.startswith("!setgame "):
            game = args["message"].content.split("!setgame ")[1]
            yield from args["bot"].change_status(game=Game(name=game))

    @asyncio.coroutine
    def event_test(self, args):
        print(str(args))
