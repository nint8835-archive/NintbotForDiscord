from .Permissions import Permission
import logging
__author__ = 'Riley Flynn (nint8835)'


class CommandRegistry:

    def __init__(self):
        self.commands = []
        self.logger = logging.getLogger("CommandRegistry")

    def register_command(self, command: str, description: str, required_perm: Permission, plugin_info: dict):
        self.commands.append({
            "command": command,
            "description": description,
            "required_permission": required_perm,
            "plugin_info": plugin_info
        })
        self.logger.debug("New command registered. Info: {}".format(self.commands[-1]))

    def unregister_command(self, command: str, plugin_info: dict):
        for command in self.commands[:]:
            if command["command"] == command and command["plugin_info"] == plugin_info:
                self.commands.remove(command)

    def unregister_all_commands_for_plugin(self, plugin_data):
        for command in self.commands[:]:
            if command["plugin_info"] == plugin_data:
                self.commands.remove(command)

    def get_available_commands_for_user(self, user):
        return [i for i in self.commands if i["required_permission"].has_permission(user)]

    def get_info_for_command(self, command):
        return [i for i in self.commands if i["command"] == command]
