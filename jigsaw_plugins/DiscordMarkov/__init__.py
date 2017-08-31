import asyncio
import datetime
import os
import traceback

import markovify

from NintbotForDiscord.Enums import EventTypes
from NintbotForDiscord.Events import MessageSentEvent
from NintbotForDiscord.Plugin import BasePlugin


class DiscordMarkov(BasePlugin):
    def __init__(self, manifest, bot_instance):
        super().__init__(manifest, bot_instance)
        self.enabled = True
        self.strings = []
        self.string_path = os.path.abspath(os.path.join(self.manifest["path"], "strings"))

        self.register_command("wisdom",
                              "Generates wisdom using the new and improved markov chains.",
                              self.command_new_wisdom)

        self.register_handler(EventTypes.MESSAGE_SENT, self.on_message)

    def load_strings(self):
        self.logger.debug("Loading strings...")
        for file in os.listdir(self.string_path):
            if file.endswith(".txt"):
                filename = os.path.join(self.string_path, file)
                self.logger.debug(f"Loading strings from {filename}...")
                with open(filename, "r", encoding="utf8") as f:
                    lines = [i.replace("\r", "") for i in f.readlines()]
                    self.strings += lines
                    self.logger.debug(f"Loaded {len(lines)} strings from {filename}.")
        self.logger.debug("Strings loaded.")

    async def regen_chain_task(self):
        while not self.bot.is_closed() and self.enabled:
            self.logger.debug("Regenerating chain.")
            await self.async_make_chain()
            self.logger.debug("Chain regenerated.")
            await asyncio.sleep(60)

    async def async_make_chain(self):
        generate_chain_task = self.bot.EventManager.loop.run_in_executor(None, self.make_chain)
        await generate_chain_task

    # noinspection PyAttributeOutsideInit
    def make_chain(self):
        self.chain = markovify.NewlineText("\n".join(self.strings))

    def enable(self):
        self.logger.info(f"Enabling DiscordMarkov v{self.manifest['version']}")
        super(DiscordMarkov, self).enable()

        if not os.path.isdir(self.string_path):
            self.logger.debug("Strings directory does not exist, creating now.")
            os.mkdir(self.string_path)
        self.load_strings()

        self.logger.debug("Starting auto-regeneration task...")
        self.bot.EventManager.loop.create_task(self.regen_chain_task())
        self.logger.debug("Task started.")

        self.enabled = True

        self.logger.info(f"Finished enabling DiscordMarkov v{self.manifest['version']}")

    def disable(self):
        super(DiscordMarkov, self).disable()
        self.logger.info(f"Disabling DiscordMarkov v{self.manifest['version']}")

        self.logger.debug("Clearing strings list...")
        self.strings = []
        self.logger.debug("Strings list cleared.")

        self.enabled = False

        self.logger.info(f"Finished disabling DiscordMarkov v{self.manifest['version']}")

    def generate_message(self, start: str = ""):
        message = ""
        count = 0
        # noinspection PyBroadException
        try:
            while message == "" and count < 15:
                if start != "":
                    message = self.chain.make_sentence_with_start(start)
                    count += 1
                else:
                    message = self.chain.make_sentence()
                    count += 1
        except:
            traceback.print_exc(3)
            message = "I don't know how to respond."
        if message == "" or message is None:
            message = "I don't know how to respond."
        return message

    async def on_message(self, args: MessageSentEvent):
        self.strings.append(args["message"].content)

        date = datetime.datetime.today()
        filename = os.path.join(self.string_path, f"{date:%m-%d-%Y}.txt")
        if os.path.exists(filename):
            write_mode = "a"
        else:
            write_mode = "w"

        with open(filename, write_mode, encoding="utf8") as f:
            f.write(f"{args.content}\n")

    async def command_new_wisdom(self, args):
        if len(args["command_args"]) == 1:
            await args.channel.send(self.generate_message())
        else:
            await args.channel.send(self.generate_message(" ".join(args["command_args"][1:])))
