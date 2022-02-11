"""
This discord bot can be used to add a role to server members when
they join a specific voice channel. This can be used to create a
text channel that can be used for posting without bothering members
not in the call.
"""

import os
import socket
import time
from typing import Dict

import discord
import yaml
from dotenv import load_dotenv

from classes import Logger, Server
from classes.exceptions import (ChannelLookupException, GuildLookupException,
                                RoleLookupException)
from classes.voiceupdate import VoiceStateUpdate

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
            _ = server.role
            _ = server.text_channel
        except (GuildLookupException, RoleLookupException,
                ChannelLookupException) as exc:
            logger.error(str(exc))
            del servers[server.server_id]
            logger.warning('Server {%d} removed from servers list. '
                           'Now serving (%d) servers', server.server_id, len(servers))
        else:
            logger.info('{%s} is connected to "%s"', client.user, server.name)


@client.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState,
                                after: discord.VoiceState):
    """Perform role updating for voice_state_update events"""

    update = VoiceStateUpdate(before, after)

    before_channel = update.before_channel
    before_server = servers.get(before_channel)

    after_channel = update.after_channel
    after_server = servers.get(after_channel)

    if before_server is None and after_server is None:
        logger.debug('Received voice_state_update for non-configured '
                     'channel update {%s} -> {%s}',
                     str(before_channel), str(after_channel))
        return

    logger.debug('Assessing voice_state_update for user {%s} in guild {%d} with update '
                 '{%s} -> {%s}', str(member), update.guild.id,
                 str(before_channel), str(after_channel))

    if update.is_move() and \
            before_server.voice_channel_id in servers and \
            after_server.voice_channel_id in servers:
        logger.debug('User {%s} has left voice channel {%s} and moved to '
                     'voice channel {%s} in guild {%s}',
                     member.display_name, before.channel.name,
                     after.channel.name, update.guild.name)
        if before_server.text_channel_id == after_server.text_channel_id:
            await before_server.user_left(member, block_clear=True)
            await after_server.user_joined(member)
    elif update.is_leave():
        logger.debug('User {%s} has left voice channel {%s} in guild {%s}',
                     member.display_name, before.channel.name, update.guild.name)
        if await before_server.user_left(member):
            logger.info('Deleting messages from empty chat channel {%s}',
                        before_server.text_channel_id)
    elif update.is_join():
        logger.debug('User {%s} has joined voice channel {%s} in guild {%s}',
                     member.display_name, after.channel.name, update.guild.name)
        await after_server.user_joined(member)


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
        if server.has_empty_id():
            logger.error('Missing required ID value(s) for server "%s": %s',
                         server.name, str(server_config['id']))
            continue
        logger.info('ID values configured for server "%s": %s',
                    server.name, str(server_config['id']))
        servers[server.voice_channel_id] = server

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
