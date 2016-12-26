"""
This module provides the interface between user commands, and interactions
with the game filters in the stream link database.
Filters are used to make stream alerts more exclusive
"""
# for creating Embed
import discord

from Commands import embed_command
from Permissions_DB.Permission_Commands import badpermissionembed
from Permissions_DB.Perm_DB_Manipulation import checkpermissions
from Stream_Link_DB.DB_Manipulation import (addfilter, removefilter,
                                            getfilters, is_enabled,
                                            registerserver, togglefilters)

permission_level = 2


# adds a new filter to a server, the discord.server object is passed
async def add(server, requester, filter_name):
    if checkpermissions(server.id, permission_level, requester) is False:
        return badpermissionembed(server, permission_level)
    # add filter has the side effect of adding the filter
    twitch_name = await addfilter(server.id, filter_name)
    if twitch_name is not False:
        description = "`{}` was added to the filters in {}\n".format(
            twitch_name, server.name)
        if not(is_enabled(server.id)):
            description += "You can use `!filters enable` to turn on filters"
    else:
        description = "`{}` doesn't seem to be a valid game on twitch".format(
            filter_name)
    Embed = discord.Embed(description=description, colour=0x42eef4)
    return Embed


def remove(server, requester, filter_name):
    if checkpermissions(server.id, permission_level, requester) is False:
        return badpermissionembed(server, permission_level)
    removed = removefilter(server.id, filter_name)
    if removed:
        description = "`{}` was removed from the filters in `{}`".format(
            filter_name, server.name)
    else:
        description = ("`{}` doesn't seem to be in the filters in `{}`\n"
                       "You can use `!filters list` for a full list").format(
            filter_name, server.name)
    Embed = discord.Embed(description=description, colour=0x42eef4)
    return Embed


# asks the database to enable filters in that server
def toggle(server, requester, boolean):
    if checkpermissions(server.id, permission_level, requester) is False:
        return badpermissionembed(server, permission_level)
    togglefilters(server.id, boolean)
    if boolean:
        description = "Filters are now enabled in `{}`".format(server.name)
    else:
        description = "Filters are now disabled in `{}`".format(server.name)
    Embed = discord.Embed(description=description, colour=0x42eef4)
    return Embed


def list_filters(server):
    filter_list = sorted(getfilters(server.id))
    filters = ", ".join(["`{}`".format(flt) for flt in filter_list])
    description = "Here's a full list of filters in `{}`:\n".format(
        server.name)
    description += filters
    Embed = discord.Embed(description=description, colour=0x42eef4)
    return Embed


# This returns an Embed object with info about these commands
def info():
    title = '!filters info'
    description = ('Kirbot has the ability to only alert streams that are '
                   'playing certain games, via *filters*: '
                   "if filters are enabled, streams not playing any of the "
                   "games in the list won't be alerted.\n"
                   'Only `!filters list` and `!filters info` are available '
                   'to everyone. The other commands are of permission level '
                   '1\nUse `!permissions info` or `!streams info` '
                   'for more info on permssions, and stream alerts.')
    field1desc = ('This command adds a new game to the filter list in this'
                  " server, by name. If the game can't be found a twitch, "
                  'it will not be added, and Kirbot will notify you of that\n'
                  'The correct syntax for this command is: '
                  '`!filters add game name`')
    field2desc = ("Removes a filter, by game name again, from the server's "
                  "list, *given it is in the list, of course*\n"
                  'The correct syntax for this command is: '
                  '`!filters remove game name`')
    field3desc = ("This command lists all the filters in a server")
    field4desc = "This command turns on filters in a server."
    field5desc = "This command turns off filters in a server"
    fields = [{'title': '`!filters add`', 'value': field1desc},
              {'title': '`!filters remove`', 'value': field2desc},
              {'title': '`!filters list`', 'value': field3desc},
              {'title': '`!filters enable`', 'value': field4desc},
              {'title': '`!filters disable`', 'value': field5desc}]

    Embed = discord.Embed(description=description,
                          title=title,
                          colour=0x42eef4)
    for field in fields:
        Embed.add_field(name=field['title'], value=field['value'])

    return Embed


# the message gets sent here if it matches '!filters'
@embed_command()
async def filters(client, author, message):
    server = message.server
    registerserver(server.id)
    # i.e. !filters keyword arg1 arg2
    args = message.content.split(' ', 2)
    # !filters add game name
    if args[1] == 'add':
        return await add(server, author, args[2])
    # !filters remove game name
    elif args[1] == 'remove':
        return remove(server, author, args[2])
    # !filters enable
    elif args[1] == 'enable':
        return toggle(server, author, True)
    elif args[1] == 'disable':
        return toggle(server, author, False)
    # !filters list
    elif args[1] == 'list':
        return list_filters(server)
    # !filters info
    elif args[1] == 'info':
        return info()
