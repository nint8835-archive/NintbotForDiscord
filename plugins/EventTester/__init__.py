from NintbotForDiscord.Enums import EventTypes
from NintbotForDiscord.Plugin import BasePlugin
__author__ = 'Riley Flynn (nint8835)'


class Plugin(BasePlugin):

    def __init__(self, bot_instance, plugin_data, folder):
        super(Plugin, self).__init__(bot_instance, plugin_data, folder)
        for eventtype in EventTypes:
            bot_instance.register_handler(eventtype, self.event_test, self)

    @staticmethod
    async def event_test(args):
        print(str(args))
