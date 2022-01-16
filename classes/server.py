"""Class to handle configuration and accessing of discord objects"""

from functools import cached_property
from typing import Dict, Optional

import discord

from classes.exceptions import (ChannelLookupException, GuildLookupException,
                                RoleLookupException)


class Server:
    """Class to handle configuration and accessing of discord objects"""

    def __init__(self, config: Dict, client: discord.Client):
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
                config['id'].get('voice_channel')
            self.text_channel_id: Optional[int] = \
                config['id'].get('text_channel')
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
                                         f'{self.text_channel_id} could not be found by client')
        return text_channel
