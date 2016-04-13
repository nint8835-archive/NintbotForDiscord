import json
import os
import traceback

from .Bot import Bot
import io
__author__ = 'Riley Flynn (nint8835)'


class BotLauncher:

    def __init__(self, auto_reboot: bool = False, max_reboots: int = 10):
        self.config = self._get_config()
        self.max_reboots = max_reboots
        self.auto_reboot = auto_reboot
        self.reboots = 0
        while self.reboots <= max_reboots:
            try:
                self._bot = Bot(self.config)
            except:
                traceback.print_exc(5)
            self.reboots += 1
            if not self.auto_reboot:
                self.reboots = self.max_reboots

    def _get_config(self) -> dict:
        """
        Returns the config
        :return: The config (in this case an empty dict)
        """
        return {}


class StreamBotLauncher(BotLauncher):

    def __init__(self, f: io.TextIOWrapper, auto_reboot: bool = False, max_reboots: int = 10):
        self._stream = f
        super(StreamBotLauncher, self).__init__(auto_reboot, max_reboots)

    def _get_config(self) -> dict:
        """
        Returns the config
        :return: The config (in this case a dictionary loaded from a I/O stream
        """
        return json.load(self._stream)


class FileBotLauncher(StreamBotLauncher):

    def __init__(self, path: str, auto_reboot: bool = False, max_reboots: int = 10):
        if os.path.exists(path):
            with open(path) as f:
                super(FileBotLauncher, self).__init__(f, auto_reboot, max_reboots)
