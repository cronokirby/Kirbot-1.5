"""
This module contains commands, that will be contained in a dictionary;
the keys of the dictionary will be the commands that must be typed into chat
in order to call these functions. They all return a discord.Embed object,
which is then used in a client.send_message coroutine
"""

import discord
from Speedrun_API import fetchabbreviation, fetchcategories, fetchtime
from Twitch_API import fetchstreaminfo


def embed_command():
    def decorator(function):
        async def wrapper(*args):
            client = args[0]
            message = args[2]
            embed = await function(*args)
            await client.send_message(message.channel, embed=embed)
        return wrapper
    return decorator


@embed_command()
async def test(client, author, message):
    msg = '{}, what is a *test* ? :whale2:'.format(author.name)
    Embed = discord.Embed(description=msg, colour=0x42eef4, title="")
    Embed.set_thumbnail(url="http://imgur.com/dU6KiDb.png")
    Embed.set_author(name=author.name, icon_url=author.avatar_url)
    print(Embed.to_dict())
    return Embed


@embed_command()
async def search(client, author, message):
    # Because the correct syntax is "!search game"
    name = message.content.split(' ', 1)[-1]
    abb = await fetchabbreviation(name)

    # This happens if the URL constructed doesn't exist
    # This *usually* means the game doesn't exist either.
    if abb != "Invalid game name":
        # The last part removes the # identifier from the name.
        msg = "The abbreviation for \"{}\" is **{}**, {}".format(
            name, abb, author.name)
    else:
        msg = "I couldn't find this game :/"

    Embed = discord.Embed(description=msg, colour=0x42eef4)
    Embed.set_thumbnail(url="http://imgur.com/dU6KiDb.png")
    return Embed


@embed_command()
async def categories(client, author, message):
    # checks whether or not the syntax is '!categories abbreviation/"Game Name"
    if len(message.content.split('"')) > 1:
        game_name = message.content.split('"')[1]
        game = await fetchabbreviation(game_name)
    else:
        game = message.content.split(' ')[1]

    categories = await fetchcategories(game)
    if categories != "Invalid game name":
        Keys = [key for key in dict.keys(categories)]
        msg = "Here's a list of valid categories for '{}', {} :)\n".format(
            game, author, author.name)
        for item in Keys:
            msg += '"{}"\n'.format(item)
    else:
        msg = "Woops, looks like the game name is wrong D:"

    Embed = discord.Embed(description=msg, colour=0x42eef4)
    Embed.set_thumbnail(url="http://imgur.com/dU6KiDb.png")
    return Embed


@embed_command()
async def wr(client, author, message):
    if len(message.content.split('"')) > 1:
        game_name = message.content.split('"')[1]
        game = await fetchabbreviation(game_name)
        category = message.content.split('"')[2][1:]
    else:
        category = message.content.split(' ', 2)[2]
        game = message.content.split(' ', 2)[1]
    categories = await fetchcategories(game)
    if categories != "Invalid game name":
        if category in categories:
            f = await fetchtime(game, category, 0)
            if not("name" in f):
                msg = "There don't seem to be any times here..."
            else:
                name = f["name"]
                time = f["time"]
                vod = f["vod"]
                msg = "The **WR** is **{}** by **{}** :whale2:\n<{}>".format(
                    time, name, vod)
        elif category == "All":
            msg = 'Here are all the **WR** times for "{}" :\n'.format(game)
            Embed = discord.Embed(description=msg, colour=0x42eef4)
            Embed.set_thumbnail(url="http://imgur.com/dU6KiDb.png")
            Cats = dict.keys(categories)
            for item in Cats:
                f = await fetchtime(game, item, 0)
                if "name" in f:
                    name = f["name"]
                    time = f["time"]
                    field_desc = "**{}** by **{}**\n".format(time, name)
                    Embed.add_field(name=item, value=field_desc)
            return Embed
        else:
            msg = ("Woops, that category doesn't seem to exist.\n"
                   'You can use "!categories game" for a list of categories')
    else:
        msg = ("Woops, that's an invalid game name.\n"
               'The correct syntax for this command is "!wr game category"')

    Embed = discord.Embed(description=msg, colour=0x42eef4)
    Embed.set_thumbnail(url="http://imgur.com/dU6KiDb.png")
    return Embed


