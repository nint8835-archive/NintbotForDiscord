__author__ = 'Riley Flynn (nint8835)'


class BasePlugin:

    def __init__(self, bot, plugin_data, folder):
        self.bot = bot
        self.plugin_data = plugin_data
        self.folder = folder
