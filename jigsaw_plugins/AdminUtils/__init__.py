from discord import Object

from NintbotForDiscord.Permissions.Special import Owner
from plugins.JigsawLoader import NintbotPlugin


class AdminUtils(NintbotPlugin):

    def enable(self):
        self.logger.info(f"Enabling Admin Utils v{self.manifest['version']}")

        self.logger.debug("Registering commands...")
        self.bot.CommandRegistry.register_command("send",
                                                  "Sends a message to a specific channel",
                                                  Owner(self.bot),
                                                  self.plugin_info,
                                                  self.command_send)
        self.logger.debug("Commands registered.")

        self.logger.info(f"Finished enabling Admin Utils v{self.manifest['version']}")

    def disable(self):
        self.logger.info(f"Disabling Admin Utils v{self.manifest['version']}")

        self.logger.debug("Unregistering commands...")
        self.bot.CommandRegistry.unregister_all_commands_for_plugin(self.plugin_info)
        self.logger.debug("Commands unregistered.")

        self.logger.info(f"Finished disabling Admin Utils v{self.manifest['version']}")

    async def command_send(self, args: dict):
        channel_id = args["command_args"][1]
        message = " ".join(args["command_args"][2:])
        channel = Object(channel_id)

        await self.bot.send_message(channel, message)
