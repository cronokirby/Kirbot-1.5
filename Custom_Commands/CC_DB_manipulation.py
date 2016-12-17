"""
These functions are used to directly manipulate the custom command database.
Commands are registered by server, and contain info necessary to build
a discord Embed object.
Ideally, the database should **only** be opened and edited vie these functions
"""
import json
import os
# to construct embed objects
import discord
# this changes the directory to the directory of this script
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

SLDataBase = ('CC_Database.json')
with open(SLDataBase) as fp:
    Data = json.load(fp)


# serverid must be a string
def cc_registerserver(serverid):
    if serverid not in Data['data']['registeredservers']:
        Data['data']['servers'][serverid] = {}
        Data['data']['registeredservers'].append(serverid)
        with open(SLDataBase, 'w') as fp:
            json.dump(Data, fp)
        return True
    else:
        return("server already registered")


# this function will remove a server that is already registered
def cc_removeserver(serverid):
    if serverid in Data['data']['registeredservers']:
        Data['data']['registeredservers'].remove(serverid)
        Data['data']['servers'].pop(serverid, None)
        with open(SLDataBase, 'w') as fp:
            json.dump(Data, fp)
        return True
    else:
        return('server not registered')


# title needs to be a string, fields need to be a list with
# a "title" / "value" dict as each element
def addcommand(serverid, name, description):
    info = {"title": "",
            "description": description,
            "fields": [],
            "color": 0x42eef4,
            "url": ""}
    Data['data']['servers'][serverid][name] = info
    with open(SLDataBase, 'w') as fp:
        json.dump(Data, fp)


def editparam(serverid, name, param, new_value):
    Data['data']['servers'][serverid][name][param] = new_value
    with open(SLDataBase, 'w') as fp:
        json.dump(Data, fp)


def removecommand(serverid, name):
    success = Data['data']['servers'][serverid].pop(name, False)
    with open(SLDataBase, 'w') as fp:
        json.dump(Data, fp)
    return success


def constructembed(serverid, name):
    info = Data['data']['servers'][serverid][name]
    Embed = discord.Embed(description=info['description'],
                          color=info['color'],
                          title=info['title'],
                          url=info['url'])
    for field in info['fields']:
        Embed.add_field(name=field['title'], value=field['value'])
    return Embed


def appendfields(serverid, command_name, fields):
    if fields is not None:
        Data['data']['servers'][serverid][command_name]['fields'] += fields
    with open(SLDataBase, 'w') as fp:
        json.dump(Data, fp)


def removefield(serverid, command_name, index):
    Data['data']['servers'][serverid][command_name]['fields'].pop(index)
    with open(SLDataBase, 'w') as fp:
        json.dump(Data, fp)


# returns a list of custom command names in that server
def getcommands(serverid):
    return Data['data']['servers'][serverid].keys()


def getregisteredservers():
    return Data['data']['registeredservers']
