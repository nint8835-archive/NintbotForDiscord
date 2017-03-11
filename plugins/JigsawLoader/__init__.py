import logging
import os
import traceback

from NintbotForDiscord.Permissions import Permission
from NintbotForDiscord.Permissions.Special import Owner
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

            self._logger.debug("Enabling Jigsaw plugins...")
            self._jigsaw.enable_all_plugins()
            self._logger.debug("Jigsaw plugins enabled.")

            self.bot.CommandRegistry.register_command("jigsawplugins",
                                                      "Views the currently installed plugins.",
                                                      Permission(),
                                                      plugin_data,
                                                      self.command_jigsawplugins)

            self.bot.CommandRegistry.register_command("reloadplugins",
                                                      "Reloads all modern (jigsaw) plugins.",
                                                      Owner(self.bot),
                                                      plugin_data,
                                                      self.command_reloadplugins)

        except:
            traceback.print_exc(5)

    async def command_jigsawplugins(self, args):
        message = "```\n"

        for plugin in self._jigsaw.get_all_plugins():
            message += f"{plugin['manifest']['name']}\n"
            message += f"\tVersion: {plugin['manifest'].get('version', '0.0.0')}\n"
            message += f"\tDeveloper: {plugin['manifest'].get('developer', 'Unspecified Developer')}\n"
            message += f"\tDependencies: {', '.join(plugin['manifest'].get('dependencies', []))}\n"

        message += "```"

        await self.bot.send_message(args["channel"], message)

    async def command_reloadplugins(self, args):
        self._jigsaw.reload_all_plugins(self.bot)
        await self.bot.send_message(args["channel"], "Plugins reloaded")
