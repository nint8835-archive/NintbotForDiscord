from NintbotForDiscord.ScheduledTask import MessageScheduledTask, RepeatingScheduledTask, ScheduledTask

__author__ = 'Riley Flynn (nint8835)'


class TaskSchedulerTask(ScheduledTask):

    def __init__(self, plugin_instance, delay = 30):
        ScheduledTask.__init__(self, delay)
        self.plugin = plugin_instance

    def construct_dict_obj(self):
        return {"type": "generic",
                "created": self.created,
                "delay": self.delay}

    async def execute_task(self):
        await ScheduledTask.execute_task(self)
        try:
            self.plugin.tasks.remove(self.construct_dict_obj())
        except ValueError:
            pass


class RepeatingTaskSchedulerTask(TaskSchedulerTask, RepeatingScheduledTask):

    def __init__(self, plugin_instance, scheduler, delay = 30):
        TaskSchedulerTask.__init__(self, plugin_instance, delay)
        RepeatingScheduledTask.__init__(self, scheduler, self.plugin.plugin_data, delay)

    async def execute_task(self):
        await TaskSchedulerTask.execute_task(self)
        await RepeatingScheduledTask.execute_task(self)
        self.plugin.tasks.append(self.construct_dict_obj())


class ScheduledMessage(TaskSchedulerTask, MessageScheduledTask):

    def __init__(self, destination, message, bot_instance, plugin_instance, delay = 30):
        TaskSchedulerTask.__init__(self, plugin_instance, delay)
        MessageScheduledTask.__init__(self, destination, message, bot_instance, delay)

    def construct_dict_obj(self):
        return {"type": "message",
                "destination": self.destination.id,
                "message": self.message,
                "delay": self.delay}

    async def execute_task(self):
        await TaskSchedulerTask.execute_task(self)
        await MessageScheduledTask.execute_task(self)


class RepeatingScheduledMessage(ScheduledMessage, RepeatingTaskSchedulerTask):

    def __init__(self, destination, message, bot_instance, plugin_instance, scheduler, delay = 30):
        ScheduledMessage.__init__(self, destination, message, bot_instance, plugin_instance, delay)
        RepeatingTaskSchedulerTask.__init__(self, plugin_instance, scheduler, delay)

    def construct_dict_obj(self):
        return {"type": "message-repeating",
                "destination": self.destination.id,
                "message": self.message,
                "delay": self.delay}

    async def execute_task(self):
        await ScheduledMessage.execute_task(self)
        await RepeatingTaskSchedulerTask.execute_task(self)
