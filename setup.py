import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='discordChatBot-TheBiggerFish',
    version='1.0.0',
    author='TheBiggerFish',
    author_email='clhnumber4@gmail.com',
    description='A discord bot to add a role to user while user is in voice channel',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/TheBiggerFish/DiscordChatBot',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'PyYAML',
        'discord',
        'python-dotenv',
        'python-dateutil'
    ],
    python_requires='>=3.8',
)