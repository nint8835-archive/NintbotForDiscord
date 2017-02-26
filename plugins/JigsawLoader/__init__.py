import logging
import os
import traceback

from jigsaw import PluginLoader

from NintbotForDiscord.Plugin import BasePlugin
from plugins.JigsawLoader.NintbotPlugin import NintbotPlugin


class Plugin(BasePlugin):

    def __init__(self, bot_instance, plugin_data, folder):
        try:
            super(Plugin, self).__init__(bot_instance, plugin_data, folder)
            self._logger = logging.getLogger("JigsawLoader")

            self._logger.debug("Initializing Jigsaw...")
            self._jigsaw = PluginLoader(os.path.join(folder, os.pardir, os.pardir, "jigsaw_plugins"),
                                        plugin_class=NintbotPlugin)
            self._logger.debug("Jigsaw initialized.")

            self._logger.debug("Loading Jigsaw manifests...")
            self._jigsaw.load_manifests()
            self._logger.debug("Jigsaw manifests loaded.")

            self._logger.debug("Loading Jigsaw plugins...")
            self._jigsaw.load_plugins(bot_instance)
            self._logger.debug("Jigsaw plugins loaded.")
        except:
            traceback.print_exc(5)
