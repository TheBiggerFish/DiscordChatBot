# ChatBot

This discord bot can be used to add a role to server members when they join a specific voice channel. This can be used to create a text channel that can be used for posting without bothering members not in the call.

## Setup

pip install discord \
pip install python-dotenv

Create *.env* file in directory with following parameters

* DISCORD_TOKEN (bot token)
* DISCORD_SERVER (server id number)
* DISCORD_VOICE_CHANNEL (voice channel id number)
* DISCORD_TEXT_CHANNEL (text channel id number)
* DISCORD_ROLE (role to add to users id number)
* LOGGING_HOST (host of log aggregator, e.g. localhost)
* LOGGING_PORT (port of log aggregator, e.g. 514)
  
Add line to crontab \
```@reboot sudo /usr/local/bin/python3 /path/to/chatbot.py >/path/to/chatbot.log 2>&1 &```
