"""
These functions allows users to interact with the custom commands db via
messages. The database isn't actually modified here
"""
# for creating Embeds
import discord

from Commands import embed_command
from Permissions_DB.Permission_Commands import permission_check
from Custom_Commands.CC_DB_manipulation import (cc_registerserver,
                                                addcommand,
                                                editparam, constructembed,
                                                removecommand, getcommands,
                                                appendfields, removefield)
permission_level = 1

colors = {'teal': 0x3498db,
          'midnight': 0x1415cf,
          'turquoise': 0x1abc9c,
          'sun': 0xf1c40f,
          'orange': 0xf39c12,
          'red': 0xc0392b,
          'green': 0x2ecc71,
          'purple': 0x8e44ad,
          'grey': 0x7f8c8d,
          'white': 0xecf0f1}


# error embeds
def non_existant_command_embed(command_name, server):
    description = "`{}` doesn't seem to be a command in `{}`".format(
        command_name, server.name)
    Embed = discord.Embed(description=description, colour=0xb01e1e)
    return Embed


# adds a new command to the server
@permission_check(permission_level)
def newcommand(server, requester, command_name, description):
    # the command already exists, user probably doesn't want to reset
    if command_name in getcommands(server.id):
        description = "`{}` already exists in `{}`\n".format(
            command_name, server.name)
        description += ("You can use `!commands remove name` to get rid of "
                        "this command, or `!commands edit name` to modify it.")
        Embed = discord.Embed(description=description, colour=0xb01e1e)
        return Embed
    else:
        addcommand(server.id, command_name, description)
        description = "`{}` is now a command in `{}`\n".format(
            command_name, server.name)
        description += "Use `!commands edit name` to modify it"
        Embed = discord.Embed(description=description, colour=0x42eef4)
        return Embed


@permission_check(permission_level)
def remove(server, requester, command_name):
    if command_name in getcommands(server.id):
        removecommand(server.id, command_name)
        description = "`{}` was deleted from `{}`".format(
            command_name, server.name)
        Embed = discord.Embed(description=description, colour=0x42eef4)
        return Embed
    else:
        return non_existant_command_embed(command_name, server)


@permission_check(permission_level)
def addfields(server, requester, command_name, fields):
    if command_name in getcommands(server.id):
        print(fields)
        appendfields(server.id, command_name, fields)
        return constructembed(server.id, command_name)
    else:
        return non_existant_command_embed(command_name, server)


@permission_check(permission_level)
def removefld(server, requester, command_name, index):
    if command_name in getcommands(server.id):
        removefield(server.id, command_name, index)
        return constructembed(server.id, command_name)
    else:
        return non_existant_command_embed(command_name, server)


# every param is formatted like {'param': 'color', 'value': 0x000000}
@permission_check(permission_level)
def edit(server, requester, command_name, params):
    if command_name in getcommands(server.id):
        for param in params:
            editparam(server.id, command_name, param['param'], param['value'])
        return constructembed(server.id, command_name)
    else:
        return non_existant_command_embed(command_name, server)


def listcommands(server):
    commands = ['`{}`'.format(c) for c in getcommands(server.id)]
    commandstring = ', '.join(commands)
    description = "Here is a list of commands in {}: \n".format(server.name)
    description += commandstring
    Embed = discord.Embed(description=description, colour=0x42eef4)
    return Embed


