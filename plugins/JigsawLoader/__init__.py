import json
import logging
import os
import traceback

from NintbotForDiscord.Permissions import Permission
from NintbotForDiscord.Permissions.Special import Owner
from NintbotForDiscord.Plugin import BasePlugin

from jigsaw import PluginLoader
from plugins.JigsawLoader.NintbotPlugin import NintbotPlugin


class Plugin(BasePlugin):

    def __init__(self, bot_instance, plugin_data, folder):
        try:
            super(Plugin, self).__init__(bot_instance, plugin_data, folder)
            self._logger = logging.getLogger("JigsawLoader")

            self._logger.debug("Initializing Jigsaw...")
            self._jigsaw = PluginLoader(os.path.abspath(os.path.join(folder, os.pardir, os.pardir, "jigsaw_plugins")),
                                        plugin_class=NintbotPlugin)
            self._logger.debug("Jigsaw initialized.")

            self._logger.debug("Loading Jigsaw manifests...")
            self._jigsaw.load_manifests()
            self._logger.debug("Jigsaw manifests loaded.")

            with open(os.path.join(folder, "plugins.json")) as f:
                self._plugin_state = json.load(f)

            self._logger.debug("Loading Jigsaw plugins...")
            for plugin in self._plugin_state:
                if self._plugin_state[plugin]:
                    self._jigsaw.load_plugin(self._jigsaw.get_manifest(plugin), self.bot)
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

            self.bot.CommandRegistry.register_command("loadplugin",
                                                      "Loads the specified modern plugin.",
                                                      Owner(self.bot),
                                                      plugin_data,
                                                      self.command_loadplugin)

            self.bot.CommandRegistry.register_command("reloadmanifests",
                                                      "Reloads all plugin manifests.",
                                                      Owner(self.bot),
                                                      plugin_data,
                                                      self.command_reloadmanifests)

            self.bot.CommandRegistry.register_command("unloadplugin",
                                                      "Unloads the specified modern plugin.",
                                                      Owner(self.bot),
                                                      plugin_data,
                                                      self.command_unloadplugin)

        except:
            traceback.print_exc(5)

    def _save_plugin_state(self):
        with open(os.path.join(self.folder, "plugins.json"), "w") as f:
            json.dump(self._plugin_state, f)

    async def command_jigsawplugins(self, args):
        message = "```\n"

        # noinspection PyProtectedMember
        for plugin in self._jigsaw._manifests:
            message += f"{plugin['name']}\n"
            message += f"\tVersion: {plugin.get('version', '0.0.0')}\n"
            message += f"\tDeveloper: {plugin.get('developer', 'Unspecified Developer')}\n"
            message += f"\tDependencies: {', '.join(plugin.get('dependencies', []))}\n"
            message += f"\tLoaded: {self._jigsaw.get_plugin_loaded(plugin['name'])}\n"

        message += "```"

        await self.bot.send_message(args["channel"], message)

    async def command_reloadplugins(self, args):
        self._jigsaw.reload_all_plugins(self.bot)
        await self.bot.send_message(args["channel"], "Plugins reloaded")

    async def command_loadplugin(self, args):
        plugin_name = " ".join(args["command_args"][1:])
        if plugin_name in self._plugin_state:
            if self._plugin_state[plugin_name] and self._jigsaw.get_plugin_loaded(plugin_name):
                await self.bot.send_message(args["channel"], "Plugin already loaded.")
            elif self._plugin_state[plugin_name] and not self._jigsaw.get_plugin_loaded(plugin_name):
                if self._jigsaw.get_manifest(plugin_name) is not None:
                    self._jigsaw.load_plugin(self._jigsaw.get_manifest(plugin_name), self.bot)
                    self._jigsaw.get_plugin(plugin_name).enable()
                    await self.bot.send_message(args["channel"], "Plugin loaded.")
                else:
                    await self.bot.send_message(
                        args["channel"],
                        "Plugin with that name not found. Maybe reload manifests and try again?"
                    )
            elif not self._plugin_state[plugin_name]:
                if self._jigsaw.get_manifest(plugin_name) is not None:
                    self._plugin_state[plugin_name] = True
                    self._save_plugin_state()
                    self._jigsaw.load_plugin(self._jigsaw.get_manifest(plugin_name), self.bot)
                    self._jigsaw.get_plugin(plugin_name).enable()
                    await self.bot.send_message(args["channel"], "Plugin loaded.")
                else:
                    await self.bot.send_message(
                        args["channel"],
                        "Plugin with that name not found. Maybe reload manifests and try again?"
                    )
        else:
            if self._jigsaw.get_manifest(plugin_name) is not None:
                self._plugin_state[plugin_name] = True
                self._save_plugin_state()
                self._jigsaw.load_plugin(self._jigsaw.get_manifest(plugin_name), self.bot)
                self._jigsaw.get_plugin(plugin_name).enable()
                await self.bot.send_message(args["channel"], "Plugin loaded.")
            else:
                await self.bot.send_message(args["channel"],
                                            "Plugin with that name not found. Maybe reload manifests and try again?")

    async def command_reloadmanifests(self, args: dict):
        self._jigsaw.reload_all_manifests()
        await self.bot.send_message(args["channel"], "Manifests reloaded.")

    async def command_unloadplugin(self, args: dict):
        plugin_name = " ".join(args["command_args"][1:])
        if plugin_name in self._plugin_state:
            if self._jigsaw.get_plugin_loaded(plugin_name):
                self._jigsaw.get_plugin(plugin_name).disable()
                self._jigsaw.unload_plugin(plugin_name)
                self._plugin_state[plugin_name] = False
                self._save_plugin_state()
                await self.bot.send_message(args["channel"], "Plugin unloaded.")
            else:
                await self.bot.send_message(args["channel"], "Plugin not loaded.")
        else:
            await self.bot.send_message(args["channel"], "Plugin not loaded.")
