import discord
import asyncio
from .EventManager import EventManager
from .PluginLoader import PluginLoader
from .Enums import EventTypes
__author__ = 'Riley Flynn (nint8835)'


class Bot(discord.Client):

    def __init__(self, config: dict, loop: asyncio.BaseEventLoop=None):
        super(Bot, self).__init__(loop=loop)
        self._config = config
        self._EventManager = EventManager(self)
        self._EventManager.register_handler(EventTypes.Message, self.log_message)
        self._PluginLoader = PluginLoader(self)
        self._PluginLoader.load_plugins()
        self.run(config["email"], config["password"])

    def register_handler(self, eventtype: EventTypes, handler):
        self._EventManager.register_handler(eventtype, handler)

    @asyncio.coroutine
    def on_message(self, message: discord.Message):
        self._EventManager.dispatch_event(EventTypes.Message,
                                       message = message,
                                       author = message.author,
                                       channel = message.channel)
        if message.channel.is_private:
            self._EventManager.dispatch_event(EventTypes.PrivateMessage,
                                           message = message,
                                           author = message.author,
                                           channel = message.channel)
        else:
            self._EventManager.dispatch_event(EventTypes.ChannelMessage,
                                           message = message,
                                           author = message.author,
                                           channel = message.channel)

    @asyncio.coroutine
    def on_message_delete(self, message):
        self._EventManager.dispatch_event(EventTypes.MessageDeleted,
                                       message = message,
                                       author = message.author,
                                       channel = message.channel)

        if message.channel.is_private:
            self._EventManager.dispatch_event(EventTypes.PrivateMessageDeleted,
                                           message = message,
                                           author = message.author,
                                           channel = message.channel)

        else:
            self._EventManager.dispatch_event(EventTypes.ChannelMessageDeleted,
                                           message = message,
                                           author = message.author,
                                           channel = message.channel)

    @asyncio.coroutine
    def on_message_edit(self, before, after):
        self._EventManager.dispatch_event(EventTypes.MessageEdited,
                                       message_before = before,
                                       message_after = after,
                                       author = after.author,
                                       channel = after.channel)

        if after.channel.is_private:
            self._EventManager.dispatch_event(EventTypes.PrivateMessageEdited,
                                           message_before = before,
                                           message_after = after,
                                           author = after.author,
                                           channel = after.channel)

        else:
            self._EventManager.dispatch_event(EventTypes.PrivateMessageEdited,
                                           message_before = before,
                                           message_after = after,
                                           author = after.author,
                                           channel = after.channel)

    @asyncio.coroutine
    def on_channel_delete(self, channel):
        self._EventManager.dispatch_event(EventTypes.ChannelDeleted,
                                       channel = channel,
                                       server = channel.server)

    @asyncio.coroutine
    def on_channel_create(self, channel):
        self._EventManager.dispatch_event(EventTypes.ChannelCreated,
                                       channel = channel,
                                       server = channel.server)

    @asyncio.coroutine
    def on_channel_update(self, before, after):
        self._EventManager.dispatch_event(EventTypes.ChannelUpdated,
                                       channel_before = before,
                                       channel_after = after,
                                       server = after.server)

    @asyncio.coroutine
    def on_member_join(self, member):
        self._EventManager.dispatch_event(EventTypes.MemberJoined,
                                       member = member,
                                       server = member.server)

    @asyncio.coroutine
    def on_member_left(self, member):
        self._EventManager.dispatch_event(EventTypes.MemberLeft,
                                       member = member,
                                       server = member.server)

    @asyncio.coroutine
    def on_member_update(self, before, after):
        self._EventManager.dispatch_event(EventTypes.MemberUpdated,
                                       member_before = before,
                                       member_after = after,
                                       server = after.server)

    @asyncio.coroutine
    def on_member_ban(self, member):
        self._EventManager.dispatch_event(EventTypes.MemberBanned,
                                       member = member,
                                       server = member.server)

    @asyncio.coroutine
    def on_member_unbanned(self, server, user):
        self._EventManager.dispatch_event(EventTypes.MemberUnbanned,
                                       server = server,
                                       user = user)

    @asyncio.coroutine
    def on_voice_status_update(self, before, after):
        self._EventManager.dispatch_event(EventTypes.MemberVoiceStateUpdated,
                                       member_before = before,
                                       member_after = after)

    @asyncio.coroutine
    def on_typing(self, channel, user, when):
        self._EventManager.dispatch_event(EventTypes.MemberTyping,
                                       channel = channel,
                                       user = user,
                                       when = when)

    @asyncio.coroutine
    def on_server_join(self, server):
        self._EventManager.dispatch_event(EventTypes.ServerJoined,
                                       server = server)

    @asyncio.coroutine
    def on_server_remove(self, server):
        self._EventManager.dispatch_event(EventTypes.ServerLeft,
                                       server = server)

    @asyncio.coroutine
    def on_server_update(self, before, after):
        self._EventManager.dispatch_event(EventTypes.ServerUpdated,
                                       server_before = before,
                                       server_after = after)

    @asyncio.coroutine
    def on_server_available(self, server):
        self._EventManager.dispatch_event(EventTypes.ServerAvailable,
                                       server = server)

    @asyncio.coroutine
    def on_server_unavailable(self, server):
        self._EventManager.dispatch_event(EventTypes.ServerUnavailable,
                                       server = server)

    @asyncio.coroutine
    def on_server_role_create(self, server, role):
        self._EventManager.dispatch_event(EventTypes.ServerRoleCreated,
                                       server = server,
                                       role = role)

    @asyncio.coroutine
    def on_server_role_delete(self, server, role):
        self._EventManager.dispatch_event(EventTypes.ServerRoleDeleted,
                                       server = server,
                                       role = role)

    @asyncio.coroutine
    def on_server_role_update(self, before, after):
        self._EventManager.dispatch_event(EventTypes.ServerRoleUpdated,
                                       role_before = before,
                                       role_after = after,
                                       server = [server for server in self.servers if after in server.roles][0])

    @asyncio.coroutine
    def on_ready(self):
        self._EventManager.dispatch_event(EventTypes.OnReady)

    @asyncio.coroutine
    def log_message(self, args):
        print("{}: {}".format(args["author"].name, args["message"].content))
