import asyncio

__author__ = 'Riley Flynn (nint8835)'


class TimedTaskManager:

    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.tasks = []
        self.bot.EventManager.loop.create_task(self.handle_tasks())

    async def handle_tasks(self):
        while not self.bot.is_closed:

            for task in self.tasks[:]:
                if task.check_task():
                    self.tasks.remove(task)
                    await task.execute_task()

            await asyncio.sleep(1)

    def add_task(self, task_instance):
        self.tasks.append(task_instance)
