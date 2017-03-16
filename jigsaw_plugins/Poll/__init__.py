import random
import string
from operator import itemgetter

import emoji
from discord import Colour
from discord import Embed
from discord import Object

from NintbotForDiscord.Permissions import Permission

from plugins.JigsawLoader import NintbotPlugin





class Poll(NintbotPlugin):

    def __init__(self, manifest, bot_instance):
        super(Poll, self).__init__(manifest, bot_instance)

        self._polls = []

        self.register_command("startpoll", "Starts a poll.", self.command_startpoll, Permission())
        self.register_command("closepoll", "Closes a poll.", self.command_closepoll, Permission())

    def enable(self) -> None:
        self.logger.info(f"Enabling Poll v{self.manifest['version']}")
        super(Poll, self).enable()

    def disable(self) -> None:
        self.logger.info(f"Disabling Poll v{self.manifest['version']}")
        super(Poll, self).disable()

    async def command_startpoll(self, args: dict):
        for poll in self._polls:
            if poll["author"] == args["author"].id:
                await self.bot.send_message(args["channel"],
                                            "You already have a poll. Please close it before making a new one.")
                return

        if len(args["command_args"]) < 4:
            await self.bot.send_message(args["channel"],
                                        "You have not specified enough options for your poll.")
            return

        question = args["command_args"][1]
        options = args["command_args"][2:]

        for option in options:
            if option not in emoji.UNICODE_EMOJI and not (option.startswith("<") and option.endswith(">")):
                await self.bot.send_message(args["channel"],
                                            "One or more of your options specified was not an emoji.")
                return

        embed = Embed()
        embed.add_field(name="Question", value=question)
        embed.add_field(name="Created by", value=(args["author"].nick or args["author"].name))
        colour = "".join([random.choice(string.hexdigits) for i in range(6)])
        embed.colour = Colour(int(colour, 16))

        message = await self.bot.send_message(args["channel"], embed=embed)

        self._polls.append({
            "author": args["author"].id,
            "channel": args["channel"].id,
            "message": message.id,
            "question": question,
            "options": options
        })

        for option in options[:]:
            for emote in self.bot.get_all_emojis():
                if str(emote) == option:
                    options.remove(option)
                    options.append(emote)

        for option in options:
            await self.bot.add_reaction(message, option)

    async def command_closepoll(self, args: dict):
        userpoll = None
        for poll in self._polls:
            if poll["author"] == args["author"].id:
                userpoll = poll

        if userpoll is None:
            await self.bot.send_message(args["channel"], "You do not have a poll. Please open one first.")
            return

        pollmessage = None

        async for message in self.bot.logs_from(Object(userpoll["channel"])):
            if message.id == userpoll["message"]:
                pollmessage = message

        if pollmessage is None:
            await self.bot.send_message(args["channel"], "The message containing the poll could not be found.")
            self._polls.remove(userpoll)
            return

        counts = []
        total = 0
        for reaction in pollmessage.reactions:
            if reaction.emoji not in userpoll["options"]:
                pass
            else:
                counts.append({"emote": reaction.emoji, "count": reaction.count - 1})
                total += (reaction.count - 1)

        sorted_counts = sorted(counts, key=itemgetter("count"), reverse=True)

        resultsmessage = f"Response rankings for \"{userpoll['question']}\"\n"

        for index, option in enumerate(sorted_counts):
            resultsmessage += f"{index + 1}: {option['emote']} - {option['count']}({(option['count']/total) * 100}%)\n"

        await self.bot.send_message(args["channel"], resultsmessage)

        self._polls.remove(userpoll)
