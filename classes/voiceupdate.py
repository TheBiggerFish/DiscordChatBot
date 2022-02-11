"""Class to handle discord voice state updates"""

from typing import Optional

import discord


class VoiceStateUpdate:
    """Class to handle discord voice state updates"""

    def __init__(self, before: discord.VoiceState, after: discord.VoiceState):
        if not isinstance(before.channel, discord.VoiceChannel) and \
                not isinstance(after.channel, discord.VoiceChannel):
            raise TypeError('VoiceStateUpdate constructor requires '
                            'discord.VoiceState type')
        self.before = before
        self.after = after

    @property
    def before_channel(self) -> Optional[int]:
        """Property representing the channel id of before"""
        if self.before.channel:
            return self.before.channel.id
        return None

    @property
    def after_channel(self) -> Optional[int]:
        """Property representing the channel id of after"""
        if self.after.channel:
            return self.after.channel.id
        return None

    @property
    def guild(self) -> Optional[discord.Guild]:
        """Property representing the guild in which the update takes place"""
        if self.before_channel is not None:
            return self.before.channel.guild
        if self.after_channel is not None:
            return self.after.channel.guild
        return None

    def is_join(self) -> bool:
        """Predicate function to check if voice state change is channel join"""
        return self.after.channel is not None and \
            (self.before.channel is None or
             self.before.channel.id != self.after.channel.id)

    def is_leave(self) -> bool:
        """Predicate function to check if voice state change is channel leave"""
        return self.before.channel is not None and \
            (self.after.channel is None or self.before.channel.id != self.after.channel.id)

    def is_move(self) -> bool:
        """Predicate function to check if voice state change is channel leave"""
        return self.before.channel is not None and self.after.channel is not None and \
            self.before.channel.id != self.after.channel.id
