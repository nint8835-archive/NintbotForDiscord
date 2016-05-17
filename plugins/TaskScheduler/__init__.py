import os
import json
import traceback

from discord import Object

from NintbotForDiscord.Permissions import create_match_any_permission_group
from NintbotForDiscord.Permissions.General import ManageServer
from NintbotForDiscord.Permissions.Special import Owner
from NintbotForDiscord.Plugin import BasePlugin
from plugins.TaskScheduler.CustomTasks import ScheduledMessage, RepeatingScheduledMessage

__author__ = 'Riley Flynn (nint8835)'


class Plugin(BasePlugin):

    def __init__(self, bot_instance, plugin_data, folder):
        super(Plugin, self).__init__(bot_instance, plugin_data, folder)

        try:
            with open(os.path.join(folder, "tasks.json")) as f:
                self.tasks = json.load(f)
        except FileNotFoundError:
            self.tasks = []
            self.save_tasks()

        self.bot.CommandRegistry.register_command("test_task",
                                                  "Tests scheduled tasks.",
                                                  Owner(self.bot),
                                                  plugin_data,
                                                  self.command_testtask)

        self.bot.CommandRegistry.register_command("task",
                                                  "Manages scheduled tasks.",
                                                  create_match_any_permission_group([Owner(self.bot), ManageServer()]),
                                                  plugin_data,
                                                  self.command_task)

        self.add_tasks()

    def save_tasks(self):
        with open(os.path.join(self.folder, "tasks.json"), "w") as f:
            json.dump(self.tasks, f)

    def add_tasks(self):
        self.bot.Scheduler.remove_tasks_for_plugin(self.plugin_data)
        for task in self.tasks:
            if task["type"] == "message":
                self.bot.Scheduler.add_task(ScheduledMessage(Object(task["destination"]),
                                                             task["message"],
                                                             self.bot,
                                                             self,
                                                             task["delay"]),
                                            self.plugin_data)
            elif task["type"] == "message-repeating":
                self.bot.Scheduler.add_task(RepeatingScheduledMessage(Object(task["destination"]),
                                                                      task["message"],
                                                                      self.bot,
                                                                      self,
                                                                      self.bot.Scheduler,
                                                                      task["delay"]),
                                            self.plugin_data)

    async def command_testtask(self, args):
        self.tasks.append({"type": "message-repeating",
                           "destination": args["channel"].id,
                           "message": "I'm a scheduled message. Hello!",
                           "delay": 15})
        self.add_tasks()

    async def command_task(self, args):
        try:
            if args["command_args"][1] == "add":
                delay = int(args["command_args"][3])

                if args["command_args"][2] == "message-repeating":
                    self.tasks.append({"type": "message-repeating",
                                       "destination": args["channel"].id,
                                       "message": args["command_args"][4],
                                       "delay": delay})
                    await self.bot.send_message(args["channel"], ":ballot_box_with_check: Task added.")
                    self.save_tasks()
                    self.add_tasks()

            elif args["command_args"][1] == "list":
                await self.bot.send_message(args["channel"], "```{}```".format("\n".join(
                    ["{}:\n{}".format(index + 1, json.dumps(item, sort_keys=True, indent=4)) for index, item in enumerate(self.tasks)]
                )))

            elif args["command_args"][1] == "remove":
                self.tasks.remove(self.tasks[int(args["command_args"][2]) - 1])
                await self.bot.send_message(args["channel"], ":ballot_box_with_check: Task removed.")
                self.save_tasks()
                self.add_tasks()
        except:
            traceback.print_exc(5)
