import json
import os
from typing import Union
import asyncio
import math
import random

from NintbotForDiscord.Plugin import BasePlugin
from NintbotForDiscord.Events import CommandSentEvent
from NintbotForDiscord.Permissions import Permission
import discord


class PointsPlugin(BasePlugin):

    def __init__(self, manifest, bot):
        super().__init__(manifest, bot)
        self.enabled = True

        if os.path.isfile(os.path.join(manifest["path"], "points.json")):
            with open(os.path.join(manifest["path"], "points.json")) as f:
                self.points = json.load(f)
        else:
            self.points = {}

        self.bot.CommandRegistry.register_modern_command(
            "^points$",
            "Gets the number of points you have",
            Permission(),
            self,
            self.command_points
        )

        self.bot.CommandRegistry.register_modern_command(
            "^gamble ([1-9]\d*)$",
            "Gambles your points.",
            Permission(),
            self,
            self.command_gamble
        )

    def _set_points(self, id: str, amount: int):
        self.points[id] = amount
        with open(os.path.join(self.manifest["path"], "points.json"), "w") as f:
            json.dump(self.points, f)

    def set_points(self, user: Union[discord.Member, discord.User], amount: int):
        self._set_points(user.id, amount)

    def _get_points(self, id: str) -> int:
        if id in self.points:
            return self.points[id]
        else:
            return 0

    def get_points(self, user: Union[discord.Member, discord.User]) -> int:
        return self._get_points(user.id)

    def add_points(self, user: Union[discord.Member, discord.User], amount: int):
        self.set_points(user, self.get_points(user) + amount)

    async def distribute_points_task(self):
        while not self.bot.is_closed and self.enabled:
            self.logger.debug("Distributing points...")
            for server in self.bot.servers:
                for member in server.members:
                    if member.status != discord.Status.offline:
                        if server.owner == member:
                            self.add_points(member, 2)
                        else:
                            self.add_points(member, 1)
            self.logger.debug("Points distributed.")
            await asyncio.sleep(60)

    def enable(self):
        super().enable()
        self.enabled = True
        self.bot.EventManager.loop.create_task(self.distribute_points_task())

    def disable(self):
        super().enable()
        self.enabled = False

    async def command_points(self, args: CommandSentEvent):
        await self.bot.send_message(args.channel, f"You have {self.get_points(args.author)} :potato:")

    async def command_gamble(self, args: CommandSentEvent):
        amount = int(args.args)
        self.logger.debug(amount)
        if self.get_points(args.author) >= amount:
            self.logger.debug(self.get_points(args.author))
            self.add_points(args.author, amount * -1)
            self.logger.debug(self.get_points(args.author))
            value = random.randint(0, 100)
            if value >= 97:
                self.add_points(args.author, amount * 50)
                await self.bot.send_message(args.channel, f"Jackpot! You won {amount * 50} points!")

            if value < 97 and value >= 70:
                multiplier = math.floor((100 - value) / float(4.0))
                self.add_points(args.author, amount * multiplier)
                await self.bot.send_message(args.channel, f"Not bad. You won {amount * multiplier} points.")

            if value >= 50 and value < 70:
                multiplier = 2
                self.add_points(args.author, amount * multiplier)
                await self.bot.send_message(args.channel, f"Not bad. You won {amount * multiplier} points.")

            if value < 50:
                await self.bot.send_message(args.channel, "Too bad! You lost your points.")
