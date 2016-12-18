"""
These functions are used to directly manipulate the Permission_Database
This database stores 3 levels of roles per server. Each level has a minimum
role, that a user must have to use commands of that level
Ideally, the database should only be opened in this module.
"""
import json
import os
# this changes the directory to the directory of the script
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)

Perm_DataBase = os.path.join(dname, 'Permission_Database.json')
with open(Perm_DataBase) as fp:
    Data = json.load(fp)


# serverid must be a string, in this, and all functions that use serverid
def Pregisterserver(serverid):
    if not(serverid in Data['data']['registeredservers']):
        Dict = {'1': {'rank': 0, 'name': '@everyone'},
                '2': {'rank': 0, 'name': '@everyone'},
                '3': {'rank': 0, 'name': '@everyone'}}
        Data['data']['servers'][serverid] = Dict
        Data['data']['registeredservers'].append(serverid)
        with open(Perm_DataBase, 'w') as fp:
            json.dump(Data, fp)
        return True
    else:
        return("server already registered")


# this function will remove a server that is already registered
def Premoveserver(serverid):
    if serverid in Data['data']['registeredservers']:
        Data['data']['registeredservers'].remove(serverid)
        Data['data']['servers'].pop(serverid, None)
        with open(Perm_DataBase, 'w') as fp:
            json.dump(Data, fp)
        return True
    else:
        return('server not registered')


# Discord puts server roles in a hierarchy, position represents an index there
def setpermissionlevel(serverid, level, position, rolename):
    level = int(level)
    # level has to be 1,2,3 or you'll get a key error
    Info = {'rank': position, 'name': rolename}
    Data['data']['servers'][serverid][str(level)] = Info
    # now all higher levels need to be higher, and all lower levels as low
    for higherlevel in range(level + 1, 4):
        rank = Data['data']['servers'][serverid][str(higherlevel)]['rank']
        if rank < position:
            Data['data']['servers'][serverid][str(higherlevel)] = Info
    for lowerlevel in range(1, level):
        rank = Data['data']['servers'][serverid][str(lowerlevel)]['rank']
        if rank > position:
            Data['data']['servers'][serverid][str(lowerlevel)] = Info

    with open(Perm_DataBase, 'w') as fp:
        json.dump(Data, fp)


# Pulls the relevant info of a server
def fetchserverinfo(serverid):
    return Data['data']['servers'][serverid]


# level has to be a string
def checkpermissions(serverid, level, user):
    user_rank = user.top_role.position
    necessary_rank = Data['data']['servers'][serverid][str(level)]['rank']
    if user_rank < necessary_rank:
        return False
    else:
        return True
