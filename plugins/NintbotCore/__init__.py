from NintbotForDiscord.Enums import EventTypes
from NintbotForDiscord.Plugin import BasePlugin
from NintbotForDiscord.Permissions import create_match_any_permission_group, Permission
from NintbotForDiscord.Permissions.Special import Owner
from NintbotForDiscord.Permissions.Text import ManageMessages

from discord import ChannelType, Status, Game

import traceback
import math
import os
import json
import re
import time

__author__ = 'Riley Flynn (nint8835)'

INFO_STRING = """```Nintbot version {}
Developed by nint8835
Currently connected to {} servers, with {} channels ({} text, {} voice) and {} users ({} of which are online).
{} plugins currently installed.```"""

USER_INFO_STRING = """```Username: {}
ID: {}
Discriminator: {}
Avatar: {}
Created: {}
```"""


class Plugin(BasePlugin):
    def __init__(self, bot_instance, plugin_data, folder):
        super(Plugin, self).__init__(bot_instance, plugin_data, folder)
        self.started_time = 0
        self.admin = create_match_any_permission_group([Owner(self.bot), ManageMessages()])
        self.bot.register_handler(EventTypes.OnReady, self.on_ready, self)

        self.bot.CommandRegistry.register_command("info",
                                                  "Gets general information about the bot.",
                                                  Permission(),
                                                  plugin_data,
                                                  self.command_info)
        self.bot.CommandRegistry.register_command("debug",
                                                  "Runs Python code to test features.",
                                                  Owner(self.bot),
                                                  plugin_data,
                                                  self.command_debug)
        self.bot.CommandRegistry.register_command("purge",
                                                  "Purges all messages for a user.",
                                                  self.admin,
                                                  plugin_data,
                                                  self.command_purge)
        self.bot.CommandRegistry.register_command("private_messages",
                                                  "Checks the private messages the bot has received.",
                                                  self.admin,
                                                  plugin_data,
                                                  self.command_private_messages)
        self.bot.CommandRegistry.register_command("plugins",
                                                  "Views the currently installed plugins.",
                                                  Permission(),
                                                  plugin_data,
                                                  self.command_plugins)
        self.bot.CommandRegistry.register_command("purgebot",
                                                  "Deletes all of the bot's messages from the channel.",
                                                  self.admin,
                                                  plugin_data,
                                                  self.command_purgebot)
        self.bot.CommandRegistry.register_command("regexpurge",
                                                  "Deletes messages filtered using a regular expression.",
                                                  self.admin,
                                                  plugin_data,
                                                  self.command_regexpurge)
        self.bot.CommandRegistry.register_command("stop",
                                                  "Stops the bot.",
                                                  Owner(self.bot),
                                                  plugin_data,
                                                  self.command_stop)
        self.bot.CommandRegistry.register_command("uptime",
                                                  "Displays the bot's uptime.",
                                                  Permission(),
                                                  plugin_data,
                                                  self.command_uptime)
        self.bot.CommandRegistry.register_command("commands",
                                                  "Displays what commands you have access to.",
                                                  Permission(),
                                                  plugin_data,
                                                  self.command_commands)
        self.bot.CommandRegistry.register_command("userinfo",
                                                  "Displays info about a certain user.",
                                                  Permission(),
                                                  plugin_data,
                                                  self.command_userinfo)
        self.bot.CommandRegistry.register_command("invitebot",
                                                  "Posts the invite link for the bot.",
                                                  Permission(),
                                                  plugin_data,
                                                  self.command_invitelink)

        with open(os.path.join(folder, "config.json")) as f:
            self.config = json.load(f)

    def member_is_admin(self, member):
        try:
            for role in member.roles:
                if role.permissions.manage_messages:
                    return True
        except:
            pass
        if member.id == self.config["owner_id"]:
            return True

        return False

    def get_all_channels(self):
        channels = []
        for server in [i for i in self.bot.servers if i.id not in self.bot.config["blacklisted_servers"]]:
            channels += server.channels
        return channels

    def get_all_text_channels(self):
        channels = []
        for server in [i for i in self.bot.servers if i.id not in self.bot.config["blacklisted_servers"]]:
            channels += [channel for channel in server.channels if channel.type == ChannelType.text]
        return channels

    def get_all_voice_channels(self):
        channels = []
        for server in [i for i in self.bot.servers if i.id not in self.bot.config["blacklisted_servers"]]:
            channels += [channel for channel in server.channels if channel.type == ChannelType.voice]
        return channels

    def get_all_users(self):
        users = []
        for server in [i for i in self.bot.servers if i.id not in self.bot.config["blacklisted_servers"]]:
            for user in server.members:
                if not any([user.id == i.id for i in users]):
                    users.append(user)
        return users

    def get_all_online_users(self):
        users = []
        for user in self.get_all_users():
            if user.status == Status.online or user.status == Status.idle:
                users.append(user)
        return users

    def get_all_roles(self):
        roles = []
        for server in [i for i in self.bot.servers if i.id not in self.bot.config["blacklisted_servers"]]:
            for role in server.roles:
                roles.append(role)
        return roles

    async def command_info(self, args):
        await self.bot.send_message(args["channel"],
                                    INFO_STRING.format(self.bot.VERSION,
                                                       len([i for i in self.bot.servers if i.id not in self.bot.config["blacklisted_servers"]]),
                                                       len(self.get_all_channels()),
                                                       len(self.get_all_text_channels()),
                                                       len(self.get_all_voice_channels()),
                                                       len(self.get_all_users()),
                                                       len(self.get_all_online_users()),
                                                       len(self.bot.PluginManager.plugins)))

    async def command_debug(self, args):
        if self.config["enable_debug"] and Owner(self.bot).has_permission(args["author"]):
            try:
                results = eval(" ".join(args["unsplit_args"].split(" ")[1:]))
            except:
                results = traceback.format_exc(5)
            await self.bot.send_message(args["channel"], "```python\n{}```".format(results))

    async def command_purge(self, args):
        if len(args["command_args"]) == 2:
            args["command_args"][2] = 100
        if self.admin.has_permission(args["author"]):
            async for message in self.bot.logs_from(args["channel"], limit = int(args["command_args"][2])):
                if message.author.name == args["command_args"][1]:
                    await self.bot.delete_message(message)
                elif args["command_args"][1] == "ALL":
                    await self.bot.delete_message(message)

    async def command_regexpurge(self, args):
        if len(args["command_args"]) == 2:
            args["command_args"][2] = 100
        if self.admin.has_permission(args["author"]):
            regex = re.compile(args["command_args"][1])
            async for message in self.bot.logs_from(args["channel"], limit = int(args["command_args"][2])):
                if regex.match(message.content):
                    await self.bot.delete_message(message)

    async def command_private_messages(self, args):
        if len(args["command_args"]) == 1:
            message = "```The bot has private messages to or from the following users:\n{}```".format(
                "\n".join([channel.user.name for channel in self.bot.private_channels]))
            await self.bot.send_message(args["channel"], message)
        if len(args["command_args"]) > 1:
            user_name = " ".join(args["command_args"][1:])
            try:
                logs = []
                async for i in self.bot.logs_from([channel for channel in self.bot.private_channels if channel.user.name == user_name][0],limit = 5):
                    logs.append(i)
                await self.bot.send_message(args["channel"],
                                            "```Last 5 private messages with {}\n{}```".format(user_name, "\n".join(
                                                    ["{}: {}".format(log.author.name, log.content) for log in logs])))
            except:
                traceback.print_exc(5)

    async def command_plugins(self, args):
        # HORRIBLE CODE ALERT
        # I'll clean it up later - Riley Flynn, ALWAYS
        # It never gets done
        await self.bot.send_message(args["channel"],
                                    "```Installed plugins:\n{}```".format("\n".join(["{} version {} by {}".format(
                                            plugin["info"]["plugin_name"], plugin["info"]["plugin_version"],
                                            plugin["info"]["plugin_developer"]) for plugin in
                                                                                     self.bot.PluginManager.plugins])))

    async def command_purgebot(self, args):
        async for message in self.bot.logs_from(args["channel"], limit = 100):
            if message.author.id == self.bot.user.id:
                await self.bot.delete_message(message)

    async def command_uptime(self, args):
        time_diff = time.time() - self.started_time
        minutes, seconds = divmod(time_diff, 60)
        minutes = int(math.floor(minutes))
        seconds = int(math.floor(seconds))
        hours, minutes = divmod(minutes, 60)
        hours = int(math.floor(hours))
        minutes = int(math.floor(minutes))
        days, hours = divmod(hours, 24)
        hours = int(math.floor(hours))
        days = int(math.floor(days))
        await self.bot.send_message(args["channel"], "The bot has been up for {} days, {} hours, {} minutes, and {} seconds.".format(days, hours, minutes, seconds))

    async def command_commands(self, args):
        message_str = ""
        for command in self.bot.CommandRegistry.get_available_commands_for_user(args["author"]):
            if message_str == "":
                message_str += "```"
            if len(message_str)>=1700:
                await self.bot.send_message(args["author"], message_str + "```")
                message_str = "```"
            message_str += "{}{}: {}\n".format(self.bot.config["command_prefix"], command["command"], command["description"])
        if message_str != "":
            await self.bot.send_message(args["author"], message_str + "```")

    async def command_userinfo(self, args):
        if len(args["command_args"]) >= 2:
            users = [user for user in args["channel"].server.members if user.name == " ".join(args["command_args"][1:])]
            for user in users:
                await self.bot.send_message(args["channel"], USER_INFO_STRING.format(user.name,
                                                                                     user.id,
                                                                                     user.discriminator,
                                                                                     user.avatar_url,
                                                                                     user.created_at))

    async def command_stop(self, args):
        await self.bot.logout()

    async def command_invitelink(self, args):
        await self.bot.send_message(args["channel"], "Invite the bot to your server using the following link: https://discordapp.com/oauth2/authorize?&client_id={}&scope=bot".format(self.bot.config["app_id"]))

    async def on_ready(self, args):
        await self.bot.change_status(game = Game(name = "Nintbot V{}".format(self.bot.VERSION)))
        self.started_time = time.time()
