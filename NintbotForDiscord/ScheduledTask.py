import time

from discord.utils import find

__author__ = 'Riley Flynn (nint8835)'


class ScheduledTask:

    def __init__(self, delay = 30):
        self.created = time.time()
        self.delay = delay

    def check_task(self):
        return time.time() - self.created >= self.delay

    async def execute_task(self):
        pass


class RepeatingScheduledTask(ScheduledTask):

    def __init__(self, scheduler, delay=30):
        ScheduledTask.__init__(self, delay)
        self.scheduler = scheduler

    async def execute_task(self):
        self.created = time.time()
        self.scheduler.add_task(self)


class RepeatingScheduledTaskWrapper(RepeatingScheduledTask):

    def __init__(self, task, scheduler):
        RepeatingScheduledTask.__init__(self, scheduler, task.delay)
        self.task = task
        self.scheduler = scheduler

    def check_task(self):
        return self.task.check_task()

    async def execute_task(self):
        await RepeatingScheduledTask.execute_task(self)
        await self.task.execute_task()


class MessageScheduledTask(ScheduledTask):

    def __init__(self, destination, message, bot_instance, delay=30):
        ScheduledTask.__init__(self, delay)
        self.destination = destination
        self.message = message
        self.bot = bot_instance

    async def execute_task(self):
        await self.bot.send_message(self.destination, self.message)


class RepeatingMessageScheduledTask(RepeatingScheduledTask, MessageScheduledTask):

    def __init__(self, destination_id, message, bot_instance, scheduler, delay=30):
        RepeatingScheduledTask.__init__(self, scheduler, delay)
        MessageScheduledTask.__init__(self, destination_id, message, bot_instance, delay)

    async def execute_task(self):
        await RepeatingMessageScheduledTask.execute_task(self)
        await MessageScheduledTask.execute_task(self)


class AddRoleScheduledTask(ScheduledTask):

    def __init__(self, user_id, server_id, role_id, bot_instance, delay=30):
        ScheduledTask.__init__(self, delay)
        self.user_id = user_id
        self.server_id = server_id
        self.role_id = role_id
        self.bot = bot_instance

    async def execute_task(self):
        await ScheduledTask.execute_task(self)
        server = find(lambda s: s.id == self.server_id, self.bot.servers)
        role = find(lambda r: r.id == self.role_id, server.roles)
        await self.bot.add_roles(server.get_member(self.user_id), role)


class RemoveRoleScheduledTask(ScheduledTask):

    def __init__(self, user_id, server_id, role_id, bot_instance, delay=30):
        ScheduledTask.__init__(self, delay)
        self.user_id = user_id
        self.server_id = server_id
        self.role_id = role_id
        self.bot = bot_instance

    async def execute_task(self):
        await ScheduledTask.execute_task(self)
        server = find(lambda s: s.id == self.server_id, self.bot.servers)
        role = find(lambda r: r.id == self.role_id, server.roles)
        await self.bot.remove_roles(server.get_member(self.user_id), role)
