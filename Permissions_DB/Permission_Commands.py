"""
These functions serve as an intemerdiary between users and the Database.
all these functions will be called if the user sends a specific message.
They all take author, and message like arguments, like all the other commands.
All of the commands start with !permissions and then a specific function is
called based on the argument.
"""
# library import
import discord
# Database functions
from Commands import embed_command
from Permissions_DB.Perm_DB_Manipulation import fetchserverinfo,\
    setpermissionlevel, Pregisterserver, checkpermissions
# the permission level for certain commands here
permission_level = 3


# Sorts a set of Discord roles by their position
def hierarchise(roles):
    Dict = {role.position : role.name for role in roles}
    hierarchy = []
    for i in range(0, len(roles)):
        role = Dict.get(i)
        if role is not None:
            hierarchy.append(role)
    return(hierarchy)


# This is an embed returned if the permissions of a user aren't sufficient
def badpermissionembed(server, level):
    level = str(level)
    required_role = fetchserverinfo(server.id)[level]['name']
    description = ("Woops, you don't have permission to use level {} commands "
                   "in {}.\nYou must be of rank `{}` or higher to access those"
                   " commands\nFor more info, use `!permissions list`").format(
        level, server.name, required_role)
    Embed = discord.Embed(description=description, colour=0xb01e1e)
    return Embed


def permission_check(level):
    """
    a decorator that checks if the user meets a required perm level
    If so, the function executes normally, otherwise, the "badpermissionembed"
    is returned instead. server, requester need to be the first 2 args of the
    decorated function
    """
    def decorator(function):
        def checker(*args):
            server = args[0]
            requester = args[1]
            if checkpermissions(server.id, level, requester):
                return function(*args)
            else:
                return badpermissionembed(server, level)
        return checker
    return decorator


@permission_check(permission_level)
def test(server, requester):
    Embed = discord.Embed(description="test", colour=0x42eef4)
    return Embed


# will be called with !permissions info.
# This returns an Embed object with info relating to the stream
def info():
    title = 'Permission info'
    description = ('Permissions are used to only let members of a certain rank'
                   ' or higher have access to certain commands. '
                   'There are only 3 levels of commands.\n'
                   "Here's some more info:")
    field1desc = ("This command allows you to set a certain level of commands "
                  "to be accessible only by members of rank equal to or higher"
                  " than a minimum Role.\n"
                  "The correct syntax for this command is:\n"
                  "`!permissions set level Role`")
    field2desc = ("This command gives you a hierarchy of Roles in your server,"
                  " as well as the minimum Role for each level.\n"
                  "The correct syntax for this command is:\n"
                  "`!permissions list`")
    level1commands = ('`!streams add`, `!streams adds`, `!streams enable`'
                      '`!streams disable`')
    level2commands = ('`!permissions set`')
    fields = [{'title': '`!permissions set`:',
               'value': field1desc},
              {'title': '`!permissions list`',
               'value': field2desc},
              {'title': 'Level 1 commands:',
               'value': level1commands},
              {'title': 'Level 2 commands:',
               'value': level2commands}]

    Embed = discord.Embed(description=description,
                          title=title,
                          colour=0x42eef4)
    for field in fields:
        Embed.add_field(name=field['title'],
                        value=field['value'],
                        inline=True)
    return Embed


# Not to be confused with 'setpermissionlevel'!
# This returns an Embed object for the user, AND runs 'setpermissionlevel'
@permission_check(permission_level)
def permissionset(server, requester, level, position, rolename):
    setpermissionlevel(server.id, level, position, rolename)
    S = ('Permission level {} is now set to `{}`, or higher.\n'
         'Use !permissions list for the role hierarchy.').format(
        level, rolename)
    Embed = discord.Embed(description=S, colour=0x42eef4)
    return Embed


# the server is passed, so that you can fetch other useful info, like the name.
def permissionlist(server):
    server_info = fetchserverinfo(server.id)
    hierarchy = hierarchise(server.roles)
    # This is clearer than list comprehension imo
    Levelranks = {1: server_info['1']['rank'],
                  2: server_info['2']['rank'],
                  3: server_info['3']['rank']}
    # Constructs a list of valid roles for each level
    Levelroles = {}
    for key in range(1, 4):
        Levelroles[key] = []
        for index, role in enumerate(hierarchy):
            if index >= Levelranks[key]:
                Levelroles[key].append(role)

    description = 'Here is some info about the permissions in *{}*:'.format(
        server.name)
    Embed = discord.Embed(description=description, colour=0x42eef4)
    Embed.add_field(name='Hierarchy:',
                    value='`{}`'.format(', '.join(hierarchy)))
    Embed.add_field(name='Level 1:',
                    value='`{}`'.format(', '.join(Levelroles[1])))
    Embed.add_field(name='Level 2:',
                    value='`{}`'.format(', '.join(Levelroles[2])))
    Embed.add_field(name='Level 3:',
                    value='`{}`'.format(', '.join(Levelroles[3])))
    return Embed


# this is the function that the message will trigger
# it directs to one of the above functions based on the 2nd argument
@embed_command()
async def permissions(client, author, message):
    server = message.server
    server_roles = server.roles
    Pregisterserver(server.id)
    args = message.content.split(' ', 3)
    # !permission info
    if args[1] == 'info':
        return info()
    # !permission set level rolename
    elif args[1] == 'set':
        if not(int(args[2]) in range(1, 4)):
            errormsg = ('Woops, please specify a level between 1 and 3\n'
                        'For more info, use `!permissions info`')
            Embed = discord.Embed(description=errormsg, colour=0xb01e1e)
            return Embed
        elif len(args) != 4:
            errormsg = ('Woops, this command only takes 4 arguments\n'
                        'For more info, use `!permissions info`')
            Embed = discord.Embed(description=errormsg, colour=0xb01e1e)
            return Embed
        # This is to allow people to mention `@everyone` without pinging
        args[3] = args[3].replace('`', '')
        # We check if the role exists in the server, and get it's rank
        role_in_server = False
        for role in server_roles:
            if role.name == args[3]:
                role_in_server = True
                rank = role.position
        if role_in_server is False:
            errormsg = ("Woops, the role `{}` doesn't seem to exist :/\n"
                        'For more info, use `!permissions info`').format(
                args[3])
            Embed = discord.Embed(description=errormsg, colour=0xb01e1e)
            return Embed
        # Now, we have checked for all the errors
        # reminder that this returns an Embed object
        return permissionset(server, author, args[2], rank, args[3])
    # !permissions list
    elif args[1] == 'list':
        return permissionlist(server)
