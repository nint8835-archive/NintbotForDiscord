import json
import random
import traceback
import discord
import logging
import os

from NintbotForDiscord.Enums import EventTypes
from NintbotForDiscord.Plugin import BasePlugin
from NintbotForDiscord.Permissions import Permission

from libraries.JSONDB import JSONDatabase, SelectionMode
__author__ = 'Riley Flynn (nint8835)'


# noinspection PyGlobalUndefined
class Plugin(BasePlugin):

    def __init__(self, bot_instance, plugin_data, folder):
        super(Plugin, self).__init__(bot_instance, plugin_data, folder)
        self.bot.CommandRegistry.register_command("voice",
                                                  "Manage private voice channels.",
                                                  Permission(),
                                                  plugin_data,
                                                  self.on_command)
        self.logger = logging.getLogger("Private Channels")
        self.bot.register_handler(EventTypes.OnReady, self.on_ready, self)
        self.bot.register_handler(EventTypes.ChannelDeleted, self.on_channel_deleted, self)
        with open(os.path.join(folder, "config.json")) as f:
            self.config = json.load(f)
        with open(os.path.join(self.folder, "adjectives")) as f:
            self.adjectives = f.readlines()
        with open(os.path.join(self.folder, "animals")) as f:
            self.animals = f.readlines()
        self.channels = JSONDatabase(os.path.join(self.folder, "channels.json"))

    async def cleanup(self):
        self.logger.info("Running cleanup...")
        try:
            for channel in self.channels.select(SelectionMode.ALL).rows:
                if not any([s_chan.id == channel["id"] for s_chan in self.bot.get_all_channels()]):
                    server = [server for server in self.bot.servers if server.id == channel["server_id"]][0]
                    if any([role.id == channel["role_id"] for role in server.roles]):
                        self.logger.warning("Found orphaned role (respective channel was removed), removing role.")
                        try:
                            await self.bot.delete_role(server, [role for role in server.roles if role.id == channel["role_id"]][0])
                        except:
                            pass
                    self.logger.warning("A channel listed in the database is missing, removing it from the database.")
                    self.channels.select(SelectionMode.VALUE_EQUALS, "id", channel["id"]).remove()
        except:
            traceback.print_exc(5)

    def generate_name(self):
        return "-".join([random.choice(self.adjectives).capitalize(), random.choice(self.animals).capitalize()]).replace("\r", "").replace("\n", "")

    async def on_command(self, args):
        try:
            if not args["channel"].is_private:
                if args["command_args"][1] == "create":
                    if len(self.channels.select(SelectionMode.VALUE_EQUALS, "owner_id", args["author"].id)) != 0:
                        self.logger.info("{} tried to create a channel, but they already have one.".format(args["author"].name))
                        await self.bot.send_message(args["channel"], ":no_entry_sign: You already have a voice channel. Use the 'cleanup' option if you can't find it.")
                    else:
                        if len(self.channels.select(SelectionMode.VALUE_EQUALS, "server_id", args["message"].server)) >= self.config["max_channels"]:
                            await self.bot.send_message(args["channel"], ":no_entry_sign: This server has reached the channel limit. Wait for some users to abandon their channels, and then try again.")
                            self.logger.info("{} tried to create a channel, but the max channels has been reached.".format(args["author"].name))
                        else:
                            name = self.generate_name()
                            channel = await self.bot.create_channel(args["message"].server, name, "voice")
                            role = await self.bot.create_role(args["message"].server, name = name)
                            self.channels.insert({"id": channel.id,
                                                  "server_id": args["message"].server.id,
                                                  "role_id": role.id,
                                                  "owner_id": args["author"].id,
                                                  "name": name,
                                                  "admins": [args["author"].id]})

                            await self.bot.add_roles(args["author"], role)

                            allow = discord.Permissions.none()
                            deny = discord.Permissions.none()
                            deny.connect = True
                            await self.bot.edit_channel_permissions(channel, [role for role in args["channel"].server.roles if role.is_everyone][0], allow = allow, deny = deny)

                            allow = discord.Permissions.none()
                            allow.connect = True
                            allow.speak = True
                            allow.use_voice_activation = True
                            await self.bot.edit_channel_permissions(channel, role, allow = allow)

                            self.logger.info("{} created a new channel called {}.".format(args["author"].name, name))
                            await self.bot.send_message(args["channel"], ":ballot_box_with_check: {}, your channel has been created. It's name is {}. Use {}voice invite <username> to invite users.".format(args["author"].mention, name.replace(" ", "-"), self.bot.config["command_prefix"]))

                if args["command_args"][1] == "invite":
                    if not len(self.channels.select(SelectionMode.VALUE_EQUALS, "owner_id", args["author"].id)) != 0:
                            self.logger.info("{} tried to invite somebody to their channel, but they don't have one.".format(args["author"].name))
                            await self.bot.send_message(args["channel"], ":no_entry_sign: You don't have a voice channel. Use the create option to create one.")
                    else:
                        user = [user for user in args["channel"].server.members if user.name == " ".join(args["command_args"][2:])][0]
                        channel_data = self.channels.select(SelectionMode.VALUE_EQUALS, "owner_id", args["author"].id)[0]
                        role = [role for role in self.bot.PluginManager.get_plugin_instance_by_name("Nintbot Core").get_all_roles() if role.id == channel_data["role_id"]][0]
                        if args["message"].server.id == channel_data["server_id"]:
                            self.logger.info("{} invited {} to their channel.".format(args["author"].name, user.name))
                            await self.bot.add_roles(user, role)
                            await self.bot.send_message(args["channel"], ":ballot_box_with_check: {}, you were invited to {}'s voice channel, {}.".format(user.mention, args["author"].mention, channel_data["name"]))
                        else:
                            self.logger.info("{} attempted to invite a user to a channel from the wrong server.".format(args["author"].name))
                            await self.bot.send_message(args["channel"], ":no_entry_sign: Your channel is not in this server.")

                if args["command_args"][1] == "kick":
                    if not len(self.channels.select(SelectionMode.VALUE_EQUALS, "owner_id", args["author"].id)) != 0:
                            self.logger.info("{} tried to kick somebody from their channel, but they don't have one.".format(args["author"].name))
                            await self.bot.send_message(args["channel"], ":no_entry_sign: You don't have a voice channel. Use the create option to create one.")
                    else:
                        user = [user for user in args["channel"].server.members if user.name == " ".join(args["command_args"][2:])][0]
                        channel_data = self.channels.select(SelectionMode.VALUE_EQUALS, "owner_id", args["author"].id)[0]
                        role = [role for role in self.bot.PluginManager.get_plugin_instance_by_name("Nintbot Core").get_all_roles() if role.id == channel_data["role_id"]][0]
                        if args["message"].server.id == channel_data["server_id"]:
                            self.logger.info("{} kicked {} from their channel.".format(args["author"].name, user.name))
                            await self.bot.remove_roles(user, role)
                            await self.bot.send_message(args["channel"], ":ballot_box_with_check: {}, you were kicked from {}'s voice channel, {}.".format(user.mention, args["author"].mention, channel_data["name"]))
                        else:
                            self.logger.info("{} attempted to kick a user from a channel from the wrong server.".format(args["author"].name))
                            await self.bot.send_message(args["channel"], ":no_entry_sign: Your channel is not in this server.")

                if args["command_args"][1] == "cleanup":
                    await self.cleanup()
                    await self.bot.send_message(args["channel"], ":ballot_box_with_check: Removed missing channels from the database.")

                if args["command_args"][1] == "remove":
                    if not len(self.channels.select(SelectionMode.VALUE_EQUALS, "owner_id", args["author"].id)) != 0:
                            self.logger.info("{} tried to delete their channel, but they don't have one.".format(args["author"].name))
                            await self.bot.send_message(args["channel"], ":no_entry_sign: You don't have a voice channel. Use the create option to create one.")
                    else:
                        channel_data = self.channels.select(SelectionMode.VALUE_EQUALS, "owner_id", args["author"].id)[0]
                        role = [role for role in self.bot.PluginManager.get_plugin_instance_by_name("Nintbot Core").get_all_roles() if role.id == channel_data["role_id"]][0]
                        channel = [channel for channel in args["channel"].server.channels if channel.id == channel_data["id"]][0]
                        await self.bot.delete_channel(channel)
                        await self.bot.delete_role(args["channel"].server, role)
                        self.logger.info("{} deleted their channel.".format(args["author"].name))
                        await self.bot.send_message(args["channel"], ":ballot_box_with_check: You have deleted your channel and released a channel slot for other users.")

        except IndexError:
            pass

        except:
            traceback.print_exc(5)

    async def on_ready(self, args):
        await self.cleanup()

    async def on_channel_deleted(self, args):
        await self.cleanup()
