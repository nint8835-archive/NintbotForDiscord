import asyncio
import logging

from .Permissions import Permission

__author__ = 'Riley Flynn (nint8835)'


class CommandRegistry:

    def __init__(self, bot):
        self.commands = []
        self.logger = logging.getLogger("CommandRegistry")
        self.bot = bot

    def register_command(self, command: str, description: str, required_perm: Permission, plugin_info: dict, command_handler: classmethod = None):
        self.commands.append({
            "command": command,
            "description": description,
            "required_permission": required_perm,
            "plugin_info": plugin_info,
            "handler": command_handler
        })
        self.logger.debug("New command registered. Info: {}".format(self.commands[-1]))

    def unregister_command(self, command_name: str, plugin_info: dict):
        for command in self.commands[:]:
            if command["command"] == command_name and command["plugin_info"] == plugin_info:
                self.commands.remove(command)

    def unregister_all_commands_for_plugin(self, plugin_data):
        for command in self.commands[:]:
            if command["plugin_info"] == plugin_data:
                self.commands.remove(command)

    def get_available_commands_for_user(self, user):
        return [i for i in self.commands if i["required_permission"].has_permission(user)]

    def get_info_for_command(self, command):
        return [i for i in self.commands if i["command"] == command]

    async def handle_command(self, command_name, args):
        self.logger.debug("Handling command {}.".format(command_name))
        for command in self.commands:
            if command["command"] == command_name:
                if command["handler"] is not None:
                    if command["required_permission"].has_permission(args["author"]):
                        try:
                            await asyncio.wait_for(command["handler"](args),
                                                   timeout = self.bot.config["event_timeout"],
                                                   loop = self.bot.EventManager.loop)
                        except asyncio.TimeoutError:
                            self.bot.logger.warning("Handling of {} command from plugin {} timed out.".format(command,
                                                                                                              command["plugin_info"]["plugin_name"]))
