import logging

from NintbotForDiscord.Enums import EventTypes
from NintbotForDiscord.Permissions import Permission
from NintbotForDiscord import Bot
from jigsaw import JigsawPlugin


class NintbotPlugin(JigsawPlugin):

    def __init__(self, manifest, bot_instance):
        super(NintbotPlugin, self).__init__(manifest)

        self.bot = bot_instance  # type: Bot.Bot

        self.plugin_info = {
            "plugin_name": self.manifest.get("name", "Unnamed Plugin"),
            "plugin_developer": self.manifest.get("developer", "Unspecified Developer"),
            "plugin_version": self.manifest.get("version", "0.0.0"),
            "module_name": self.manifest.get("module_name", self.manifest.get("name", "Unnamed Plugin")),
            "main_file": self.manifest.get("main_path", "__init__.py")
        }

        self._registered_commands = []
        self._registered_handlers = []

        self.logger = logging.getLogger(self.plugin_info["plugin_name"])

    def register_command(self, name: str, description: str, method: classmethod, permission: Permission = Permission()) -> None:
        """
        Adds a command to the internal command registry to be auto-registered/unregistered on enable/disable
        :param name: The command name
        :param description: The command description
        :param method: The method that will handle the command
        :param permission: The permission required to use the command
        """
        self._registered_commands.append({
            "command": name,
            "description": description,
            "required_perm": permission,
            "plugin_info": self.plugin_info,
            "command_handler": method
        })

    def register_handler(self, event_type: EventTypes, event_handler: classmethod) -> None:
        """
        Adds a handler to the internal handler registry to be auto-registered/unregistered on enable/disable
        :param event_type: The type of event this handler will handle
        :param event_handler: The method that will handle the event
        """
        self._registered_handlers.append({
            "event_type": event_type,
            "event_handler": event_handler,
            "plugin": self
        })

    def enable(self) -> None:
        self.logger.debug("Registering commands...")
        for command in self._registered_commands:
            self.bot.CommandRegistry.register_command(**command)
        self.logger.debug("Commands registered.")

        self.logger.debug("Registering handlers...")
        for handler in self._registered_handlers:
            self.bot.EventManager.register_handler(**handler)
        self.logger.debug("Handlers registered.")

    def disable(self) -> None:
        self.logger.debug("Unregistering commands...")
        self.bot.CommandRegistry.unregister_all_commands_for_plugin(self.plugin_info)
        self.logger.debug("Commands unregistered.")

        self.logger.debug("Unregistering handlers...")
        self.bot.EventManager.remove_handlers(self)
