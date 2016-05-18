import json
import os
import traceback

from discord.opus import load_opus
from discord.utils import find

from NintbotForDiscord.Permissions import Permission
from NintbotForDiscord.Permissions.Special import Owner
from NintbotForDiscord.Plugin import BasePlugin

__author__ = 'Riley Flynn (nint8835)'


class Plugin(BasePlugin):

    def __init__(self, bot_instance, plugin_data, folder):
        super(Plugin, self).__init__(bot_instance, plugin_data, folder)
        self.voice = None
        with open(os.path.join(folder, "files.json")) as f:
            self.files = json.load(f)

        load_opus(os.path.join(folder, "libopus"))

        for file in self.files:
            self.bot.CommandRegistry.register_command(self.files[file]["command"],
                                                      self.files[file]["description"],
                                                      Permission(),
                                                      plugin_data,
                                                      self.command_soundboard)

        self.bot.CommandRegistry.register_command("reload_soundboard",
                                                  "Reloads the soundboard file list",
                                                  Owner(self.bot),
                                                  plugin_data,
                                                  self.command_reload_soundboard)

    async def command_soundboard(self, args):
        try:
            file_key = find(lambda f: self.files[f]["command"] == args["command_args"][0], self.files)
            if self.voice is None:
                try:
                    if self.bot.is_voice_connected(args["channel"].server):
                        self.voice = self.bot.voice_client_in(args["channel"].server)
                    elif args["author"].voice_channel is not None:
                        self.voice = await self.bot.join_voice_channel(args["author"].voice_channel)
                        player = self.voice.create_ffmpeg_player(os.path.join(self.folder, "files", file_key))
                        player.start()
                except:
                    if args["author"].voice_channel is not None:
                        self.voice = await self.bot.join_voice_channel(args["author"].voice_channel)
                        player = self.voice.create_ffmpeg_player(os.path.join(self.folder, "files", file_key))
                        player.start()
            else:
                player = self.voice.create_ffmpeg_player(os.path.join(self.folder, "files", file_key))
                player.start()

        except:
            traceback.print_exc(5)

    async def command_reload_soundboard(self, args):
        self.files = {}
        self.bot.CommandRegistry.unregister_all_commands_for_plugin(self.plugin_data)
        with open(os.path.join(self.folder, "files.json")) as f:
            self.files = json.load(f)
        for file in self.files:
            self.bot.CommandRegistry.register_command(self.files[file]["command"],
                                                      self.files[file]["description"],
                                                      Permission(),
                                                      self.plugin_data,
                                                      self.command_soundboard)

