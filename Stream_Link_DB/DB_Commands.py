"""
These functions serve as the intermediary between messages in chat, and the
manipulation of the Stream_Link_Database.
All of these commands are of permission level 1
"""
import re

import discord
# to check if streams exist mainly
from Twitch_API import findstream

from Permissions_DB.Permission_Commands import badpermissionembed
from Permissions_DB.Perm_DB_Manipulation import checkpermissions
from Stream_Link_DB.DB_Manipulation import (addstream, fetchserverinfo,
                                            enableserver, disableserver,
                                            registerserver)


# e.g. Cronokirby#4567
discord_name_regex = re.compile('\D+#[0-9][0-9][0-9][0-9]')
# the permission level for certain commands here
permission_level = 1


# you need to pass the server object through this function
def live(server):
    # each element in live streams contains the necessary info we need
    live_streams = fetchserverinfo(server.id)['live_streams']
    extra_streams = False
    description = ("Here's a list of streams in `{}` "
                   "that are currently live:\n").format(server.name)
    # The max # of fields in an embed is 25
    if len(live_streams) > 24:
        description += ("*there are more than 24 streams live atm,"
                        "and I couldn't display them all* :/")
        extra_streams = live_streams[24:]
        live_streams = live_streams[:24]

    Embed = discord.Embed(description=description, colour=0x9e42f4)
    for stream in live_streams:
        url = stream['URL']
        status = stream['status']
        Embed.add_field(name=url, value=status)
    if extra_streams is not False:
        field_value = '`{}`'.format(extra_streams)
        Embed.add_field(name='Other streams:', value=field_value)

    return Embed


# This returns an Embed object with info about these commands
def info():
    title = 'Stream Commands info'
    description = ('Kirbot has the ability to keep track of a list of streams '
                   'in every server, and give alerts when they go live\n'
                   'only `!streams live`, `!streams info`, and `!streams list`'
                   ' are available '
                   'to everyone. The other commands need permission level 1\n'
                   'Use `!permissions info` for more info on permissions\n'
                   "Here's some more info:")
    field1desc = ('This command adds a stream to the list of streams for this '
                  'server.\nThe correct syntax for this command is: '
                  '`!streams add twitchname`')
    field2desc = ('This command appends a list of streams to the server list.'
                  '\nThe correct syntax for this command is: '
                  '`!streams add twitchname1, twitchname2` '
                  "*spaces aren't necessary, but allowed*")
    field3desc = ('This command returns a list of streams currently live\n'
                  'Since the max field count for embeds is 25, it can only'
                  ' fully format 25 streams in the message')
    field4desc = ('This command enables Kirbot to alert the server, '
                  'when streams go live.\nThe channel you use this command in '
                  'will be where the alerts happen.')
    field5desc = ("Alerts are disabled by default, but if you want to disable "
                  "them after they've been enabled, use this command.")
    fields = [{'title': '`!streams add`', 'value': field1desc},
              {'title': '`!streams add`s', 'value': field2desc},
              {'title': '`!streams live`', 'value': field3desc},
              {'title': '`!streams enable`', 'value': field4desc},
              {'title': '`!streams disable`', 'value': field5desc}]

    Embed = discord.Embed(description=description,
                          title=title,
                          colour=0x42eef4)
    for field in fields:
        Embed.add_field(name=field['title'], value=field['value'])

    return Embed


def streamcount(server):
    info = fetchserverinfo(server.id)
    # sorted is to alphabetize the list
    stream_list = sorted(info['streamlist'])
    description = ("Here's some info about the streams in `{}`").format(
        server.name)
    Embed = discord.Embed(description=description, colour=0x42eef4)
    title2 = 'Stream count:'
    field2 = '`{}`'.format(len(stream_list))
    Embed.add_field(name=title2, value=field2)

    return Embed


# if the user does !streams add, list will be of size 1
def addstreams(server, requester, streams_to_add):
    if checkpermissions(server.id, permission_level, requester) is False:
        return badpermissionembed(server, permission_level)
    valid_streams, invalid_streams = [], []
    for twitchname in streams_to_add:
        print(twitchname)
        if findstream(twitchname) is not False:
            addstream(server.id, twitchname)
            valid_streams.append(twitchname)
        else:
            invalid_streams.append(twitchname)
    color = 0x42eef4
    if len(valid_streams) == 0 :
        color = 0xb01e1e
        if len(streams_to_add) == 1:
            S = "I couldn't find that stream on twitch :/"
        else:
            S = "I couldn't find any of these streams on twitch :/"
    else:
        valid_string = ', '.join(valid_streams)
        S = 'Added `{}` to the streamlist in {}\n'.format(
            valid_string, server.name)
        if len(invalid_streams) != 0:
            invalid_string = ', '.join(invalid_streams)
            S += ("The following streams couldn't be found on twitch:\n"
                  "`{}`".format(invalid_string))
    Embed = discord.Embed(description=S, colour=color)
    return Embed


def enable(server, channel, requester):
    if checkpermissions(server.id, permission_level, requester) is False:
        return badpermissionembed(server, permission_level)
    enableserver(server.id, channel.id)
    S = ('Kirbot will now tell you when streams go live in `{}`\n'
         'If you want me to alert you in a different channel, use'
         '`!streams enable` there. \n'
         'If you want to disable this feature, use `!streams disable`').format(
        channel.name)
    Embed = discord.Embed(description=S, colour=0x42eef4)
    return Embed


def disable(server, requester):
    if checkpermissions(server.id, permission_level, requester) is False:
        return badpermissionembed(server, permission_level)
    disableserver(server.id)
    S = ('Kirbot will no longer alert streams.\n'
         'To reenable this feauture, use '
         '`!streams disable`')
    Embed = discord.Embed(description=S, colour=0x42eef4)
    return Embed


async def streams(author, message):
    server = message.server
    channel = message.channel
    registerserver(server.id)
    # i.e. !streams keyword args
    args = message.content.split(' ', 2)
    # !streams live
    if args[1] == 'live':
        return live(server)
    # !streams info
    elif args[1] == 'info':
        return info()
    # !streams list
    elif args[1] == 'count':
        return streamcount(server)
    # !streams enable
    elif args[1] == 'enable':
        return enable(server, channel, author)
    # !streams disable
    elif args[1] == 'disable':
        return disable(server, author)
    # !streams add
    elif args[1] == 'add':
        # args[2] is the twitchname
        streamtoadd = args[2].lower()
        return addstreams(server, author, [streamtoadd])
    # !streams adds
    elif args[1] == 'adds':
        args[2].replace(" ", "")
        streamstoadd = args[2].lower()
        streamstoadd = streamstoadd.split(",")
        return addstreams(server, author, streamstoadd)
