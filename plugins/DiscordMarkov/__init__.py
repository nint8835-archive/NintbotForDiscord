import traceback
import pymarkovchain
import os
import json
import logging
import asyncio
import requests

from NintbotForDiscord.Enums import EventTypes
from NintbotForDiscord.Plugin import BasePlugin
from NintbotForDiscord.Permissions import Permission, create_match_any_permission_group
from NintbotForDiscord.Permissions.Text import ManageMessages
from NintbotForDiscord.Permissions.Special import Owner

__author__ = 'Riley Flynn (nint8835)'


# noinspection PyBroadException
class Plugin(BasePlugin):

    def __init__(self, bot_instance, plugin_data, folder):
        super(Plugin, self).__init__(bot_instance, plugin_data, folder)
        self.cleanstrings_permission_group = create_match_any_permission_group([ManageMessages(), Owner(self.bot)])
        logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(logging.ERROR)
        self.bot.register_handler(EventTypes.MESSAGE_SENT, self.on_message, self)
        self.bot.CommandRegistry.register_command("wisdom",
                                                  "Generates wisdom using markov chains.",
                                                  Permission(),
                                                  plugin_data,
                                                  self.command_wisdom)
        self.bot.CommandRegistry.register_command("cleanstrings",
                                                  "Cleans extra data from the strings used to generate data.",
                                                  self.cleanstrings_permission_group,
                                                  plugin_data,
                                                  self.command_cleanstrings)
        self.bot.CommandRegistry.register_command("web_learn",
                                                  "Learns messages from a plain text file hosted online.",
                                                  Owner(self.bot),
                                                  plugin_data,
                                                  self.command_web_learn)
        self.bot.CommandRegistry.register_command("messages",
                                                  "Gives the number of messages the bot has to base it's knowledge off of.",
                                                  Permission(),
                                                  plugin_data,
                                                  self.command_messages)
        self.strings = []
        self.load_strings()
        self.chain = pymarkovchain.MarkovChain()
        self.bot.EventManager.loop.create_task(self.regen_db())

    async def regen_db(self):
        while not self.bot.is_closed:
            generate_db_task = self.bot.EventManager.loop.run_in_executor(None, self.chain.generateDatabase, "\n".join(self.strings))
            await generate_db_task
            await asyncio.sleep(60)

    def save_strings(self):
        with open(os.path.join(self.folder, "strings.json"), "w") as f:
            json.dump(self.strings, f)

    def load_strings(self):
        with open(os.path.join(self.folder, "strings.json")) as f:
            self.strings = json.load(f)

    async def on_message(self, args):
        self.strings.append(args["message"].content)
        self.save_strings()

    async def command_wisdom(self, args):
        if len(args["command_args"]) == 1:
            await self.bot.send_typing(args["channel"])
            try:
                message_string_task = self.bot.EventManager.loop.run_in_executor(None, self.chain.generateString)
                message_string = await message_string_task
                try:
                    if message_string.count("\"") % 2 != 0 and message_string.count("\"") > 0:
                        message_string += "\""
                except ZeroDivisionError:
                    pass

                if message_string.count("(") - message_string.count(")") >0:
                    message_string += ")"

                if message_string.count(")") - message_string.count("(") >0:
                    message_string = "(" + message_string

                message_string = message_string.capitalize()
                await self.bot.send_message(args["channel"], message_string)
            except:
                await self.bot.send_message(args["channel"], "```{}```".format(traceback.format_exc(2)))
        elif len(args["command_args"]) >= 2:
            await self.bot.send_typing(args["channel"])
            try:
                message_string = ""
                count = 0
                while len(message_string.split(" "))<=5 and count < 10:
                    message_string_task = self.bot.EventManager.loop.run_in_executor(None, self.chain.generateStringWithSeed, " ".join(args["command_args"][1:]))
                    message_string = await message_string_task
                    count += 1
                try:
                    if message_string.count("\"") % 2 != 0 and message_string.count("\"") > 0:
                        message_string += "\""
                except ZeroDivisionError:
                    pass

                if message_string.count("(") - message_string.count(")") >0:
                    message_string += ")"

                if message_string.count(")") - message_string.count("(") >0:
                    message_string = "(" + message_string

                await self.bot.send_message(args["channel"], message_string)
            except pymarkovchain.StringContinuationImpossibleError:
                await self.bot.send_message(args["channel"], "I don't know how to respond to that.")
            except:
                await self.bot.send_message(args["channel"], "```{}```".format(traceback.format_exc(2)))

    async def command_cleanstrings(self, args):
        count = 0
        for item in self.strings[:]:
            if item == "" or item.startswith("http") or item.startswith(self.bot.config["command_prefix"]) or item.count("its ok to accept urself nintbot") >= 1 or item.count("Nathanial is the") >= 1:
                count += 1
                self.strings.remove(item)

        self.save_strings()
        await self.bot.send_message(args["channel"], "Removed {} extra strings.".format(count))

    async def command_web_learn(self, args):
        if len(args["command_args"])==2:
            data = requests.get(args["command_args"][1]).text
            self.strings.append(data)
            self.save_strings()

    async def command_messages(self, args):
        await self.bot.send_message(args["channel"], "The bot knows {} messages.".format(len(self.strings)))
