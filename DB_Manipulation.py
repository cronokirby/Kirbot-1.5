"""
These functions are used to directly manipulate the Stream_Link_Database.
This Database serves to act as a link between Discord Names, and twitch names.
Ideally, the database should only be opened in this module.
"""
import json
import os
# Twich api functions, for live_streams
from Twitch_API import fetchstreaminfolist
# this changes the directory to the directory of the script
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

SLDataBase = ('Stream_Link_Database.json')
with open(SLDataBase) as fp:
    Data = json.load(fp)


# serverid must be a string, in this, and all functions that use serverid
def registerserver(serverid):
    if not(serverid in Data['data']['registeredservers']):
        Dict = {'streamlist': [],
                'live_streams': [],
                'channel': None}
        Data['data']['servers'][serverid] = Dict
        Data['data']['registeredservers'].append(serverid)
        with open(SLDataBase, 'w') as fp:
            json.dump(Data, fp)
        return True
    else:
        return("server already registered")


def removeserver(serverid):
    if serverid in Data['data']['registeredservers']:
        Data['data']['registeredservers'].remove(serverid)
        Data['data']['servers'].pop(serverid, None)
        with open(SLDataBase, 'w') as fp:
            json.dump(Data, fp)
        return True
    else:
        return('server not registered')


# This adds a stream of a list of streams to send alerts too
def enableserver(serverid, channelid):
    if not(serverid in set(Data['data']['enabledservers'])):
        Data['data']['enabledservers'].append(serverid)
        Data['data']['servers'][serverid]['channel'] = channelid
    with open(SLDataBase, 'w') as fp:
        json.dump(Data, fp)


# this effectively stops the server from recieving alerts
def disableserver(serverid):
    enabled = Data['data']['enabledservers']
    new_enabled = [server for server in enabled
                   if server != serverid]
    Data['data']['enabledservers'] = new_enabled
    with open(SLDataBase, 'w') as fp:
        json.dump(Data, fp)


# This adds a stream to the list of streams to watch
def addstream(serverid, twitchname):
    if not(twitchname in set(Data['data']['servers'][serverid]['streamlist'])):
        Data['data']['servers'][serverid]['streamlist'].append(twitchname)
        with open(SLDataBase, 'w') as fp:
            json.dump(Data, fp)


def removestream(serverid, twitchname):
    if twitchname in set(Data['data']['servers'][serverid]['streamlist']):
        Data['data']['servers'][serverid]['streamlist'].remove(twitchname)
        with open(SLDataBase, 'w') as fp:
            json.dump(Data, fp)


def fetchenabledservers():
    return Data['data']['enabledservers']


def fetchserverinfo(serverid):
        serverinfo = Data['data']['servers'][serverid]
        return serverinfo


# iterates over all the servers, and adds a list of all streams currently Live
# to their live_streams list. The bot calls this directly.
async def updatestreamlists():
    servers = Data['data']['enabledservers']
    for server in servers:
        stream_list = set(fetchserverinfo(server)['streamlist'])
        list_info = await fetchstreaminfolist(stream_list)
        Data['data']['servers'][server]['live_streams'] = list_info
        with open(SLDataBase, 'w') as fp:
            json.dump(Data, fp)
