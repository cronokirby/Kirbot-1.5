import discord
import asyncio
import re
import logging
import emoji
# commands
import Commands
import Chrono_Commands
# commands from the permission database
import Permissions_DB.Permission_Commands as PermCommands
# stream commands
import Stream_Link_DB.DB_Commands as StreamCommands
# to update the stream database every minute
import Stream_Link_DB.DB_Manipulation as Stream_Database
import Stream_Link_DB.Stream_Alerts as Stream_Alerts
# setting up error logging (for the Discord api)
logging.basicConfig(level=logging.INFO)

client = discord.Client()


# The routine for stream alerts, the current interval is 60s
async def alerts(interval):
    old_streams = None
    while True:
        await Stream_Database.updatestreamlists()
        print('streams updated')
        alerts = Stream_Alerts.alert_generator(old_streams)
        old_streams = alerts['streams']
        for message in alerts['messages']:
            await client.send_message(client.get_channel(message['channel']),
                                      embed=message['embed'])
        await asyncio.sleep(interval)
client.loop.create_task(alerts(60))
# All of these functions return a discord.Embed object.
# They're called if a message starts with the key.
EmbedCommands = {
    "!test": Commands.test,
    "!categories": Commands.categories,
    "!search": Commands.search,
    "!wr": Commands.wr,
    "!streaminfo": Commands.streaminfo,
    "!permissions": PermCommands.permissions,
    "!streams": StreamCommands.streams}


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
            Embed.set_footer(text=message.content)
            await client.send_message(message.channel, embed=Embed)

    # Example: !1st !2nd !3rd
    TimeCommandREGEX = re.compile("!\d+[nsrt][tdh]|!-\d+[nsrt][tdh]")
    if TimeCommandREGEX.match(message.content.split(" ")[0]):
        Embed = await Commands.time(author, message)
        Embed.set_footer(text=message.content)
        await client.send_message(message.channel, embed=Embed)

# This is the oauth token
client.run(# supply your own)
