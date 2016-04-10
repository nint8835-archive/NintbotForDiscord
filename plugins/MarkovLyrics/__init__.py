import os
import random

from pymarkovchain import MarkovChain

from NintbotForDiscord.Permissions import Permission
from NintbotForDiscord.Permissions.Special import Owner
from NintbotForDiscord.Plugin import BasePlugin

__author__ = 'Riley Flynn (nint8835)'


class Plugin(BasePlugin):
    def __init__(self, bot_instance, plugin_data, folder):
        super(Plugin, self).__init__(bot_instance, plugin_data, folder)
        self.artists = []
        self.chain = MarkovChain()
        self.title_chain = MarkovChain()

        self.bot.CommandRegistry.register_command("lyricchain",
                                                  "Generates text using markov chains of song lyrics.",
                                                  Permission(),
                                                  plugin_data,
                                                  self.command_lyricchain)

        self.bot.CommandRegistry.register_command("reloadlyrics",
                                                  "Reloads the song lyrics.",
                                                  Owner(self.bot),
                                                  plugin_data,
                                                  self.command_reloadlyrics)

        self.load_lyrics()

    async def command_lyricchain(self, args):
        await self.bot.send_message(args["channel"], "\"{}\" -{} by {}".format(self.chain.generateString(),
                                                                               self.title_chain.generateString(),
                                                                               random.choice(self.artists)))

    async def command_reloadlyrics(self, args):
        self.load_lyrics()

    def load_lyrics(self):
        lyrics = []
        song_titles = []
        for item in os.listdir(os.path.join(self.folder, "lyrics")):
            with open(os.path.join(self.folder, "lyrics", item)) as f:
                song_titles.append(item.split("- ")[1])
                artist = item.split(" -")[0]
                if artist not in self.artists:
                    self.artists.append(artist)
                lyrics.append(f.read())
        self.chain.generateDatabase("\n".join(lyrics))
        self.title_chain.generateDatabase("\n".join(song_titles))
