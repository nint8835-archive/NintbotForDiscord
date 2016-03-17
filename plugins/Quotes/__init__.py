import random
import traceback

from NintbotForDiscord.Enums import EventTypes
from NintbotForDiscord.Permissions.Special import Owner
from NintbotForDiscord.Permissions.Text import ManageMessages
from NintbotForDiscord.Plugin import BasePlugin
from NintbotForDiscord.Permissions import Permission, create_match_any_permission_group

import os
import sys
import datetime
__author__ = 'Riley Flynn (nint8835)'


class Plugin(BasePlugin):

    def __init__(self, bot_instance, plugin_data, folder):
        super(Plugin, self).__init__(bot_instance, plugin_data, folder)
        self.admin = create_match_any_permission_group([Owner(self.bot), ManageMessages()])
        self.bot.CommandRegistry.register_command("quote",
                                                  "View and manage quotes.",
                                                  Permission(),
                                                  plugin_data)
        self.bot.register_handler(EventTypes.CommandSent, self.on_command, self)
        sys.path.append(os.path.join(folder))
        from JSONDB import JSONDatabase, SelectionMode
        global JSONDatabase, SelectionMode
        self.quotes = JSONDatabase(os.path.join(self.folder, "quotes.json"))

    async def on_command(self, args):
        if args["command_args"][0] == "quote":
            if len(args["command_args"])>=4:
                if args["command_args"][1] == "add" and self.admin.has_permission(args["author"]):
                    try:
                        quote_msg = args["command_args"][2]
                        quote_author = " ".join(args["command_args"][3:])
                        quote_addtime = datetime.datetime.now().strftime("%x %X")
                        self.quotes.insert({"msg": quote_msg,
                                            "author": quote_author,
                                            "added_at": quote_addtime})
                        await self.bot.send_message(args["channel"], ":ballot_box_with_check: New quote added to database.")
                    except:
                        traceback.print_exc(5)
            if len(args["command_args"]) == 1:
                quote = random.choice(self.quotes.select(SelectionMode.ALL).rows)
                await self.bot.send_message(args["channel"], "\"{}\" {}".format(quote["msg"], quote["author"]))
