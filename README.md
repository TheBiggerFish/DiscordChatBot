# ChatBot

This discord bot can be used to add a role to server members when they join a specific voice channel. This can be used to create a text channel that can be used for posting without bothering members not in the call.

## Setup to Use Existing Infrastructure

Create pull request to add server configuration to config.yml


## Setup to Self-Host

Written for `Python 3.8.10` 

`pip install discord` \
`pip install python-dotenv` \
`pip install python-dateutil` \
`pip install pyyaml `

Create *.env* file in directory with following parameters

* `DISCORD_TOKEN` (SECRET bot token)
* `CONFIG_PATH` (path to config.yml)
* `LOGGING_HOST` (host of log aggregator, e.g. localhost)
* `LOGGING_PORT` (port of log aggregator, e.g. 514)

Add line to crontab \
```@reboot sudo /usr/local/bin/python3 /path/to/chatbot.py &```

Create server configurations in config.yml