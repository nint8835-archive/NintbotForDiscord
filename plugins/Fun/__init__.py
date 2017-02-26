import traceback
from operator import itemgetter
import aiohttp
import random
import praw
import requests
import os
import json

from discord import Colour, Game

from NintbotForDiscord.Permissions import Permission, create_match_any_permission_group
from NintbotForDiscord.Permissions.General import ManageRoles
from NintbotForDiscord.Permissions.Special import Owner
from NintbotForDiscord.Plugin import BasePlugin

__author__ = 'Riley Flynn (nint8835)'


def get_index(list, key, value):
    for index, item in enumerate(list):
        if item[key] == value:
            return index
    return None


# noinspection PyBroadException
class Plugin(BasePlugin):

    def __init__(self, bot_instance, plugin_data, folder):
        super(Plugin, self).__init__(bot_instance, plugin_data, folder)
        # self.praw = praw.Reddit(user_agent = "Fun plugin V{} for NintbotForDiscord - Developed by /u/nint8835".format(self.plugin_data["plugin_version"]))
        # self.praw.get_random_subreddit(True)
        self.admin_perm = create_match_any_permission_group([ManageRoles(), Owner(self.bot)])
        self.bot.CommandRegistry.register_command("weather",
                                                  "Looks up the weather for a specified location on openweathermap.",
                                                  Permission(),
                                                  plugin_data,
                                                  self.command_weather)
        self.bot.CommandRegistry.register_command("8ball",
                                                  "Asks the bot's built-in magic 8ball a question.",
                                                  Permission(),
                                                  plugin_data,
                                                  self.command_8ball)
        self.bot.CommandRegistry.register_command("setavatar",
                                                  "Changes the bot's avatar.",
                                                  Owner(self.bot),
                                                  plugin_data,
                                                  self.command_setavatar)
        self.bot.CommandRegistry.register_command("avatar",
                                                  "Gets the URL for a user's avatar.",
                                                  Permission(),
                                                  plugin_data,
                                                  self.command_avatar)
        self.bot.CommandRegistry.register_command("decide",
                                                  "Makes the bot choose between two or more options, separated by pipes.",
                                                  Permission(),
                                                  plugin_data,
                                                  self.command_decide)
        self.bot.CommandRegistry.register_command("role_color",
                                                  "Sets the color for a role to a hex color value.",
                                                  self.admin_perm,
                                                  plugin_data,
                                                  self.command_role_color)
        self.bot.CommandRegistry.register_command("name",
                                                  "Changes the bot's username.",
                                                  Owner(self.bot),
                                                  plugin_data,
                                                  self.command_name)
        self.bot.CommandRegistry.register_command("setgame",
                                                  "Sets the game the bot is displayed as playing.",
                                                  Owner(self.bot),
                                                  plugin_data,
                                                  self.command_setgame)
        self.bot.CommandRegistry.register_command("topgames",
                                                  "Displays the games that are currently being played by the most users.",
                                                  Permission(),
                                                  plugin_data,
                                                  self.command_topgames)
        # self.bot.CommandRegistry.register_command("reddit",
        #                                           "Posts a random link from a subreddit.",
        #                                           Permission(),
        #                                           plugin_data,
        #                                           self.command_reddit)

        with open(os.path.join(folder, "config.json")) as f:
            self.config = json.load(f)

    async def command_weather(self, args):
        if len(args["command_args"]) >= 2:
            location = " ".join(args["command_args"][1:]).replace(" ", "%20")
            with aiohttp.ClientSession() as session:
                async with session.get("http://api.openweathermap.org/data/2.5/weather?q=\"{}\"&units=metric&APPID={}".format(location, self.config["openweathermap_appid"])) as resp:
                    weather_text = await resp.text()
                    weather = json.loads(weather_text)
                    await self.bot.send_message(args["channel"], "It is currently {} degrees Celsius with {} in {}.".format(weather["main"]["temp"],
                                                                                                                            weather["weather"][0]["main"].lower(),
                                                                                                                            weather["name"]))

    async def command_8ball(self, args):
        try:
            await self.bot.send_message(args["channel"], random.choice(self.config["8ball_messages"]))
        except:
            self.bot.send_message(args["channel"], traceback.format_exc(2))

    async def command_setavatar(self, args):
        if len(args["command_args"]) == 2:
            try:
                data = requests.get(args["command_args"][1], stream=True)
                await self.bot.edit_profile(self.bot.config["password"], avatar = data.raw.data)
            except:
                traceback.print_exc(5)

    async def command_avatar(self, args):
        if len(args["command_args"]) >= 2:
            try:
                username = " ".join(args["command_args"][1:])
                user = [i for i in args["channel"].server.members if i.name == username][0]
                await self.bot.send_message(args["channel"], "The avatar URL for {} is {}".format(username, user.avatar_url))
            except:
                traceback.print_exc(5)

        else:
            await self.bot.send_message(args["channel"], "My avatar URL is {}".format(self.bot.user.avatar_url))

    async def command_decide(self, args):
        if len(args["command_args"]) >= 2:
            options = " ".join(args["command_args"][1:]).split("|")
            await self.bot.send_message(args["channel"], random.choice(options))

    async def command_role_color(self, args):
        if len(args["command_args"]) >= 3:
            try:
                role_name = " ".join(args["command_args"][1:-1])
                color = args["command_args"][-1]
                roles_matching = [role for role in args["message"].server.roles if role.name == role_name]
                await self.bot.edit_role(args["message"].server, roles_matching[0], colour = Colour(int(color, 16)))

            except:
                traceback.print_exc(5)

    async def command_name(self, args):
        if len(args["command_args"]) >= 2:
            try:
                new_name = " ".join(args["command_args"][1:])
                await self.bot.edit_profile(self.bot.config["password"], username = new_name)
            except:
                traceback.print_exc(5)

    async def command_setgame(self, args):
        if len(args["command_args"]) >= 2:
            game = " ".join(args["command_args"][1:])
            await self.bot.change_status(game = Game(name = game))

    async def command_topgames(self, args):
        games = []
        for user in self.bot.PluginManager.get_plugin_instance_by_name("Nintbot Core").get_all_users():
            try:
                if user.game is not None:
                    if not any([i["game"] == user.game.name for i in games]):
                        games.append({"game": user.game.name, "count": 1})
                    else:
                        games[get_index(games, "game", user.game.name)]["count"] += 1
            except:
                traceback.print_exc(5)
        sorted_games = sorted(games, key=itemgetter("count"), reverse=True)
        await self.bot.send_message(args["channel"], "```Top games:\n{}```".format("\n".join(["{} - {} users".format(i["game"], i["count"]) for i in sorted_games])))

    # async def command_reddit(self, args):
    #     if len(args["command_args"]) == 2:
    #         try:
    #             submission = self.praw.get_random_submission(args["command_args"][1])
    #             if (submission.over_18 and args["channel"].id in self.config["nsfw_channels"]) or not submission.over_18:
    #                 if not submission.is_self:
    #                     await self.bot.send_message(args["channel"], "{}\n{}".format(submission.title, submission.url.replace(".gifv", ".gif")))
    #                 else:
    #                     await self.bot.send_message(args["channel"], "{}\n{}".format(submission.title, submission.selftext))
    #             else:
    #                 await self.bot.send_message(args["channel"], ":no_entry_sign: This is not a NSFW channel. NSFW content is not available here.")
    #         except:
    #             traceback.print_exc(5)
