from discord import Member

from .Permission import Permission

__author__ = 'Riley Flynn (nint8835)'


class Owner(Permission):
    def __init__(self, bot_instance):
        self.bot = bot_instance

    def has_permission(self, member: Member):
        return member.id == self.bot.config["owner_id"]
