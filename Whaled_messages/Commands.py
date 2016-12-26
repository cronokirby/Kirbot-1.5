"""
These commands serve to allow users to enable whaling messages, and allows them
to access previous messages
"""
import discord

from Whaled_messages.Whale_DataBase import (registerserver, toggle,
                                            get_random_message,
                                            get_messages)
from Permissions_DB.Permission_Commands import permission_check
from Commands import embed_command


@permission_check(1)
# toggletype = now / no longer
def toggle_whales(server, requester, boolean):
    toggle(server.id, boolean)
    if boolean:
        insert = 'now'
    else:
        insert = 'no longer'
    description = "Kirbot can {} :whale2: messages in `{}`".format(
        insert, server.name)
    return discord.Embed(description=description, colour=0x42eef4)


def revert_whale_dict(embed_dict):
    embed_dict['colour'] = 0x42eef4
    Embed = discord.Embed(**embed_dict)
    Embed.set_footer(**embed_dict['footer'])
    Embed.set_author(**embed_dict['author'])
    return Embed


# returns a random message
async def random(serverid):
    embed_dict = await get_random_message(serverid)
    return revert_whale_dict(embed_dict)


# returns the last whaled message
async def last(serverid):
    embed_list = await get_messages(serverid)
    last_embed_dict = embed_list[-1]
    return revert_whale_dict(last_embed_dict)


@embed_command()
# !whale last
async def whale(client, author, message):
    args = message.content.split(' ')
    server = message.server
    registerserver(server.id)
    keyword = args[1]
    if keyword == 'enable':
        return toggle_whales(server, author, True)
    elif keyword == 'disable':
        return toggle_whales(server, author, False)
    elif keyword == 'last':
        return await last(server.id)
    elif keyword == 'random':
        return await random(server.id)
