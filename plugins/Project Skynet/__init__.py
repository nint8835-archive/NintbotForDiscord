import os
import json
import traceback

from NintbotForDiscord.Enums import EventTypes
from NintbotForDiscord.Permissions import Permission
from NintbotForDiscord.Permissions.Special import Owner
from NintbotForDiscord.Plugin import BasePlugin

__author__ = 'Riley Flynn (nint8835)'


class Plugin(BasePlugin):
    def __init__(self, bot_instance, plugin_data, folder):
        super(Plugin, self).__init__(bot_instance, plugin_data, folder)

        with open(os.path.join(folder, "learned_data.json")) as f:
            self.learned_data = json.load(f)

        self.bot.CommandRegistry.register_command("answer",
                                                  "Asks my A.I. a yes or no question.",
                                                  Permission(),
                                                  plugin_data)
        self.bot.CommandRegistry.register_command("train",
                                                  "Trains my data with a yes or no question",
                                                  Owner(self.bot),
                                                  plugin_data)

        self.bot.register_handler(EventTypes.CommandSent, self.on_command, self)

    def get_portions_for_message(self, message: str) -> tuple:
        words = message.split(" ")
        portions = []
        for i in range(len(words) - 1):
            portions.append([words[i].lower(), words[i + 1].lower()])
        return portions

    def train(self, message: str, answer: bool):

        for i in self.get_portions_for_message(message):
            self.learned_data.append({"data_tuple": i,
                                      "value": answer})

        with open(os.path.join(self.folder, "learned_data.json"), "w") as f:
            json.dump(self.learned_data, f)

    def get_response(self, message: str) -> bool:
        tuples = self.get_portions_for_message(message)
        averages = []
        for tuple in tuples:
            try:
                values = []
                for value in self.learned_data:
                    if value["data_tuple"] == tuple:
                        values.append(value["value"])
                is_true = len([value for value in values if value])
                averages.append(float(is_true) / len(values))
            except:
                averages.append(float(0))
        avg = float(0)
        for value in averages:
            avg += value
        return avg / len(averages) >= 0.5

    async def on_command(self, args):
        try:
            if args["command_args"][0] == "answer" and len(args["command_args"]) >= 3:
                resp = self.get_response(" ".join(args["command_args"][1:]))
                if resp:
                    await self.bot.send_message(args["channel"], "My research seems to say the answer is yes.")
                else:
                    await self.bot.send_message(args["channel"], "My research seems to say the answer is no.")

            if args["command_args"][0] == "train" and len(args["command_args"]) >= 4 and Owner(self.bot).has_permission(args["author"]):
                message_to_train = " ".join(args["command_args"][1:-1])
                value = bool(args["command_args"][-1])
                self.train(message_to_train, value)
        except:
            traceback.print_exc(5)

