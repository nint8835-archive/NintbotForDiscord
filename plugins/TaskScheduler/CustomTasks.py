from NintbotForDiscord.ScheduledTask import MessageScheduledTask

__author__ = 'Riley Flynn (nint8835)'


class ScheduledMessage(MessageScheduledTask):

    def __init__(self, destination, message, bot_instance, plugin_instance, delay = 30):
        super().__init__(destination, message, bot_instance, delay)
        self.plugin = plugin_instance

    def construct_dict_obj(self):
        return {"type": "message",
                "destination": self.destination.id,
                "message": self.message,
                "delay": self.delay}

    async def execute_task(self):
        await super(ScheduledMessage, self).execute_task()
        self.plugin.tasks.remove(self.construct_dict_obj())