@embed_command()
async def time(client, author, message):

    if len(message.content.split('"')) > 1:
        game_name = message.content.split('"')[1]
        game = await fetchabbreviation(game_name)
        category = message.content.split('"')[2][1:]
        command = message.content.split('"')[0][:-1]
        rank = int(command[1:-2])
    else:
        category = message.content.split(' ', 2)[2]
        game = message.content.split(' ', 2)[1]
        command = message.content.split(' ')[0]
        rank = int(command[1:-2])

    categories = await fetchcategories(game)
    if categories != "Invalid game name":

        if category in categories:
            if rank > 0:
                place = command[1:4 + len(str(rank)) - 1]
                rank -= 1
            elif rank == 0:
                return "0 isn't a rank, silly x)"
            elif rank == -1:
                place = "last"
            else:
                place = command[2:5 + len(str(rank)) - 1] + " to last"
            f = await fetchtime(game, category, rank)
            if not("name" in f):
                msg = ("There don't seem to be any times here...")
            else:
                name = f["name"]
                time = f["time"]
                vod = f["vod"]
                if rank != 0:
                    msg = ("""The **{}** place time is **{}** by **{}** :whale2:
                    <{}>""").format(place, time, name, vod)
                else:
                    msg = ("The **WR** is **{}** by **{}** :whale2:\n"
                           "<{}>").format(time, name, vod)

        elif category == "All":
            if rank > 0:
                place = command[1:4 + len(str(rank)) - 1]
                rank -= 1
                if rank != 0:
                    msg = ("Here are all the **{}** place times for "
                           "{}:\n").format(place, game)
                else:
                    msg = "Here are all the **WR** times for {}:\n".format(
                        place, game)
            elif rank == 0:
                return "0 isn't a rank, silly x)"
            elif rank == -1:
                place = "last"
                msg = "Here are all the **{}** place times for {}:\n".format(
                    place, game)
            else:
                place = command[2:5 + len(str(rank)) - 1]
                msg = ("Here are all the **{}** to last**"
                       "place times for {}:\n").format(place, game)
            Embed = discord.Embed(description=msg, colour=0x42eef4)
            Embed.set_thumbnail(url="http://imgur.com/dU6KiDb.png")
            Cats = dict.keys(categories)
            for item in Cats:
                f = await fetchtime(game, item, rank)
                if "name" in f:
                    name = f["name"]
                    time = f["time"]
                    field_desc = "**{}** by **{}**\n".format(time, name)
                    Embed.add_field(name=item, value=field_desc)
            return Embed
        else:
            msg = '''Woops, that category doesn't seem to exist.
            You can use "!categories game" for a list of valid categories'''
    else:
        msg = '''Woops, that's an invalid game name.
        The correct syntax for this command is "!wr game category"'''

    Embed = discord.Embed(description=msg, colour=0x42eef4)
    Embed.set_thumbnail(url="http://imgur.com/dU6KiDb.png")
    return Embed


@embed_command()
async def streaminfo(client, author, message):
    # example command: !streaminfo cronokirby -> twitch.tv/cronokirby
    name = message.content.split(" ")[1]
    Info = await fetchstreaminfo(name)
    valid_extra_arguments = ["status", "game", "uptime", "viewers", "preview"]
    settings = {key: True for key in valid_extra_arguments}
    # e.g. !streaminfo name /preview won't display preview * is only that field
    arg_type = None
    if "/" in message.content:
        # arg_type is what the setting will be set to
        arg_type = False
        extra_args = message.content.split("/")[-1].replace(" ", "").split(",")
        extra_args = [string.lower() for string in extra_args]
    elif "*" in message.content:
        arg_type = True
        extra_args = message.content.split("*")[-1].replace(" ", "").split(",")
        extra_args = [string.lower() for string in extra_args]

    if arg_type is not None:
        if arg_type:
            settings = {key: False for key in valid_extra_arguments}
        # checking if any of the arguments is bad
        for item in extra_args:
            if not(item in valid_extra_arguments):
                S = ('"{}" is not a valid extra argument :/\n'
                     'Here is a list of valid arguments:\n'
                     '`{}`').format(item, ", ".join(valid_extra_arguments))
                Embed = discord.Embed(description=S, colour=0xb01e1e)
                return Embed
            else:
                settings[item] = arg_type

    if Info != "bad name":
        StreamURL = Info["URL"]

        if Info["online"]:
            Embed = discord.Embed(description="", colour=0x9e42f4)
            Embed.set_author(name=Info["display_name"], url=StreamURL)
            Embed.set_thumbnail(url=Info["logo"])
            Hours = str(Info["uptime"]["Hours"])
            Minutes = str(Info["uptime"]["Minutes"])
            HourString = "**{}** hour".format(Hours)
            MinuteString = "& **{}** minute".format(Minutes)
            if int(Hours) == 0:
                HourString = ""
                MinuteString = MinuteString[2:]
            # This implies that if int(Hours) == 1, no "s" is needed
            elif int(Hours) > 1:
                HourString += "s"
            if int(Minutes) == 0:
                MinuteString = ""
            elif int(Minutes) > 1:
                MinuteString += "s"
            # This is a different Uptime, will be used in the iterator.
            Info["uptime"] = "{} {}".format(HourString, MinuteString)
            for setting, boolean in sorted(settings.items()):
                if boolean:
                    if setting != "preview":
                        Embed.add_field(name=setting.title() + ':',
                                        value=Info[setting])
            if settings['preview']:
                Embed.add_field(name="Preview", value=u"\u200b")
                Embed.set_image(url=Info["preview"])
        else:
            S = "{} isn't live at the moment :/".format(name)
            Embed = discord.Embed(description=S, colour=0xb01e1e)
    else:
        S = "Woops, that channel doesn't seem to exist..."
        Embed = discord.Embed(description=S, colour=0xb01e1e)
    return Embed
