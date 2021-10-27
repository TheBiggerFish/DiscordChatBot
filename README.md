# ChatBot

This discord bot can be used to add a role to server members when they join a specific voice channel. This can be used to create a text channel that can be used for posting without bothering members not in the call.

## Setup to Use Existing Infrastructure

Invite `ChatBot#5666` to your server \
Create pull request to add your server configuration to config.yml

## Setup to Self-Host

Written for `Python 3.8.10` 

`pip install .`

---
Create *.env* file in directory with following parameters

* `DISCORD_TOKEN`* (SECRET bot token)
* `CONFIG_PATH`* (path to config.yml)
* `LOGGING_NAME`* (name of service displayed in log output)
* `LOGGING_HOST` (host of log aggregator, e.g. localhost)
* `LOGGING_PORT` (port of log aggregator, e.g. 514)
* `LOGGING_LEVEL` (log output threshold, e.g. DEBUG,INFO,WARNING)

If LOGGING_HOST is not provided, logs output to stdout \
**required*

---
Add line to crontab for auto-run on startup \
```@reboot sudo /usr/local/bin/python3 /path/to/chatbot.py &```

---
Create server configurations in config.yml
