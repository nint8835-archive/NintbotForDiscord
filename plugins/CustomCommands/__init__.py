from NintbotForDiscord.Enums import EventTypes
from NintbotForDiscord.Plugin import BasePlugin
from NintbotForDiscord.Permissions import Permission, create_match_any_permission_group
from NintbotForDiscord.Permissions.Text import ManageMessages
from NintbotForDiscord.Permissions.Special import Owner

import os
import sys
__author__ = 'Riley Flynn (nint8835)'


class Plugin(BasePlugin):

    def __init__(self, bot_instance, plugin_data, folder):
        super(Plugin, self).__init__(bot_instance, plugin_data, folder)
        self.manage_perm = create_match_any_permission_group([ManageMessages(), Owner(self.bot)])
        sys.path.append(os.path.join(folder))
        from JSONDB import JSONDatabase, SelectionMode
        global JSONDatabase, SelectionMode
        self.commands = JSONDatabase(os.path.join(self.folder, "commands.json"))
        self.refresh_custom_registry()

    def refresh_custom_registry(self):
        self.bot.CommandRegistry.unregister_all_commands_for_plugin(self.plugin_data)
        self.bot.CommandRegistry.register_command("customcommand",
                                                  "Manage custom commands.",
                                                  self.manage_perm,
                                                  self.plugin_data,
                                                  self.command_customcommand)
        for command in self.commands.select(SelectionMode.ALL).rows:
            self.bot.CommandRegistry.register_command(command["command"],
                                                      "A custom command from the Custom Commands plugin.",
                                                      Permission(),
                                                      self.plugin_data,
                                                      self.command_handle_customcommand)

    async def command_customcommand(self, args):
        if len(args["command_args"]) > 1:

            if args["command_args"][1] == "add" and len(args["command_args"]) > 3:
                command = args["command_args"][2]
                message = " ".join(args["command_args"][3:])
                if len(self.bot.CommandRegistry.get_info_for_command(command)) != 0:
                    await self.bot.send_message(args["channel"], ":no_entry_sign: That command is already registered in the command registry.")
                else:
                    self.commands.insert({"command": command, "message": message})
                    await self.bot.send_message(args["channel"], ":ballot_box_with_check: Command '{}' created.".format(command))
                    self.refresh_custom_registry()

            if args["command_args"][1] == "remove" and len(args["command_args"]) == 3:
                command = args["command_args"][2]
                sel = self.commands.select(SelectionMode.VALUE_EQUALS, "command", command)
                if len(sel) >= 1:
                    sel.remove()
                    self.refresh_custom_registry()
                    await self.bot.send_message(args["channel"], ":ballot_box_with_check: Command '{}' removed.".format(command))
                else:
                    await self.bot.send_message(args["channel"], ":no_entry_sign: That command does not exist.")

    async def command_handle_customcommand(self, args):
        sel = self.commands.select(SelectionMode.VALUE_EQUALS, "command", args["command_args"][0])
        if len(sel) == 1:
            await self.bot.send_message(args["channel"], sel[0]["message"])
