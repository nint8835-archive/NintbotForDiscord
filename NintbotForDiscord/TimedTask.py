import time

__author__ = 'Riley Flynn (nint8835)'


class TimedTask:

    def __init__(self, delay = 30):
        self.created = time.time()
        self.delay = delay

    def check_task(self):
        return time.time() - self.created >= self.delay

    async def execute_task(self):
        pass


class RepeatingTimedTask(TimedTask):

    def __init__(self, task_manager, delay=30):
        super(RepeatingTimedTask, self).__init__(delay)
        self.task_manager = task_manager

    async def execute_task(self):
        self.created = time.time()
        self.task_manager.add_task(self)


class RepeatingTimedTaskWrapper(RepeatingTimedTask):

    def __init__(self, task, task_manager):
        super(RepeatingTimedTaskWrapper, self).__init__(task_manager, task.delay)
        self.task = task
        self.task_manager = task_manager

    def check_task(self):
        return self.task.check_task()

    async def execute_task(self):
        await self.task.execute_task()
        await super(RepeatingTimedTaskWrapper, self).execute_task()


class MessageTimedTask(TimedTask):

    def __init__(self, destination, message, bot_instance, delay=30):
        super(MessageTimedTask, self).__init__(delay)
        self.destination = destination
        self.message = message
        self.bot = bot_instance

    async def execute_task(self):
        await self.bot.send_message(self.destination, self.message)


class RepeatingMessageTimedTask(RepeatingTimedTask):

    def __init__(self, destination, message, bot_instance, task_manager, delay=30):
        super(RepeatingMessageTimedTask, self).__init__(task_manager, delay)
        self.destination = destination
        self.message = message
        self.bot = bot_instance

    async def execute_task(self):
        await super(RepeatingMessageTimedTask, self).execute_task()
        await self.bot.send_message(self.destination, self.message)
