import shlex
import subprocess
import os
import json
import math
import asyncio
import traceback
import logging
import soundcloud

import youtube_dl
from googleapiclient.discovery import build

from discord import ClientException, ChannelType, Member
from discord.voice_client import ProcessPlayer
from discord.opus import load_opus

from NintbotForDiscord.Plugin import BasePlugin
from NintbotForDiscord.Permissions import Permission, create_match_any_permission_group, create_permission_group
from NintbotForDiscord.Permissions.Voice import MuteMembers, MoveMembers
from NintbotForDiscord.Permissions.Special import Owner

__author__ = 'Riley Flynn (nint8835)'


class VoidLogger:

    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass

    def info(self, msg):
        pass




class WhitelistedUser(Permission):

    def __init__(self, plugin_instance):
        self.plugin = plugin_instance

    def has_permission(self, member: Member) -> bool:
        return True


class InWhitelistedServer(Permission):

    def __init__(self, plugin_instance):
        self.plugin = plugin_instance

    def has_permission(self, member: Member) -> bool:
        # try:
        #     return member.server.id in self.plugin.config["whitelisted_servers"]
        # except:
        #     return False
        return True


# noinspection PyProtectedMember,PyAttributeOutsideInit
class Plugin(BasePlugin):

    def __init__(self, manifest, bot_instance):
        super(Plugin, self).__init__(manifest, bot_instance)
        self.queue = asyncio.Queue()
        with open(os.path.join(self.manifest["path"], "config.json")) as f:
            self.config = json.load(f)
        with open(os.path.join(self.manifest["path"], "queue.json")) as f:
            for item in json.load(f):
                self.bot.EventManager.loop.create_task(self.queue.put(item))
        self.admin = create_match_any_permission_group([Owner(self.bot), MuteMembers()])
        self.admin = create_permission_group([self.admin, InWhitelistedServer(self)])

        self.bot.CommandRegistry.register_command("play",
                                                  "Adds a song to the song queue.",
                                                  InWhitelistedServer(self),
                                                  self,
                                                  self.command_play)
        self.bot.CommandRegistry.register_command("joinvoice",
                                                  "Makes the bot connect to a voice channel.",
                                                  WhitelistedUser(self),
                                                  self,
                                                  self.command_joinvoice)
        self.bot.CommandRegistry.register_command("leavevoice",
                                                  "Makes the bot disconnect from a voice channel",
                                                  WhitelistedUser(self),
                                                  self,
                                                  self.command_leavevoice)
        self.bot.CommandRegistry.register_command("skip",
                                                  "Votes to skip the current song.",
                                                  InWhitelistedServer(self),
                                                  self,
                                                  self.command_skip)
        self.bot.CommandRegistry.register_command("youtube",
                                                  "Searches your request on Youtube and adds the first result to the queue.",
                                                  InWhitelistedServer(self),
                                                  self,
                                                  self.command_youtube)
        self.bot.CommandRegistry.register_command("soundcloud",
                                                  "Searches your request on Soundcloud and adds the first result to the queue.",
                                                  InWhitelistedServer(self),
                                                  self,
                                                  self.command_soundcloud)
        self.bot.CommandRegistry.register_command("queue",
                                                  "Gets the current queue.",
                                                  InWhitelistedServer(self),
                                                  self,
                                                  self.command_queue)
        self.bot.CommandRegistry.register_command("song",
                                                  "Gets the current song.",
                                                  InWhitelistedServer(self),
                                                  self,
                                                  self.command_song)
        self.bot.CommandRegistry.register_command("volume",
                                                  "Changes the playback volume for the remaining songs in the queue.",
                                                  self.admin,
                                                  self,
                                                  self.command_volume)
        self.bot.CommandRegistry.register_command("rate",
                                                  "Changes the sample rate of the remaining songs in the queue.",
                                                  self.admin,
                                                  self,
                                                  self.command_rate)
        self.bot.CommandRegistry.register_command("voteskip",
                                                  "Toggles the ability to voteskip songs.",
                                                  self.admin,
                                                  self,
                                                  self.command_voteskip)
        self.bot.CommandRegistry.register_command("ffmpegopts",
                                                  "Changes the FFMPEG filter options.",
                                                  self.admin,
                                                  self,
                                                  self.command_ffmpegopts)
        self.bot.CommandRegistry.register_command("priority_play",
                                                  "Adds a song to the beginning of the queue and bypasses all restrictions.",
                                                  self.admin,
                                                  self,
                                                  self.command_priority_play)

        load_opus(os.path.join(self.manifest["path"], "libopus"))
        # self.text_channel = Channel()
        logging.getLogger("googleapiclient.discovery").setLevel(logging.ERROR)
        self._youtube = build("youtube", "v3", developerKey = self.config["youtube_api_key"])
        self.soundcloud = soundcloud.Client(client_id=self.config["soundcloud_client_id"])
        self.joined_voice = False
        self.skips = []
        self.messages = []
        self.song = {}
        self.next_song_event = asyncio.Event()
        self.bot.EventManager.loop.create_task(self.song_queue())
        # self.bot.EventManager.loop.create_task(self.purge_messages())

    def has_hit_limit(self, user: str) -> bool:
        count = 0
        for item in self.queue._queue:
            if item["requester"] == user:
                count += 1
        return count >= self.config["limit"]

    def is_in_time_limit(self, info: dict) -> bool:
        return info["duration"] <= self.config["max_duration"]

    # noinspection PyBroadException
    def get_stream_info(self, url):
        import youtube_dl

        opts = {
            'format': 'webm[abr>0]' if 'youtube' in url else 'best',
            'prefer_ffmpeg': True,
            'logger': VoidLogger()
        }

        ydl = youtube_dl.YoutubeDL(opts)
        try:
            info = ydl.extract_info(url, download=False)
            for blacklist in self.config["blacklisted"]:
                if blacklist in str(info["title"]).lower():
                    print(blacklist)
                    return None
            return info
        except:

            return None


    def toggle_next_song(self):
        self.logger.debug("Setting next song event...")
        self.bot.loop.call_soon_threadsafe(self.next_song_event.set)

    def dump_queue(self):
        try:
            queue = []
            for item in self.queue._queue:
                queue.append(item)
            print(json.dumps(queue))
            with open(os.path.join(self.manifest["path"], "queue.json"), "w") as f:
                json.dump(queue, f)
        except:
            traceback.print_exc(5)

    def get_queue_length(self) -> int:
        length = 0
        for item in self.queue._queue:
            try:
                length += item["info"]["duration"]
            except:
                pass
        return length

    def get_queue_length_formatted(self) -> str:
        seconds = self.get_queue_length()
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return "{} hours, {} minutes, and {} seconds".format(h, m, s)

    def custom_ffmpeg_player(self, filename, volume, playback_rate, *, use_avconv=False, pipe = False, options = None, after = None):
        command = 'ffmpeg' if not use_avconv else 'avconv'
        input_name = '-' if pipe else shlex.quote(filename)
        cmd = command + ' -i {} -f s16le -ar {} -ac {} {} -loglevel warning pipe:1'
        cmd = cmd.format(input_name, self.voice.encoder.sampling_rate, self.voice.encoder.channels, "-af \"volume={}{}{}\"".format(volume, playback_rate, self.config["ffmpeg_options"]))
        if isinstance(options, str):
            cmd = cmd + ' ' + options

        stdin = None if not pipe else filename
        args = shlex.split(cmd)
        try:
            p = subprocess.Popen(args, stdin = stdin, stdout = subprocess.PIPE)
            return ProcessPlayer(p, self.voice, after)
        except subprocess.SubprocessError as e:
            raise ClientException('Popen failed: {0.__name__} {1}'.format(type(e), str(e)))

    def custom_ytdl_player(self, url, *, options = None, use_avconv = False, after = None):

        opts = {
            'format': 'webm[abr>0]' if 'youtube' in url else 'best',
            'prefer_ffmpeg': not use_avconv,
            'logger': VoidLogger()
        }
        if options is not None and isinstance(options, dict):
            opts.update(options)

        ydl = youtube_dl.YoutubeDL(opts)
        info = ydl.extract_info(url, download = False)

        if self.config["playback_rate"] == 0:
            rate = ""
        else:
            rate = ",asetrate=r={}".format(self.config["playback_rate"])

        return self.custom_ffmpeg_player(info['url'], volume = self.config["playback_volume"], playback_rate = rate, use_avconv = use_avconv, after = after)

    # noinspection PyBroadException
    async def song_queue(self):
        while not self.bot.is_closed:
            self.skips = []
            waiting_to_join = True
            while waiting_to_join:
                try:
                    waiting_to_join = not self.voice.is_connected()
                except:
                    waiting_to_join = True
                if waiting_to_join:
                    await asyncio.sleep(5)
            self.logger.debug("Waiting for new song...")
            self.song = await self.queue.get()
            self.logger.debug("Got new song.")
            self.dump_queue()
            self.player = self.custom_ytdl_player(self.song["url"],
                                                  after=self.toggle_next_song)
            self.next_song_event.clear()
            self.player.start()
            message = await self.bot.send_message(self.text_channel, ":speaker: Now playing {}, requested by {}.".format(self.song["info"]["title"], self.song["requester"]))
            self.messages.append(message)
            self.logger.debug("Waiting for song to end...")
            await self.next_song_event.wait()
            self.logger.debug("Song ended.")

    async def purge_messages(self):
        while not self.bot.is_closed:
            if len(self.messages) >= 1:
                await asyncio.sleep(10)
                def check_func(m):
                    return m in self.messages
                def second_check_func(m):
                    return any([m.content.startswith(self.bot.config["command_prefix"]+i) for i in [
                        "play",
                        "skip",
                        "youtube",
                        "priority_play"
                    ]])
                try:
                    await self.bot.purge_from(self.messages[0].channel, check=check_func)
                    await self.bot.purge_from(self.messages[0].channel, check=second_check_func)
                except:
                    traceback.print_exc(5)
                self.messages = []
            await asyncio.sleep(5)

    async def command_play(self, args):
        self.text_channel = args["message"].channel
        if len(args["command_args"]) >= 2:
            for item in args["command_args"][1:]:
                try:
                    domain = ".".join(item.split("://")[1].split("/")[0].split(".")[-2:])
                    if (domain in self.config["whitelisted_domains"] or self.admin.has_permission(args["author"])) and item.count("&list=") < 1:
                        stream_info_getter = self.bot.EventManager.loop.run_in_executor(None, self.get_stream_info, item)
                        stream_info = await stream_info_getter
                        if stream_info is not None:
                            info = {"url": item, "info": stream_info, "requester": args["author"].name}
                            if not self.has_hit_limit(args["author"].name):
                                if self.is_in_time_limit(info["info"]):
                                    await self.queue.put(info)
                                    message = await self.bot.send_message(args["message"].channel,
                                                                ":ok_hand: Song {} added to queue.".format(info["info"]["title"]))
                                    self.messages.append(message)
                                else:
                                    message = await self.bot.send_message(args["message"].channel,
                                                                ":no_entry_sign: The requested song is too long.")
                                    self.messages.append(message)
                            else:
                                message = await self.bot.send_message(args["message"].channel,
                                                            ":no_entry_sign: You have hit the maximum number of requests. Please wait for some of your requests to play and try again.")
                                self.messages.append(message)
                            self.dump_queue()

                        else:
                            message = await self.bot.send_message(args["message"].channel,
                                                        ":no_entry_sign: Song from {} failed to be added to queue. Please use a different upload of the song.".format(item))
                            self.messages.append(message)
                except:
                    pass

    async def command_joinvoice(self, args):
        self.text_channel = args["message"].channel
        try:
            await self.voice.disconnect()
        except:
            pass
        if self.bot.is_voice_connected(args["channel"].server):
            self.voice = self.bot.voice_client_in(args["channel"].server)
        else:
            if len(args["command_args"]) == 1:
                for channel in [i for i in args["message"].server.channels if i.type == ChannelType.voice]:
                    if args["author"] in channel.voice_members:
                        self.voice = await self.bot.join_voice_channel(channel)
                        message = await self.bot.send_message(args["message"].channel,
                                                         ":ok_hand: Joined voice channel \"{}\"".format(channel.name))
                        self.messages.append(message)
            if len(args["command_args"]) > 1:
                joined = False
                for channel in [i for i in args["message"].server.channels if i.type == ChannelType.voice]:
                    if channel.name == args["command_args"][1]:
                        await self.bot.join_voice_channel(channel)
                        message = await self.bot.send_message(args["message"].channel,
                                                         ":ok_hand: Joined voice channel \"{}\"".format(channel.name))
                        self.messages.append(message)
                        joined = True
                        break

                if not joined:
                    message = await self.bot.send_message(args["channel"], ":no_entry_sign: Channel not found.")
                    self.messages.append(message)

    async def command_leavevoice(self, args):
        self.text_channel = args["message"].channel
        try:
            await self.voice.disconnect()
            message = await self.bot.send_message(self.text_channel, ":ok_hand: Disconnected from voice.")
            self.messages.append(message)
        except:
            message = await self.bot.send_message(args["channel"], ":no_entry_sign: The bot is not in a voice channel.")
            self.messages.append(message)

    async def command_skip(self, args):
        self.text_channel = args["message"].channel
        if self.admin.has_permission(args["author"]):
            message = await self.bot.send_message(self.text_channel, ":ok_hand: Admin skipped song.")
            self.messages.append(message)
            try:
                self.player.stop()
            except:
                pass
            # self.toggle_next_song()

        elif args["author"] in self.voice.channel.voice_members and args["author"] not in self.skips and self.config["voteskip_enabled"]:
            self.skips.append(args["author"])
            message = await self.bot.send_message(self.text_channel, ":question: {} of the required {} users have voted to skip.".format(len(self.skips), int(math.ceil((len(self.voice.channel.voice_members)-1)/2))))
            self.messages.append(message)
            if len(self.skips) >= int(math.ceil((len(self.voice.channel.voice_members)-1)/2)):
                message = await self.bot.send_message(self.text_channel, ":ok_hand: Vote passed.")
                self.messages.append(message)
                self.player.stop()
                # self.toggle_next_song()

    async def command_youtube(self, args):
        self.text_channel = args["message"].channel
        if len(args["command_args"])>=2:
            try:
                query = " ".join(args["command_args"][1:])
                results = self._youtube.search().list(
                    q=query,
                    part="id",
                    maxResults = 10
                ).execute().get("items", [])
                for result in results:
                    if result["id"]["kind"] == "youtube#video":
                        item = "https://www.youtube.com/watch?v={}".format(result["id"]["videoId"])
                        break
                    else:
                        item = ""

                if item != "":
                    stream_info_getter = self.bot.EventManager.loop.run_in_executor(None, self.get_stream_info, item)
                    stream_info = await stream_info_getter
                    if stream_info is not None:
                        info = {"url": item, "info": stream_info, "requester": args["author"].name}
                        if not self.has_hit_limit(args["author"].name):
                            if self.is_in_time_limit(info["info"]):
                                    await self.queue.put(info)
                                    message = await self.bot.send_message(args["message"].channel,
                                                                ":ok_hand: Song {} added to queue.".format(info["info"]["title"]))
                                    self.messages.append(message)
                            else:
                                message = await self.bot.send_message(args["message"].channel,
                                                            ":no_entry_sign: The requested song is too long.")
                                self.messages.append(message)
                        else:
                            message = await self.bot.send_message(args["message"].channel,
                                                        ":no_entry_sign: You have hit the maximum number of requests. Please wait for some of your requests to play and try again.")
                            self.messages.append(message)

                        self.dump_queue()
                    else:
                        message = await self.bot.send_message(args["message"].channel,
                                                    ":no_entry_sign: Song from {} failed to be added to queue. Please use a different upload of the song.".format(item))
                        self.messages.append(message)
            except:
                traceback.print_exc(5)

    async def command_queue(self, args):
        self.text_channel = args["message"].channel
        # noinspection PyProtectedMember
        message = await self.bot.send_message(self.text_channel, "```{}```\nThe queue will take an estimated {} to complete.".format("\n".join([item["info"]["title"] for item in self.queue._queue]), self.get_queue_length_formatted()))
        self.messages.append(message)

    async def command_volume(self, args):
        self.text_channel = args["message"].channel
        if len(args["command_args"])==2:
            self.config["playback_volume"] = args["command_args"][1]
            message = await self.bot.send_message(self.text_channel, ":ok_hand: Playback volume set to {}%.".format(float(self.config["playback_volume"]) * 100))
            self.messages.append(message)

    async def command_rate(self, args):
        self.text_channel = args["message"].channel
        if len(args["command_args"])==2:
            self.config["playback_rate"] = int(args["command_args"][1])
            if args["command_args"][1] == "0":
                message = await self.bot.send_message(self.text_channel, ":ok_hand: Playback rate set to content default.".format(self.config["playback_rate"]))
                self.messages.append(message)
            else:
                message = await self.bot.send_message(self.text_channel, ":ok_hand: Playback rate set to {}Hz.".format(self.config["playback_rate"]))
                self.messages.append(message)

    async def command_voteskip(self, args):
        self.text_channel = args["message"].channel
        self.config["voteskip_enabled"] = not self.config["voteskip_enabled"]
        message = await self.bot.send_message(args["channel"], ":ok_hand: Voteskip enabled status set to {}.".format(self.config["voteskip_enabled"]))
        self.messages.append(message)

    async def command_ffmpegopts(self, args):
        self.text_channel = args["message"].channel
        if len(args["command_args"])>=2:
            if args["command_args"][1] == "NONE":
                self.config["ffmpeg_options"] = ""
            else:
                self.config["ffmpeg_options"] = " ".join(args["command_args"][1:])
            message = await self.bot.send_message(self.text_channel, ":ok_hand: FFMPEG options updated")
            self.messages.append(message)

    async def command_priority_play(self, args):
        self.text_channel = args["message"].channel
        if len(args["command_args"]) >= 2:
            for item in args["command_args"][1:]:
                try:
                    stream_info_getter = self.bot.EventManager.loop.run_in_executor(None, self.get_stream_info, item)
                    stream_info = await stream_info_getter
                    if stream_info is not None:
                        info = {"url": item, "info": stream_info, "requester": args["author"].name}
                        backup_queue = self.queue._queue
                        self.queue = asyncio.Queue()
                        await self.queue.put(info)
                        for backup_item in backup_queue:
                            await self.queue.put(backup_item)
                        message = await self.bot.send_message(args["message"].channel,
                                                    ":ok_hand: Song {} added to top of queue.".format(info["info"]["title"]))
                        self.messages.append(message)
                        self.dump_queue()

                    else:
                        message = await self.bot.send_message(args["message"].channel,
                                                    ":no_entry_sign: Song from {} failed to be added to queue. Please use a different upload of the song.".format(item))
                        self.messages.append(message)
                except:
                    pass

    async def command_soundcloud(self, args):
        self.text_channel = args["message"].channel
        if len(args["command_args"])>=2:
            try:
                query = " ".join(args["command_args"][1:])
                tracks = self.soundcloud.get('/tracks', q=query)
                item = tracks[0].permalink_url
                if item != "":
                    stream_info_getter = self.bot.EventManager.loop.run_in_executor(None, self.get_stream_info, item)
                    stream_info = await stream_info_getter
                    if stream_info is not None:
                        info = {"url": item, "info": stream_info, "requester": args["author"].name}
                        if not self.has_hit_limit(args["author"].name):
                            if self.is_in_time_limit(info["info"]):
                                    await self.queue.put(info)
                                    message = await self.bot.send_message(args["message"].channel,
                                                                ":ok_hand: Song {} added to queue.".format(info["info"]["title"]))
                                    self.messages.append(message)
                            else:
                                message = await self.bot.send_message(args["message"].channel,
                                                            ":no_entry_sign: The requested song is too long.")
                                self.messages.append(message)
                        else:
                            message = await self.bot.send_message(args["message"].channel,
                                                        ":no_entry_sign: You have hit the maximum number of requests. Please wait for some of your requests to play and try again.")
                            self.messages.append(message)

                        self.dump_queue()
                    else:
                        message = await self.bot.send_message(args["message"].channel,
                                                    ":no_entry_sign: Song from {} failed to be added to queue. Please use a different upload of the song.".format(item))
                        self.messages.append(message)
            except:
                traceback.print_exc(5)

    async def command_song(self, args):
        await self.bot.send_message(self.text_channel, ":speaker: Now playing {}, requested by {}.".format(self.song["info"]["title"], self.song["requester"]))
