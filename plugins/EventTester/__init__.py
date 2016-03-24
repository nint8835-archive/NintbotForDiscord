from NintbotForDiscord.Enums import EventTypes
from NintbotForDiscord.Plugin import BasePlugin
__author__ = 'Riley Flynn (nint8835)'


class Plugin(BasePlugin):

    def __init__(self, bot, plugin_data, folder):
        super(Plugin, self).__init__(bot, plugin_data, folder)
        for eventtype in EventTypes:
            bot.register_handler(eventtype, self.event_test, self)

    @staticmethod
    async def event_test(args):
        print(str(args))
