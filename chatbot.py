import os
import logging,logging.handlers

import discord
from discord.ext.commands import Bot

import time, socket
from dotenv import load_dotenv
from datetime import datetime
from dateutil.relativedelta import relativedelta


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = int(os.getenv('DISCORD_SERVER'))
T_CHANNEL = int(os.getenv('DISCORD_TEXT_CHANNEL'))
V_CHANNEL = int(os.getenv('DISCORD_VOICE_CHANNEL'))
ROLE = int(os.getenv('DISCORD_ROLE'))
LOGGING_HOST = os.getenv('LOGGING_HOST')
LOGGING_PORT = int(os.getenv('LOGGING_PORT'))
LOGGING_NAME = 'DISCORD_CHAT_BOT'

logger = logging.Logger(LOGGING_NAME)
handler = logging.handlers.SysLogHandler(address=(LOGGING_HOST,LOGGING_PORT))
formatter = logging.Formatter(fmt=f'{socket.gethostname()} [%(levelname)s] %(process)s {{%(name)s}} %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

client = discord.Client()

@client.event
async def on_ready():
    guild = client.get_guild(GUILD)
    if not isinstance(guild,discord.Guild):
        logger.error(f'Discord guild {GUILD} is not valid')
    else:
        logger.info(f'{client.user} is connected to {guild.name}\n')

def is_join(before:discord.VoiceState,after:discord.VoiceState) -> bool:
    return before.channel is None and after.channel is not None
    
def is_leave(before:discord.VoiceState,after:discord.VoiceState) -> bool:
    return before.channel is not None and after.channel is None

async def clear_chat():
    text_channel = client.get_channel(T_CHANNEL)
    if not isinstance(text_channel,discord.TextChannel):
        logger.error(f'Discord text channgel {T_CHANNEL} is not valid')
        return
    
    if not await text_channel.history(limit=1).flatten():
        logger.info('No messages to delete from empty chat channel')
        return
    else:
        logger.info('Deleting messages from empty chat channel')
    dt = datetime.now() - relativedelta(weeks=2)
    while messages := await text_channel.history(after=dt).flatten():
        await text_channel.delete_messages(messages)

    logger.info('All messages deleted')

@client.event
async def on_voice_state_update(member:discord.Member, before:discord.VoiceState, after:discord.VoiceState):
    guild = client.get_guild(GUILD)
    if not isinstance(guild,discord.Guild):
        logger.error(f'Discord guild {GUILD} is not valid')
        return
    
    role = guild.get_role(ROLE)
    if not isinstance(role,discord.Role):
        logger.error(f'Discord guild {ROLE} is not valid')
        return
    
    if not isinstance(before.channel,discord.VoiceChannel) or not isinstance(after.channel,discord.VoiceChannel):
        logger.error(f'Channel type error in voice_state_update event')
        return
    
    if is_join(before,after) and after.channel.id==V_CHANNEL:
        logger.info(f'User {member.display_name} has joined voice channel {after.channel.name}')
        await member.add_roles(role)
    elif is_leave(before,after) and before.channel.id==V_CHANNEL:
        logger.info(f'User {member.display_name} has left voice channel {before.channel.name}')
        await member.remove_roles(role)
        if len(before.channel.voice_states.keys()) == 0:
            await clear_chat()


def connected():
    try:
        socket.create_connection(("8.8.8.8", 53))
        return True
    except Exception as err:
        logger.error("Error connecting: {0}".format(err))
        return False

while not connected():
    logger.error("Failed to connect, waiting 60 seconds")
    time.sleep(60)
    
client.run(TOKEN)