from enum import Enum
__author__ = 'Riley Flynn (nint8835)'


class EventTypes(Enum):

    # Messages - Sent
    ChannelMessage = "channel_message"
    PrivateMessage = "private_message"
    Message        = "message"

    # Messages - Edited/Deleted
    MessageDeleted        = "message_deleted"
    MessageEdited         = "message_edited"
    ChannelMessageDeleted = "channel_message_deleted"
    ChannelMessageEdited  = "channel_message_edited"
    PrivateMessageDeleted = "private_message_deleted"
    PrivateMessageEdited  = "private_message_edited"

    # Channels
    ChannelDeleted = "channel_deleted"
    ChannelCreated = "channel_created"
    ChannelUpdated = "channel_updated"

    # Members
    MemberJoined            = "member_joined"
    MemberLeft              = "member_left"
    MemberUpdated           = "member_updated"
    MemberBanned            = "member_banned"
    MemberUnbanned          = "member_unbanned"
    MemberVoiceStateUpdated = "member_voice_state_updated"
    MemberTyping            = "member_typing"

    # Servers
    ServerJoined      = "server_joined"
    ServerLeft        = "server_left"
    ServerUpdated     = "server_updated"
    ServerAvailable   = "server_available"
    ServerUnavailable = "server_unavailable"
    ServerRoleCreated = "server_role_created"
    ServerRoleDeleted = "server_role_deleted"
    ServerRoleUpdated = "server_role_updated"

    # Client Status
    OnReady = "on_ready"
