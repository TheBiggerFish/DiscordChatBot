"""Exceptions to be used in discord object lookup"""

from discord import DiscordException


class GuildLookupException(DiscordException):
    """Caught to handle exceptions from discord.Client.get_guild()"""

class RoleLookupException(DiscordException):
    """Caught to handle exceptions from discord.guild.get_role()"""

class ChannelLookupException(DiscordException):
    """Caught to handle exceptions from discord.Client.get_channel()"""
