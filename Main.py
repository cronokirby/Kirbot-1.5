import discord
import re
import logging
import random
import emoji
# commands
import Commands, CT_Commands
# commands from the permission database
import Permissions_DB.Permission_Commands as PermCommands
# setting up error logging (for the Discord api)
logging.basicConfig(level=logging.INFO)

client = discord.Client()


# All of these functions return a discord.Embed object.
# They're called if a message starts with the key.
EmbedCommands = {
    "!test": Commands.test,
    "!categories": Commands.categories,
    "!search": Commands.search,
    "!wr": Commands.wr,
    "!streaminfo": Commands.streaminfo,
    "!permissions": PermCommands.permissions}


@client.event
async def on_message(message):
    # This is an object. Name should be fetched with .name, not str(author)!
    author = message.author
    # shifts the RNG table index by one, and gets a random num.
    RandomNum = CT_Commands.updateRNG()
    if RandomNum < 33:
        Reactions = [emoji.emojize(":whale:"), emoji.emojize(":dolphin:")]
        Reaction = Reactions[RandomNum % 2]
        await client.add_reaction(message, Reaction)
    # This iterates over my dictionary of commands, imported from Commands.
    # The keys are the commands, and what the message needs to start with.
    # All of the functions in EmbedCommands return a discord.Embed object
    for command, function in EmbedCommands.items():
        if message.content.startswith(command):
            EM = function(author, message)
            EM.set_footer(text=message.content)
            await client.send_message(message.channel, embed=EM)

    # Example: !1st !2nd !3rd
    TimeCommandREGEX = re.compile("!\d+[nsrt][tdh]|!-\d+[nsrt][tdh]")
    if TimeCommandREGEX.match(message.content.split(" ")[0]):
        EM = Commands.time(author, message)
        EM.set_footer(text=message.content)
        await client.send_message(message.channel, embed=EM)

# This is the oauth token
client.run("MjUxNzc4ODI3NjA3MzQzMTA0.CxvEXw.F-4iBCTslMSqfruNMbsSgWp_Kak")
