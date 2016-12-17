import discord
import asyncio
import re
import logging
import emoji
# these 2 are just to parse the config file
import json
import os
# commands
import Commands
import Chrono_Commands
# commands from the permission database
import Permissions_DB.Permission_Commands as PermCommands
# stream commands
import Stream_Link_DB.DB_Commands as StreamCommands
# filter commands
import Stream_Link_DB.Filter_Commands as FilterCommands
# to update the stream database every minute
import Stream_Link_DB.DB_Manipulation as Stream_Database
import Stream_Link_DB.Stream_Alerts as Stream_Alerts
# setting up error logging (for the Discord api)
logging.basicConfig(level=logging.INFO)

client = discord.Client()


# The routine for stream alerts, the current interval is 60s
async def alerts(interval):
    # this block executes only once
    await Stream_Database.updatestreamlists()
    alerter = Stream_Alerts.alert_generator()
    alerts = next(alerter)
    old_streams = alerts['streams']
    while True:
        await asyncio.sleep(interval)
        await Stream_Database.updatestreamlists()
        next(alerter)
        alerts = alerter.send(old_streams)
        old_streams = alerts['streams']
        # ~1/300 messages fail to send, this catches that to avoid a crash
        try:
            for message in alerts['messages']:
                channel = client.get_channel(message['channel'])
                await client.send_message(channel, embed=message['embed'])
        except:
            print("message failed to send...")
client.loop.create_task(alerts(60))

# All of these functions return a discord.Embed object.
# They're called if a message starts with the key.
EmbedCommands = {
    '!notes': Commands.notes,
    "!test": Commands.test,
    "!categories": Commands.categories,
    "!search": Commands.search,
    "!wr": Commands.wr,
    "!streaminfo": Commands.streaminfo,
    "!permissions": PermCommands.permissions,
    "!streams": StreamCommands.streams,
    "!filters": FilterCommands.filters}


@client.event
async def on_message(message):
    # This is an object. Name should be fetched with .name, not str(author)!
    author = message.author
    # shifts the RNG table index by one, and gets a random num.
    RandomNum = Chrono_Commands.updateRNG()
    if RandomNum < 33:
        Reactions = [emoji.emojize(":whale:"), emoji.emojize(":dolphin:")]
        Reaction = Reactions[RandomNum % 2]
        await client.add_reaction(message, Reaction)
    # This iterates over my dictionary of commands, imported from Commands.
    # The keys are the commands, and what the message needs to start with.
    # All of the functions in EmbedCommands return a discord.Embed object
    for command, function in EmbedCommands.items():
        if message.content.startswith(command):
            Embed = await function(author, message)
            if Embed is not None:
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
