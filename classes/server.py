"""Class to handle configuration and accessing of discord objects"""

from datetime import datetime
from functools import cached_property
from typing import Dict, Optional

import discord
from dateutil.relativedelta import relativedelta

from classes.exceptions import (ChannelLookupException, GuildLookupException,
                                RoleLookupException)


class Server:
    """Class to handle configuration and accessing of discord objects"""

    def __init__(self, config: Dict, client: discord.Client):
        self.name: Optional[str] = None
        self.server_id: Optional[int] = None
        self.voice_channel_id: Optional[int] = None
        self.text_channel_id: Optional[int] = None
        self.role_id: Optional[int] = None
        self._clear_chat: bool = True
        self._read_config(config)
        self.client = client

    def __str__(self):
        return self.name

    def _read_config(self, config: Dict):
        self.name: str = config.get('name', 'unknown')

        if 'config' in config and isinstance(config['config'], dict):
            self._clear_chat: bool = config['config'].get('clear_chat', True)
        else:
            self._clear_chat: bool = True

        if 'id' in config and isinstance(config['id'], dict):
            self.server_id: Optional[int] = config['id'].get('server')
            self.voice_channel_id: Optional[int] = \
                config['id'].get('voice')
            self.text_channel_id: Optional[int] = \
                config['id'].get('text')
            self.role_id: Optional[int] = config['id'].get('role')

    def has_empty_id(self) -> bool:
        """Predicate method to validate presence of required IDs"""
        return None in {self.server_id, self.voice_channel_id,
                        self.text_channel_id, self.role_id}

    @property
    def clear_chat(self) -> bool:
        """Return value of _clear_chat"""
        return self._clear_chat

    @cached_property
    def guild(self) -> discord.Guild:
        """Lookup and return guild if found"""
        guild = self.client.get_guild(self.server_id)
        if not isinstance(guild, discord.Guild):
            raise GuildLookupException(f'Discord guild {{{self.server_id}}} '
                                       'could not be found by client')
        return guild

    @cached_property
    def role(self) -> discord.Role:
        """Lookup and return role if found"""
        role = self.guild.get_role(self.role_id)
        if not isinstance(role, discord.Role):
            raise RoleLookupException(f'Discord guild role {{{self.role_id}}} '
                                      'could not be found by client')
        return role

    @cached_property
    def text_channel(self) -> discord.TextChannel:
        """Lookup and return text_channel if found"""
        text_channel = self.client.get_channel(self.text_channel_id)
        if not isinstance(text_channel, discord.TextChannel):
            raise ChannelLookupException('Discord text channel '
                                         f'{{{self.text_channel_id}}} '
                                         'could not be found by client')
        return text_channel

    @cached_property
    def voice_channel(self) -> discord.VoiceChannel:
        """Lookup and return voice_channel if found"""
        voice_channel = self.client.get_channel(self.voice_channel_id)
        if not isinstance(voice_channel, discord.VoiceChannel):
            raise ChannelLookupException('Discord voice channel '
                                         f'{{{self.voice_channel_id}}} '
                                         'could not be found by client')
        return voice_channel

    async def _do_clear_chat(self):
        """Clear all chat in server's text channel"""

        if not await self.text_channel.history(limit=1).flatten():
            return
        date_time = datetime.now() - relativedelta(weeks=2)
        while messages := await self.text_channel.history(after=date_time).flatten():
            await self.text_channel.delete_messages(messages)

    async def user_left(self, member: discord.Member, block_clear: bool = False) -> bool:
        """Remove role from user that leaves, clear channel if empty, return true if cleared"""
        await member.remove_roles(self.role)

        if self.clear_chat and not block_clear:
            if len(self.voice_channel.voice_states.keys()) == 0:
                await self._do_clear_chat()
                return True
        return False

    async def user_joined(self, member: discord.Member):
        """Add role to new user"""
        await member.add_roles(self.role)
