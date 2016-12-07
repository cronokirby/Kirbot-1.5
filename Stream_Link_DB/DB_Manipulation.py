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
        # if the name isn't in the query, .get returns 0
        name_count = 1 + (Data['data']['stream_query'].get(twitchname, 0))
        Data['data']['stream_query'][twitchname] = name_count
        with open(SLDataBase, 'w') as fp:
            json.dump(Data, fp)


def removestream(serverid, twitchname):
    if twitchname in set(Data['data']['servers'][serverid]['streamlist']):
        Data['data']['servers'][serverid]['streamlist'].remove(twitchname)
        if Data['data']['stream_query'][twitchname] == 1:
            Data['data']['stream_query'].pop(twitchname)
        else:
            Data['data']['stream_query'][twitchname] -= 1
        with open(SLDataBase, 'w') as fp:
            json.dump(Data, fp)


def fetchenabledservers():
    return Data['data']['enabledservers']


def fetchserverinfo(serverid):
        serverinfo = Data['data']['servers'][serverid]
        return serverinfo


# Updates the live_stream list of every server
async def updatestreamlists():
    # All the streams shared by servers
    streams_to_query = [stream for stream in Data['data']['stream_query']]
    # One call to twitch for all servers
    stream_info = await fetchstreaminfolist(streams_to_query)
    for server in Data['data']['enabledservers']:
        stream_list = Data['data'][server]['streamlist']
        # This filters out the streams not in the server.
        live_streams = [stream for stream in stream_info
                        if stream['twitch_name'] in set(stream_list)]
        Data['data'][server]['live_streams'] = live_streams
    with open(SLDataBase, 'w') as fp:
        json.dump(Data, fp)
        
