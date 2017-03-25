import traceback

from NintbotForDiscord.Plugin import BasePlugin
from NintbotForDiscord.Permissions import Permission
import os
import json
import requests
__author__ = 'Riley Flynn (nint8835)'

INFO_STRING = """```Osu stats for user {}
PP rank: {}
Country: {}
Country PP rank: {}
Total score: {}
Accuracy: {}
Amount by rank:
    SS: {}
    S: {}
    A: {}
```"""


class Plugin(BasePlugin):

    def __init__(self, manifest, bot_instance):
        super(Plugin, self).__init__(manifest, bot_instance)
        self.bot.CommandRegistry.register_command("osu",
                                                  "Gets the Osu stats for a user.",
                                                  Permission(),
                                                  self,
                                                  self.on_command)
        with open(os.path.join(self.manifest["path"], "config.json")) as f:
            self.config = json.load(f)

    async def on_command(self, args):
        if len(args["command_args"]) >= 2:
            username = " ".join(args["command_args"][1:])
            user_data = requests.get("https://osu.ppy.sh/api/get_user",
                                     params = {"k": self.config["api_key"],
                                               "u": username,
                                               "type": "string"})
            print(user_data.text)
            # noinspection PyBroadException
            try:
                user_data_json = json.loads(user_data.text)[0]
                print(user_data_json)
                await self.bot.send_message(args["channel"],
                                            INFO_STRING.format(user_data_json["username"],
                                                               user_data_json["pp_rank"],
                                                               user_data_json["country"],
                                                               user_data_json["pp_country_rank"],
                                                               user_data_json["total_score"],
                                                               user_data_json["accuracy"],
                                                               user_data_json["count_rank_ss"],
                                                               user_data_json["count_rank_s"],
                                                               user_data_json["count_rank_a"]))
            except:
                traceback.print_exc(5)
