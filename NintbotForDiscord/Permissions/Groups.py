from .Permission import PermissionGroup
from .General import *
from .Text import *
from .Voice import *

__author__ = 'Riley Flynn (nint8835)'


class All(PermissionGroup):
    permissions = [ManageServer(),
                   ManageRoles(),
                   ManageChannels(),
                   KickMembers(),
                   BanMembers(),
                   CreateInstantInvite(),
                   ReadMessages(),
                   SendMessages(),
                   SendTTSMessages(),
                   ManageMessages(),
                   EmbedLinks(),
                   AttachFiles(),
                   ReadMessageHistory(),
                   MentionEveryone(),
                   Connect(),
                   Speak(),
                   MuteMembers(),
                   DeafenMembers(),
                   MoveMembers(),
                   UseVoiceActivity()]


class Default(PermissionGroup):
    permissions = [CreateInstantInvite(),
                   ReadMessages(),
                   SendMessages(),
                   SendTTSMessages(),
                   EmbedLinks(),
                   AttachFiles(),
                   ReadMessageHistory(),
                   MentionEveryone(),
                   Connect(),
                   Speak(),
                   UseVoiceActivity()]
