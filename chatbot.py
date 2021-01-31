import os

import discord
from dotenv import load_dotenv
from discord.ext.commands import Bot
import time, socket

from datetime import datetime
from dateutil.relativedelta import relativedelta


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = int(os.getenv('DISCORD_SERVER'))
T_CHANNEL = int(os.getenv('DISCORD_TEXT_CHANNEL'))
V_CHANNEL = int(os.getenv('DISCORD_VOICE_CHANNEL'))
ROLE = int(os.getenv('DISCORD_ROLE'))

client = discord.Client()


@client.event
async def on_ready():
    guild = discord.utils.find(lambda g: g.id==GUILD, client.guilds)
    print(f'{client.user} is connected to {guild.name}\n')

def is_join(before:discord.VoiceState,after:discord.VoiceState) -> bool:
    return before.channel is None and after.channel is not None

async def clear_chat():
    text_channel = client.get_channel(T_CHANNEL)
    if text_channel.last_message_id is None:
        print('No messages to delete from empty chat channel')
        return
    else:
        print('Deleting messages from empty chat channel')
    dt = datetime.now() - relativedelta(weeks=2)
    while messages := await text_channel.history(after=dt).flatten():
        await text_channel.delete_messages(messages)
    async for message in text_channel.history(): 
        await message.delete()
    print('All messages deleted')

@client.event
async def on_voice_state_update(member:discord.Member, before:discord.VoiceState, after:discord.VoiceState):
    role = client.get_guild(GUILD).get_role(ROLE)
    if is_join(before,after) and after.channel.id==V_CHANNEL:
        print(member.display_name,"has joined",after.channel.name)
        await member.add_roles(role)
    elif not is_join(before,after) and before.channel.id==V_CHANNEL:
        print(member.display_name,"has left",before.channel.name)
        await member.remove_roles(role)
        await clear_chat()


def connected():
    try:
        socket.create_connection(("8.8.8.8", 53))
        return True
    except Exception as err:
        print("Error: {0}".format(err))
        return False

while not connected():
    print("Failed to connect, waiting 60 seconds")
    time.sleep(60)
    
client.run(TOKEN)