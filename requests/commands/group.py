# pylint: skip-file

import os

import requests
from dotenv.main import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

url = 'https://discord.com/api/v8/applications/795160689240047668/commands/'

json = {
    'name': 'group',
    'type': 1,
    'description': 'Create temporary voice and text channels viewable only by yourself and the user/role mentioned. This channel will be automatically deleted when the last member leaves, or after 5 minutes if not joined by anyone.',
    'options': [
        {
            'name': 'create/remove',
            'description': 'Create or remove a group',
            'type': 3,
            'required': True,
            'choices': [
                {
                    'name': 'create',
                    'value': 'STATUS_CREATE'
                },
                {
                    'name': 'remove',
                    'value': 'STATUS_REMOVE'
                }
            ]
        },
        {
            'name': 'Channel Name',
            'description': 'Name of temporary voice/text channels',
            'type': 3,
            'required': True
        },
        {
            'name': 'User or Role',
            'description': 'User or role which will be able to join channel',
            'type': 9,
            'required': False
        }
    ]
}


headers = {
    "Authorization": f"Bot {TOKEN}"
}

r = requests.post(url, headers=headers, json=json)
