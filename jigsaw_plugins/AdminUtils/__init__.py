from discord import Object

from NintbotForDiscord.Permissions.Special import Owner
from NintbotForDiscord.Plugin import BasePlugin


class AdminUtils(BasePlugin):

    def __init__(self, manifest, bot_instance):
        super(AdminUtils, self).__init__(manifest, bot_instance)

        self.register_command("send",
                              "Sends a message to a specific channel.",
                              self.command_send,
                              Owner(self.bot))

    def enable(self):
        super(AdminUtils, self).enable()
        self.logger.info(f"Enabling Admin Utils v{self.manifest['version']}")

    def disable(self):
        super(AdminUtils, self).disable()
        self.logger.info(f"Disabling Admin Utils v{self.manifest['version']}")

    async def command_send(self, args: dict):
        channel_id = args["command_args"][1]
        message = " ".join(args["command_args"][2:])
        channel = Object(int(channel_id))

        await channel.send(message)
