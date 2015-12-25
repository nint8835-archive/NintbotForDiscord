import discord
import asyncio
import NintbotForDiscord.EventManager
from .PluginLoader import PluginLoader
from .Enums import EventTypes

__author__ = 'Riley Flynn (nint8835)'


class Bot(discord.Client):
    def __init__(self, config: dict, loop: asyncio.BaseEventLoop = None):
        super(Bot, self).__init__(loop = loop)
        self._config = config

        self._PluginLoader = PluginLoader(self)
        self._PluginLoader.load_plugins()
        print(NintbotForDiscord.EventManager.handlers)
        self.run(config["email"], config["password"])

    def register_handler(self, eventtype: EventTypes, handler):
        NintbotForDiscord.EventManager.register_handler(eventtype, handler)

    @asyncio.coroutine
    def on_message(self, message: discord.Message):
        NintbotForDiscord.EventManager.dispatch_event(EventTypes.Message,
                                                      message = message,
                                                      author = message.author,
                                                      channel = message.channel)
        if message.channel.is_private:
            NintbotForDiscord.EventManager.dispatch_event(EventTypes.PrivateMessage,
                                                          message = message,
                                                          author = message.author,
                                                          channel = message.channel)
        else:
            NintbotForDiscord.EventManager.dispatch_event(EventTypes.ChannelMessage,
                                                          message = message,
                                                          author = message.author,
                                                          channel = message.channel)

    @asyncio.coroutine
    def on_message_delete(self, message):
        NintbotForDiscord.EventManager.dispatch_event(EventTypes.MessageDeleted,
                                                      message = message,
                                                      author = message.author,
                                                      channel = message.channel)

        if message.channel.is_private:
            NintbotForDiscord.EventManager.dispatch_event(EventTypes.PrivateMessageDeleted,
                                                          message = message,
                                                          author = message.author,
                                                          channel = message.channel)

        else:
            NintbotForDiscord.EventManager.dispatch_event(EventTypes.ChannelMessageDeleted,
                                                          message = message,
                                                          author = message.author,
                                                          channel = message.channel)

    @asyncio.coroutine
    def on_message_edit(self, before, after):
        NintbotForDiscord.EventManager.dispatch_event(EventTypes.MessageEdited,
                                                      message_before = before,
                                                      message_after = after,
                                                      author = after.author,
                                                      channel = after.channel)

        if after.channel.is_private:
            NintbotForDiscord.EventManager.dispatch_event(EventTypes.PrivateMessageEdited,
                                                          message_before = before,
                                                          message_after = after,
                                                          author = after.author,
                                                          channel = after.channel)

        else:
            NintbotForDiscord.EventManager.dispatch_event(EventTypes.PrivateMessageEdited,
                                                          message_before = before,
                                                          message_after = after,
                                                          author = after.author,
                                                          channel = after.channel)

    @asyncio.coroutine
    def on_channel_delete(self, channel):
        NintbotForDiscord.EventManager.dispatch_event(EventTypes.ChannelDeleted,
                                                      channel = channel,
                                                      server = channel.server)

    @asyncio.coroutine
    def on_channel_create(self, channel):
        NintbotForDiscord.EventManager.dispatch_event(EventTypes.ChannelCreated,
                                                      channel = channel,
                                                      server = channel.server)

    @asyncio.coroutine
    def on_channel_update(self, before, after):
        NintbotForDiscord.EventManager.dispatch_event(EventTypes.ChannelUpdated,
                                                      channel_before = before,
                                                      channel_after = after,
                                                      server = after.server)

    @asyncio.coroutine
    def on_member_join(self, member):
        NintbotForDiscord.EventManager.dispatch_event(EventTypes.MemberJoined,
                                                      member = member,
                                                      server = member.server)

    @asyncio.coroutine
    def on_member_left(self, member):
        NintbotForDiscord.EventManager.dispatch_event(EventTypes.MemberLeft,
                                                      member = member,
                                                      server = member.server)

    @asyncio.coroutine
    def on_member_update(self, before, after):
        NintbotForDiscord.EventManager.dispatch_event(EventTypes.MemberUpdated,
                                                      member_before = before,
                                                      member_after = after,
                                                      server = after.server)

    @asyncio.coroutine
    def on_member_ban(self, member):
        NintbotForDiscord.EventManager.dispatch_event(EventTypes.MemberBanned,
                                                      member = member,
                                                      server = member.server)

    @asyncio.coroutine
    def on_member_unbanned(self, server, user):
        NintbotForDiscord.EventManager.dispatch_event(EventTypes.MemberUnbanned,
                                                      server = server,
                                                      user = user)

    @asyncio.coroutine
    def on_voice_status_update(self, before, after):
        NintbotForDiscord.EventManager.dispatch_event(EventTypes.MemberVoiceStateUpdated,
                                                      member_before = before,
                                                      member_after = after)

    @asyncio.coroutine
    def on_typing(self, channel, user, when):
        NintbotForDiscord.EventManager.dispatch_event(EventTypes.MemberTyping,
                                                      channel = channel,
                                                      user = user,
                                                      when = when)

    @asyncio.coroutine
    def on_server_join(self, server):
        NintbotForDiscord.EventManager.dispatch_event(EventTypes.ServerJoined,
                                                      server = server)

    @asyncio.coroutine
    def on_server_remove(self, server):
        NintbotForDiscord.EventManager.dispatch_event(EventTypes.ServerLeft,
                                                      server = server)

    @asyncio.coroutine
    def on_server_update(self, before, after):
        NintbotForDiscord.EventManager.dispatch_event(EventTypes.ServerUpdated,
                                                      server_before = before,
                                                      server_after = after)

    @asyncio.coroutine
    def on_server_available(self, server):
        NintbotForDiscord.EventManager.dispatch_event(EventTypes.ServerAvailable,
                                                      server = server)

    @asyncio.coroutine
    def on_server_unavailable(self, server):
        NintbotForDiscord.EventManager.dispatch_event(EventTypes.ServerUnavailable,
                                                      server = server)

    @asyncio.coroutine
    def on_server_role_create(self, server, role):
        NintbotForDiscord.EventManager.dispatch_event(EventTypes.ServerRoleCreated,
                                                      server = server,
                                                      role = role)

    @asyncio.coroutine
    def on_server_role_delete(self, server, role):
        NintbotForDiscord.EventManager.dispatch_event(EventTypes.ServerRoleDeleted,
                                                      server = server,
                                                      role = role)

    @asyncio.coroutine
    def on_server_role_update(self, before, after):
        NintbotForDiscord.EventManager.dispatch_event(EventTypes.ServerRoleUpdated,
                                                      role_before = before,
                                                      role_after = after,
                                                      server =
                                                      [server for server in self.servers if after in server.roles][0])

    @asyncio.coroutine
    def on_ready(self):
        NintbotForDiscord.EventManager.dispatch_event(EventTypes.OnReady)

    @asyncio.coroutine
    @NintbotForDiscord.EventManager.event_handler(EventTypes.Message)
    def log_message(self, args):
        print("{}: {}".format(args["author"].name, args["message"].content))
