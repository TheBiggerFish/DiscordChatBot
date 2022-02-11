"""
This discord bot can be used to add a role to server members when
they join a specific voice channel. This can be used to create a
text channel that can be used for posting without bothering members
not in the call.
"""

import os
import socket
import time
from datetime import datetime
from typing import Dict, Optional

import discord
import yaml
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

from classes import Logger, Server
from classes.exceptions import (ChannelLookupException, GuildLookupException,
                                RoleLookupException)

client = discord.Client()
logger: Logger = None
servers: Dict[int, Server] = {}

load_dotenv()
LOGGING_HOST = os.getenv('LOGGING_HOST')
LOGGING_PORT = os.getenv('LOGGING_PORT')
LOGGING_NAME = os.getenv('LOGGING_NAME')
LOGGING_LEVEL = os.getenv('LOGGING_LEVEL')

logger = Logger(LOGGING_NAME, LOGGING_HOST,
                LOGGING_PORT, LOGGING_LEVEL)
logger.debug('Logger configured: {{"name":%s,"level":%s,"host":%s,"port":%d}}',
             LOGGING_HOST, LOGGING_LEVEL, LOGGING_HOST, LOGGING_PORT)


@client.event
async def on_ready():
    """Called by discord upon bot ready state, validate IDs"""

    logger.debug('Client ready. Iterating servers')
    for _, server in servers.items():
        try:
            _ = server.guild
        except GuildLookupException as exc:
            logger.error(str(exc))
            del servers[server.server_id]
            logger.warning('Server {%d} removed from servers list for GuildLookupException. '
                           'Now serving (%d) servers', server.server_id, len(servers))
        else:
            logger.info('{%s} is connected to "%s"', client.user, server.name)

            if server.validate_chat_channels() == 0:
                del servers[server.server_id]
                logger.warning('Server {%d} removed from servers for lack of channels. '
                               'Now serving (%d) servers', server.server_id, len(servers))


def is_join(before: Optional[discord.VoiceState],
            after: Optional[discord.VoiceState]) -> bool:
    """Predicate function to check if voice state change is channel join"""
    return after.channel is not None and \
        (before.channel is None or before.channel.id != after.channel.id)


def is_leave(before: Optional[discord.VoiceState],
             after: Optional[discord.VoiceState]) -> bool:
    """Predicate function to check if voice state change is channel leave"""
    return before.channel is not None and \
        (after.channel is None or before.channel.id != after.channel.id)


@client.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState,
                                after: discord.VoiceState):
    """Perform role updating for voice_state_update events"""

    if not isinstance(before.channel, discord.VoiceChannel) and \
            not isinstance(after.channel, discord.VoiceChannel):
        logger.error('Channel type error in voice_state_update event: '
                     '{before:%s,after:%s}', type(before.channel), type(after.channel))
        return

    if before.channel is not None:
        guild_id: int = before.channel.guild.id
    elif after.channel is not None:
        guild_id: int = after.channel.guild.id

    server = servers.get(guild_id)
    if server is None:
        logger.warning('Received voice_state_update for non-configured guild {%d}',
                       guild_id)
        return

    logger.debug('Assessing voice_state_update on guild {%d}', guild_id)
    if is_leave(before, after) and before.channel.id in server.chat_channels:
        logger.debug('User {%s} has left voice channel {%s}',
                     member.display_name, before.channel.name)
        await member.remove_roles(server.chat_channels[before.channel.id].role_id)
        if server.clear_chat:
            if len(before.channel.voice_states.keys()) == 0:
                await server.chat_channels[before.channel.id].clear_chat(server.client)
    if is_join(before, after) and after.channel.id in server.chat_channels:
        logger.debug('User {%s} has joined voice channel {%s}',
                     member.display_name, after.channel.name)
        await member.add_roles(server.chat_channels[after.channel.id].role_id)
    else:
        logger.debug('voice_state_update event in guild {%d} is '
                     'neither join nor leave', guild_id)


def connected() -> bool:
    """Predicate function to check if server has connected to network"""

    try:
        logger.debug('Checking network connection')
        socket.create_connection(('8.8.8.8', 53)).close()
        return True
    except socket.error as err:
        logger.error('Error connecting to network: %s', str(err))
        return False


def main():
    """Main entry point for program, handles discord server configuration"""

    while not connected():
        logger.error('Failed to connect, waiting 60 seconds')
        time.sleep(60)
    logger.debug('Successfully connected to network')

    try:
        config_path = os.getenv('CONFIG_PATH')
        logger.debug('Opening configuration file: %s', config_path)
        if config_path is None:
            logger.critical('CONFIG_PATH environment variable not defined')
            return
        with open(config_path, encoding='UTF-8') as config_file:
            config = yaml.safe_load(config_file)
    except IOError as err:
        logger.critical('Error opening configuration file: %s', str(err))
        return

    for server_config in config['chatbot']['servers']:
        server = Server(server_config, client)
        if server.server_id is None:
            logger.error('Missing required ID value(s) for server "%s": %s',
                         server.name, str(server_config['id']))
            continue
        logger.info('Server ID value configured for server "%s": %s',
                    server.name, str(server_config['id']))
        servers[server.server_id] = server

    token = os.getenv('DISCORD_TOKEN')
    if token is not None:
        logger.debug('DISCORD_TOKEN found, running client')
        client.run(token)
        logger.info('Client closed by keyboard interrupt')
    else:
        logger.error('DISCORD_TOKEN environment variable not defined')
        return


if __name__ == '__main__':
    main()
