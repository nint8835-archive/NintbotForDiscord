import json
import os
import aiohttp
import feedparser
from discord import Object

from NintbotForDiscord.Plugin import BasePlugin
from NintbotForDiscord.ScheduledTask import RepeatingScheduledTask

__author__ = 'Riley Flynn (nint8835)'


class FeedCheckRepeatingTask(RepeatingScheduledTask):

    def __init__(self, feed, feed_desc, channel, plugin_instance, delay):
        RepeatingScheduledTask.__init__(self, plugin_instance.bot.Scheduler, plugin_instance.plugin_data, delay)
        self.channel = channel
        self.feed = feed
        self.plugin = plugin_instance
        self.first_run = True
        self.feed_desc = feed_desc
        self.seen_posts = []

    async def execute_task(self):
        print("Checking feed {}".format(self.feed))
        with aiohttp.ClientSession() as session:
            async with session.get(self.feed) as resp:
                feed = feedparser.parse(await resp.text())
                print(feed)
                for entry in feed.entries:
                    print(entry)
                    if entry not in self.seen_posts:
                        self.seen_posts.append(entry)
                        print(self.first_run)
                        if not self.first_run:
                            await self.plugin.bot.send_message(Object(self.channel),
                                                               "New post from {}: ```{}```{}".format(self.feed_desc,
                                                                                                      entry["title_detail"]["value"],
                                                                                                      entry["link"]))
        self.first_run = False
        await RepeatingScheduledTask.execute_task(self)


class Plugin(BasePlugin):

    def __init__(self, bot_instance, plugin_data, folder):
        super(Plugin, self).__init__(bot_instance, plugin_data, folder)
        with open(os.path.join(folder, "feeds.json")) as f:
            self.feeds = json.load(f)
        for feed in self.feeds:
            self.bot.Scheduler.add_task(FeedCheckRepeatingTask(feed["url"], feed["desc"], feed["channel"], self, 5), self.plugin_data)
