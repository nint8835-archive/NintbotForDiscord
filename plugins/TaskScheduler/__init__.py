import os
import json

from discord import Object

from NintbotForDiscord.Permissions.Special import Owner
from NintbotForDiscord.Plugin import BasePlugin
from plugins.TaskScheduler.CustomTasks import ScheduledMessage

__author__ = 'Riley Flynn (nint8835)'


class Plugin(BasePlugin):

    def __init__(self, bot_instance, plugin_data, folder):
        super(Plugin, self).__init__(bot_instance, plugin_data, folder)

        try:
            with open(os.path.join(folder, "tasks.json")) as f:
                self.tasks = json.load(f)
        except FileNotFoundError:
            self.tasks = []
            # self.task_objs
            self.save_tasks()

        self.bot.CommandRegistry.register_command("test_task",
                                                  "Tests scheduled tasks.",
                                                  Owner(self.bot),
                                                  plugin_data,
                                                  self.command_testtask)

    def save_tasks(self):
        with open(os.path.join(self.folder, "tasks.json"), "w") as f:
            json.dump(self.tasks, f)

    def add_tasks(self):
        for task in self.tasks:
            if task["type"] == "message":
                self.bot.Scheduler.add_task(ScheduledMessage(Object(task["destination"]), task["message"], self.bot, self, task["delay"]))

    async def command_testtask(self, args):
        self.tasks.append({"type": "message",
                           "destination": args["channel"].id,
                           "message": "I'm a scheduled message. Hello!",
                           "delay": 5})
        self.add_tasks()
