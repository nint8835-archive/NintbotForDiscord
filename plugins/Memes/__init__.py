from NintbotForDiscord.Enums import EventTypes
from NintbotForDiscord.Plugin import BasePlugin
from NintbotForDiscord.Permissions import Permission

import praw

__author__ = 'Riley Flynn (nint8835)'


subreddits = ["memes",
              "dankmemes",
              "funnymeme",
              "meme",
              "terriblefacebookmemes",
              "emojipasta"]


class Plugin(BasePlugin):

    def __init__(self, bot_instance, plugin_data, folder):
        super(Plugin, self).__init__(bot_instance, plugin_data, folder)
        self.praw = praw.Reddit(user_agent = "Memes plugin V{} for NintbotForDiscord. Developed by /u/nint8835".format(plugin_data["plugin_version"]))
        self.bot.CommandRegistry.register_command("meme",
                                                  "Posts an amazing meme.",
                                                  Permission(),
                                                  plugin_data)
        self.bot.register_handler(EventTypes.CommandSent, self.on_command, self)

    async def on_command(self, args):
        if args["command_args"][0] == "meme":
            submission = self.praw.get_random_submission("+".join(subreddits))
            if not submission.is_self:
                await self.bot.send_message(args["channel"], submission.url)
            else:
                await self.bot.send_message(args["channel"], "{}\n{}".format(submission.title, submission.selftext))
