"""
Kirbot can *whale* a message at random, this module handles that
"""
import discord
import os
import emoji
# for storing whaled messages
from Whaled_messages.Whale_DataBase import store_message, is_enabled,

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
CT_RNG_Table = os.path.join(dname, 'CT_RNG_Table.txt')
with open(CT_RNG_Table, 'r') as fp:
    raw_data = fp.read()
rng_table = [int(raw_data[i:i + 2], 16) for i in range(0, len(raw_data), 2)]

Reactions = [emoji.emojize(":whale:"), emoji.emojize(":dolphin:")]


def updateRNG():
    index = 0
    while True:
        RandomNum = rng_table[index % 256]
        index += 1
        yield RandomNum


rng_generator = updateRNG()


# converts a message into an archivable message
async def archive_message(author, message):
    Embed = discord.Embed(description=message.clean_content)
    Embed.set_author(name=author.name, icon_url=author.avatar_url)
    Embed.set_footer(text=str(message.timestamp)[:-7])
    return Embed


async def whale(client, author, message):
    random_num = next(rng_generator)
    serverid = message.server.id
    if is_enabled(serverid):
        if random_num > 225:
            reaction = Reactions[random_num % 2]
            await client.add_reaction(message, reaction)
            archived_message = await archive_message(author, message)
            store_message(serverid, archived_message.to_dict())
