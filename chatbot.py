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
formatter = logging.Formatter(fmt=f'{socket.gethostname()} {{%(name)s}} [%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

client = discord.Client()

@client.event
async def on_ready():
    guild = discord.utils.find(lambda g: g.id==GUILD, client.guilds)
    logger.info(f'{client.user} is connected to {guild.name}\n')

def is_join(before:discord.VoiceState,after:discord.VoiceState) -> bool:
    return before.channel is None and after.channel is not None
    
def is_leave(before:discord.VoiceState,after:discord.VoiceState) -> bool:
    return before.channel is not None and after.channel is None

async def clear_chat():
    text_channel = client.get_channel(T_CHANNEL)
    if text_channel.last_message_id is None:
        logger.info('No messages to delete from empty chat channel')
        return
    else:
        logger.info('Deleting messages from empty chat channel')
    dt = datetime.now() - relativedelta(weeks=2)
    while messages := await text_channel.history(after=dt).flatten():
        await text_channel.delete_messages(messages)
    async for message in text_channel.history(): 
        await message.delete()
    logger.info('All messages deleted')

@client.event
async def on_voice_state_update(member:discord.Member, before:discord.VoiceState, after:discord.VoiceState):
    role = client.get_guild(GUILD).get_role(ROLE)
    if is_join(before,after) and after.channel.id==V_CHANNEL:
        logger.info(f'{member.display_name} has joined {after.channel.name}')
        await member.add_roles(role)
    elif is_leave(before,after) and before.channel.id==V_CHANNEL:
        logger.info(f'{member.display_name} has left {before.channel.name}')
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