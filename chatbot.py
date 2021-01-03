import os

import discord
from dotenv import load_dotenv
from discord.ext.commands import Bot
import time, socket


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_SERVER')
V_CHANNEL = os.getenv('DISCORD_CHANNEL')
ROLE = os.getenv('DISCORD_ROLE')

client = discord.Client()


@client.event
async def on_ready():
    guild = discord.utils.find(lambda g: str(g.id) == GUILD, client.guilds)
    print(f'{client.user} is connected to {guild.name}\n')


@client.event
async def on_voice_state_update(member:discord.Member, before:discord.VoiceState, after:discord.VoiceState):
    guild = discord.utils.find(lambda g: str(g.id) == GUILD, client.guilds)
    role = discord.utils.find(lambda r: r.name==ROLE,guild.roles)
    if before.channel is None and after.channel is not None and after.channel.name==V_CHANNEL:
        print(member.display_name,"has joined",V_CHANNEL)
        await member.add_roles(role)
    elif before.channel is not None and after.channel is None and before.channel.name==V_CHANNEL:
        print(member.display_name,"has left",V_CHANNEL)
        await member.remove_roles(role)

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
