"""Class to handle configuration and accessing of discord objects"""

from datetime import datetime
from functools import cached_property
from typing import Dict, Optional

import discord
from dateutil.relativedelta import relativedelta

from classes.exceptions import (ChannelLookupException, GuildLookupException,
                                RoleLookupException)


class ChatChannel:
    """Class to handle configuration of a single set of channels"""

    def __init__(self, voice: Optional[int], text: Optional[int], role: Optional[int]):
        self.voice = voice
        self.text = text
        self.role_id = role

    async def clear_chat(self, client: discord.Client) -> None:
        """Clear all chat in text channel"""
        text_channel = self.text_channel(client)
        if not await text_channel.history(limit=1).flatten():
            return
        two_weeks_ago = datetime.now() - relativedelta(weeks=2)
        while messages := await text_channel.history(after=two_weeks_ago).flatten():
            await text_channel.delete_messages(messages)

    def validate(self, client: discord.Client, guild: discord.Guild) -> bool:
        """Verify that the ChatChannel object can use each channel and the role"""
        try:
            _ = self.role(guild)
            _ = self.text_channel(client)
            _ = self.voice_channel(client)
        except (RoleLookupException, ChannelLookupException):
            return False
        else:
            return True

    def role(self, guild: discord.Guild) -> discord.Role:
        """Lookup and return role if found"""
        role = guild.get_role(self.role_id)
        if not isinstance(role, discord.Role):
            raise RoleLookupException(f'Discord guild role {{{self.role_id}}} '
                                      'could not be found by client in guild'
                                      f'{{{guild.id}}}')
        return role

    def text_channel(self, client: discord.Client) -> discord.TextChannel:
        """Lookup and return text channel if found"""
        text_channel = client.get_channel(self.text)
        if not isinstance(text_channel, discord.TextChannel):
            raise ChannelLookupException(f'Discord text channel {{{text_channel}}}'
                                         'could not be found by client')
        return text_channel

    def voice_channel(self, client: discord.Client) -> discord.VoiceChannel:
        """Lookup and return voice channel if found"""
        voice_channel = client.get_channel(self.voice)
        if not isinstance(voice_channel, discord.VoiceChannel):
            raise ChannelLookupException(f'Discord voice channel {{{voice_channel}}}'
                                         'could not be found by client')
        return voice_channel


class Server:
    """Class to handle configuration and accessing of discord objects"""

    def __init__(self, config: Dict, client: discord.Client):
        self.server_id: Optional[int] = None
        self.chat_channels: Dict[int, ChatChannel] = {}
        self._default_role: Optional[int] = None
        self._default_text: Optional[int] = None
        self._clear_chat: Optional[bool] = True

        self._read_config(config)
        self.client = client

    def __str__(self):
        return self.name

    def _read_config(self, config: Dict):
        self.name: str = config.get('name', 'unknown')

        if 'config' in config and isinstance(config['config'], dict):
            self._clear_chat: bool = config['config'].get('clear_chat', True)

        ids = config['id']
        if 'id' in config and isinstance(ids, dict):
            self.server_id: Optional[int] = ids.get('server')

            if 'default' in ids and isinstance(ids['default'], dict):
                self._default_role = ids['default'].get('role')
                self._default_text = ids['default'].get('text')

            if 'channels' in ids and isinstance(ids['channels'], list):
                for chat_channel in ids['channels']:
                    chat_channel: Dict[str, int]

                    voice_channel_id: Optional[int] = \
                        chat_channel.get('voice')
                    text_channel_id: Optional[int] = \
                        chat_channel.get('text', self._default_text)
                    role_id: Optional[int] = \
                        chat_channel.get('role', self._default_role)

                    if voice_channel_id and text_channel_id and role_id:
                        self.chat_channels[voice_channel_id] = ChatChannel(
                            voice_channel_id, text_channel_id, role_id)

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

    def validate_chat_channels(self) -> int:
        """
        Validate chat_channels for server, removing invalid chat_channels.
        Returns updated length of chat_channels list
        """

        for voice_id, chat_channel in self.chat_channels.items():
            if not chat_channel.validate(self.client, self.guild):
                del self.chat_channels[voice_id]

        return len(self.chat_channels)
