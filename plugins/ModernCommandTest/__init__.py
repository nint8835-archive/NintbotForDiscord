import traceback

from NintbotForDiscord.Events import CommandSentEvent
from NintbotForDiscord.Permissions.Special import Owner
from NintbotForDiscord.Plugin import BasePlugin


class ModernCommandTest(BasePlugin):
    def __init__(self, manifest, bot_instance):
        super().__init__(manifest, bot_instance)
        self.bot.CommandRegistry.register_modern_command(
            "^test ([\\S ]+)$",
            "Tests things",
            Owner(self.bot),
            self,
            self.command_test
        )

    async def command_test(self, args: CommandSentEvent):
        try:
            await self.bot.send_message(args.channel, f"{args.args}, {args.command}")
        except:
            print(traceback.format_exc(5))
