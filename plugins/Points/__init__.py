import json
import os
from typing import Union
import asyncio
import math

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

    def add_point_percentage(self, user, percentage):
        points = self.get_points(user)
        add = math.ceil(points * percentage)
        if add == 0:
            self.add_points(user, 1)
        else:
            self.add_points(user, add)

    async def distribute_points_task(self):
        while not self.bot.is_closed and self.enabled:
            self.logger.debug("Distributing points...")
            for server in self.bot.servers:
                for member in server.members:
                    if member.status != discord.Status.offline:
                        if server.owner == member:
                            self.add_point_percentage(member, 0.05)
                        else:
                            self.add_point_percentage(member, 0.01)
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