def info():
    title = '!commands info'
    description = ('Kirbot has the ability to keep track of a list of '
                   'custom commands in every server.\n'
                   'You can add custom commands, and edit their content, '
                   'color, and even add new fields, with titles and values\n'
                   'To use a command, simply add a `?` before the command '
                   'name\n'
                   "You need to have permission level `1` to edit custom "
                   "commands. For more info on permissions, "
                   "use `!permissions info`\n"
                   "Here's some more info:")
    field1desc = ('This command adds a new command to the list, '
                  'with a message attached to it. '
                  "Commands can't contain spaces."
                  'The correct syntax for this command is: '
                  '`!commands new command_name message goes here`')
    field2desc = ('This command removes a command from the list, '
                  'if it exists.\nThe correct syntax for this command is: '
                  '`!commands remove command_name`')
    field3desc = ('This command edits a preexisting command.\n'
                  'The parameters this command can take are '
                  '`title()`, `description()`, `url()`, and `color()`. '
                  'You can include any of them in the command. '
                  'Use `!commands colors` for a list of colors.\n'
                  'The correct syntax for this command is: '
                  '`!commands edit command_name title(new title) '
                  'description(new description) color(mint)`')
    field4desc = ('Fields have a title, and a value. Use this command to '
                  'add fields to your command.\nThe correct syntax for this '
                  'command is: `!commands addfields command_name '
                  'title(new title) value(new value) title(new title)`')
    field5desc = ('You can remove fields by index (starting at 0) with '
                  'this command.\nThe correct syntax for this command is: '
                  '`!commands delfield command_name 0`')
    field6desc = ('This command returns a list of all the commands in this '
                  'server.')
    fields = [{'title': '`!commands new`', 'value': field1desc},
              {'title': '`!commands remove`', 'value': field2desc},
              {'title': '`!commands edit`', 'value': field3desc},
              {'title': '`!commands addfields`', 'value': field4desc},
              {'title': '`!commands delfield`', 'value': field5desc},
              {'title': '`!commands list`', 'value': field6desc}]
    Embed = discord.Embed(description=description,
                          title=title,
                          colour=0x42eef4)
    for field in fields:
        Embed.add_field(name=field['title'], value=field['value'])
    return Embed


def commandcolors():
    colorstring = ['`{}`'.format(c) for c in colors.keys()]
    description = "Here is a list of colors you can use: \n{}".format(
        colorstring)
    Embed = discord.Embed(description=description, colour=0x42eef4)
    return Embed


def badfieldsyntax():
    description = ("Please make sure to specify a *title()* and a *value()* "
                   "for every field to add")
    Embed = discord.Embed(description=description, colour=0xb01e1e)
    return Embed


@embed_command()
async def commands(client, author, message):
    server = message.server
    cc_registerserver(server.id)
    content = message.content
    keyword = content.split(' ')[1]
    if keyword == 'colors':
        return commandcolors()
    elif keyword == 'info':
        return info()
    # !commands new command_name description goes here
    elif keyword == 'new' or keyword == 'add':
        args = content.split(' ', 3)
        command_name = args[2]
        description = args[3]
        return newcommand(server, author, command_name, description)
    # !commands remove command_name
    elif keyword == 'remove':
        args = content.split(' ')
        command_name = args[2]
        return remove(server, author, command_name)
    # !commands edit command_name color()
    elif keyword == 'edit':
        args = content.split(' ', 3)
        # where the parameter
        param_space = args[3]
        command_name = args[2]
        possibleargs = ['color', 'title', 'description', 'url']
        parameters = []
        for arg in possibleargs:
            if arg in param_space:
                # finds the first occurence of arg(
                value_start = param_space.find(arg + '(') + len(arg) + 1
                # finds the paranthesis that belongs to it
                value_end = param_space.find(')', value_start,
                                             len(param_space))
                param_value = param_space[value_start:value_end]
                if arg == 'color':
                    print(param_value)
                    param_value = colors.get(param_value, 0x42eef4)
                    print(param_value)
                parameters.append({'param': arg, 'value': param_value})
        return edit(server, author, command_name, parameters)
    # !commands addfields command_name title() value()
    elif keyword == 'addfields':
        args = content.split(' ', 3)
        command_name = args[2]
        param_space = args[3]
        if param_space.count('title') != param_space.count('value'):
            return badfieldsyntax()

        # returns the first pair of field values in a space
        def getnextfield(space):
            field = {'title': None, 'value': None}
            for value in field:
                value_start = space.find(value + '(') + len(value) + 1
                value_end = space.find(')', value_start, len(space))
                field[value] = space[value_start:value_end]
            return field
        fields = []
        while param_space.replace(' ', '') != '':
            print(param_space)
            if 'title(' not in param_space or 'value(' not in param_space:
                return badfieldsyntax()
            next_field = getnextfield(param_space)
            print(next_field)
            fields.append(next_field)
            param_space = param_space.split(')', 2)[-1]
        return addfields(server, author, command_name, fields)
    # !commands delfield command_name 1
    elif keyword == 'delfield':
        args = content.split(' ')
        command_name = args[2]
        index = int(args[3])
        return removefld(server, author, command_name, index)
    elif keyword == 'list':
        return listcommands(server)
    elif keyword == 'info':
        return info()
