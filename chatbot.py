import os
import logging
import logging.handlers
import time
import socket
from typing import Dict
from datetime import datetime


import yaml
import discord

from dotenv import load_dotenv
from dateutil.relativedelta import relativedelta

from classes.server import Server
from classes.exceptions import ChannelLookupException,RoleLookupException,GuildLookupException


client = discord.Client()
logger:logging.Logger = None
servers:Dict[str,Server] = {}


def configure_logging(name:str, level:str, host:str, port:int) -> logging.Logger:
    """Perform formatting and handling configuration and return logging.Logger"""
    logger_ = logging.Logger(name)
    handler = logging.handlers.SysLogHandler(address=(host,port))
    formatter = logging.Formatter(fmt=f'{socket.gethostname()} '\
        '[%(levelname)s] %(process)s {%(name)s} %(message)s')
    handler.setFormatter(formatter)
    logger_.addHandler(handler)
    logger_.setLevel(level)
    return logger_



load_dotenv()
with open(os.getenv('CONFIG_PATH'),encoding='UTF-8') as config_file:
    config = yaml.safe_load(config_file)
TOKEN = os.getenv('DISCORD_TOKEN')
LOGGING_HOST = os.getenv('LOGGING_HOST')
LOGGING_PORT = int(os.getenv('LOGGING_PORT'))
LOGGING_NAME = config['chatbot']['logging']['logger_name']
LOGGING_LEVEL = config['chatbot']['logging']['log_level']
logger = configure_logging(LOGGING_NAME,LOGGING_LEVEL,
                            LOGGING_HOST,LOGGING_PORT)


@client.event
async def on_ready():
    """Called by discord upon bot ready state, validate IDs"""

    for _,server in servers.items():
        try:
            _ = server.guild
            _ = server.role
            _ = server.text_channel
        except (GuildLookupException,RoleLookupException,
                ChannelLookupException) as exc:
            logger.error(str(exc))
            del servers[server.server_id]
            logger.info('Server {%d} removed from servers list. '\
                'Now serving (%d) servers',server.server_id,len(servers))
        else:
            logger.info('{%s} is connected to "%s"',client.user,server.name)


def is_join(before:discord.VoiceState,after:discord.VoiceState) -> bool:
    """Predicate function to check if voice state change is channel join"""
    return before.channel is None and after.channel is not None


def is_leave(before:discord.VoiceState,after:discord.VoiceState) -> bool:
    """Predicate function to check if voice state change is channel leave"""
    return before.channel is not None and after.channel is None


async def clear_chat(server:Server):
    """Clear all chat in server's text channel"""

    logger.info('Checking text channel for message deletion')
    if not await server.text_channel.history(limit=1).flatten():
        logger.info('No messages to delete from empty chat channel')
        return

    logger.info('Deleting messages from empty chat channel')
    date_time = datetime.now() - relativedelta(weeks=2)
    while messages := await server.text_channel.history(after=date_time).flatten():
        logger.debug('Deleting %d messages from text_channel {%d}',
                     len(messages),server.text_channel_id)
        await server.text_channel.delete_messages(messages)

    logger.info('All messages deleted')


@client.event
async def on_voice_state_update(member:discord.Member, before:discord.VoiceState,
                                after:discord.VoiceState):
    """Perform role updating for voice_state_update events"""

    if not isinstance(before.channel,discord.VoiceChannel) and \
            not isinstance(after.channel,discord.VoiceChannel):
        logger.error('Channel type error in voice_state_update event: '\
                     '{before:%s,after:%s}',type(before.channel),type(after.channel))
        return

    if before.channel is not None:
        guild_id:int = before.channel.guild.id
    elif after.channel is not None:
        guild_id:int = after.channel.guild.id
    else:
        logger.warning('Channel not defined in voice_state_update event')
        return

    server = servers.get(guild_id)
    if server is None:
        logger.warning('Received voice_state_update for non-configured channel {%d}',guild_id)
        return
    logger.debug('Assessing voice_state_update on guild {%d}',guild_id)

    if is_join(before,after) and after.channel.id==server.voice_channel_id:
        logger.info('User {%s} has joined voice channel {%s}',
                    member.display_name,after.channel.name)
        await member.add_roles(server.role)
    elif is_leave(before,after) and before.channel.id==server.voice_channel_id:
        logger.info('User {%s} has left voice channel {%s}',
                    member.display_name,before.channel.name)
        await member.remove_roles(server.role)
        if server.clear_chat:
            if len(before.channel.voice_states.keys()) == 0:
                await clear_chat(server)
    else:
        logger.debug('voice_state_update event in guild {%d} is '\
            'neither join nor leave', guild_id)


def connected() -> bool:
    """Predicate function to check if server has connected to internet"""
    try:
        socket.create_connection(("8.8.8.8", 53))
        return True
    except socket.error as err:
        logger.error("Error connecting to internet: %s", str(err))
        return False


def main():
    """Main entry point for program, handles discord server configuration"""
    while not connected():
        logger.error("Failed to connect, waiting 60 seconds")
        time.sleep(60)

    for server_config in config['chatbot']['servers']:
        server = Server(server_config,client)
        if server.has_empty_id():
            logger.error('Missing required ID value(s) for server "%s": %s',
                        server.name, str(server_config["id"]))
            continue
        logger.info('ID values configured for server "%s": %s',server.name,str(server_config["id"]))
        servers[server.server_id] = server

    client.run(TOKEN)

if __name__ == '__main__':
    main()
