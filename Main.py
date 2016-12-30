import discord
import re
import logging
# these 2 are just to parse the config file
import json
import os
# commands
import Commands
# whale commands
from Whaled_messages.Reactions import whale
import Whaled_messages.Commands as Whale_commands
# commands from the permission database
import Permissions_DB.Permission_Commands as PermCommands
# stream commands
import Stream_Link_DB.DB_Commands as StreamCommands
# filter commands
import Stream_Link_DB.Filter_Commands as FilterCommands
# to update the stream database every minute
import Stream_Link_DB.Stream_Alerts as Stream_Alerts
# For custom commands
import Custom_Commands.CC_Commands as Custom_Commands
import Custom_Commands.CC_DB_manipulation as Customs_DB
# For message logging
import Messages.Logger as Logger
# setting up error logging (for the Discord api)
logging.basicConfig(level=logging.INFO)

client = discord.Client()
# set up the stream alerter to update the streamlist every 60s
# the alerter sends a message if a new stream pops up
client.loop.create_task(Stream_Alerts.alerts(client, 60))

# All of these functions return a discord.Embed object.
# They're called if a message starts with the key.
command_list = {
    "!test": Commands.test,
    "!categories": Commands.categories,
    "!search": Commands.search,
    "!wr": Commands.wr,
    "!streaminfo": Commands.streaminfo,
    "!permissions": PermCommands.permissions,
    "!streams": StreamCommands.streams,
    "!filters": FilterCommands.filters,
    "!commands": Custom_Commands.commands,
    "!!logs": Logger.send_logs,
    '!whale': Whale_commands.whale}


@client.event
async def on_message(message):
    # This is an object. Name should be fetched with .name, not str(author)!
    author = message.author
    # will add a reaction to the message, if the rng is right
    #await whale(client, author, message)
    # This iterates over my dictionary of commands, imported from Commands.
    # The keys are the commands, and what the message needs to start with.
    for command, function in command_list.items():
        if message.content.startswith(command):
            await function(client, author, message)
    # this get a list of custom commands in this server, and handles matches
    serverid = message.server.id
    if serverid not in Customs_DB.getregisteredservers():
        Customs_DB.cc_registerserver(serverid)
    for command in Customs_DB.getcommands(serverid):
        if message.content.startswith('?' + command):
            Embed = Customs_DB.constructembed(serverid, command)
            Embed.set_footer(text=message.content)
            await client.send_message(message.channel, embed=Embed)

    # Example: !1st !2nd !3rd
    TimeCommandREGEX = re.compile("!\d+[nsrt][tdh]|!-\d+[nsrt][tdh]")
    if TimeCommandREGEX.match(message.content.split(" ")[0]):
        Embed = await Commands.time(author, message)
        Embed.set_footer(text=message.content)
        await client.send_message(message.channel, embed=Embed)


# this changes the directory to the directory of the script
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
with open(os.path.join(dname, 'config.json')) as fp:
    Oauth = json.load(fp)['discord_oauth']
# start running the bot with the Oauth key
client.run(Oauth)
