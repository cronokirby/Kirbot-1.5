"""
These functions are used to directly manipulate the Stream_Link_Database.
This Database serves to act as a link between Discord Names, and twitch names.
Ideally, the database should only be opened in this module.
"""
import json
import os
# Twich api functions, for live_streams
from Twitch_API import fetchstreaminfolist, findgame
# this changes the directory to the directory of the script
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)

SLDataBase = os.path.join(dname, 'Stream_Link_Database.json')
with open(SLDataBase) as fp:
    Data = json.load(fp)


# serverid must be a string, in this, and all functions that use serverid
def registerserver(serverid):
    if not(serverid in Data['data']['registeredservers']):
        default_info = {'streamlist': [],
                        'live_streams': [],
                        'channel': None,
                        'filters': {'enabled': False, 'list': []}}
        Data['data']['servers'][serverid] = default_info
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
        # each value represents the servers it is in
        if twitchname in set(Data['data']['stream_query']):
            Data['data']['stream_query'][twitchname] += 1
        # this happens if it's not in the query => one server
        else:
            Data['data']['stream_query'][twitchname] = 1
        with open(SLDataBase, 'w') as fp:
            json.dump(Data, fp)


def removestream(serverid, twitchname):
    if twitchname in set(Data['data']['servers'][serverid]['streamlist']):
        Data['data']['servers'][serverid]['streamlist'].remove(twitchname)
        if Data['data']['stream_query'][twitchname] > 1:
            Data['data']['stream_query'][twitchname] -= 1
        else:
            Data['data']['stream_query'].pop(twitchname)
        with open(SLDataBase, 'w') as fp:
            json.dump(Data, fp)


# enables game filtering for stream alerts in that server
def togglefilters(serverid, boolean):
    Data['data']['servers'][serverid]['filters']['enabled'] = boolean
    with open(SLDataBase, 'w') as fp:
        json.dump(Data, fp)


# returns info about the above boolean
def is_enabled(serverid):
    return Data['data']['servers'][serverid]['filters']['enabled']


# adds a new filter to a server's list
# to avoid junk games in the db, game filtering is done at this level
async def addfilter(serverid, gamename):
    # this is False if the game doesn't exist
    twitchname = await findgame(gamename)
    if twitchname:
        if gamename not in set(Data['data']['servers'][serverid]
                               ['filters']['list']):
            Data['data']['servers'][serverid]['filters']['list'].append(
                twitchname)
            with open(SLDataBase, 'w') as fp:
                json.dump(Data, fp)
            return twitchname
    return False


# does the exist opposite. returns a bool noting operation success
def removefilter(serverid, gamename):
    if gamename in set(Data['data']['servers'][serverid]['filters']['list']):
        Data['data']['servers'][serverid]['filters']['list'].remove(gamename)
        return True
    else:
        return False


def getfilters(serverid):
    return Data['data']['servers'][serverid]['filters']['list']


def fetchenabledservers():
    return Data['data']['enabledservers']


def fetchserverinfo(serverid):
        serverinfo = Data['data']['servers'][serverid]
        return serverinfo


# iterates over all the servers, and adds a list of all streams currently Live
# to their live_streams list. The bot calls this directly.
async def updatestreamlists():
    print('updating streams...')
    query_list = [stream for stream in Data['data']['stream_query']]
    # This is the data for the streams shared by all servers
    full_stream_info = await fetchstreaminfolist(query_list)
    for server in Data['data']['enabledservers']:
        stream_list = Data['data']['servers'][server]['streamlist']
        live_streams = [stream for stream in full_stream_info
                        if stream['twitch_name'] in set(stream_list)]
        if Data['data']['servers'][server]['filters']['enabled']:
            filters = Data['data']['servers'][server]['filters']['list']
            live_streams = [stream for stream in live_streams
                            if stream['game'] in set(filters)]
        Data['data']['servers'][server]['live_streams'] = live_streams
        with open(SLDataBase, 'w') as fp:
            json.dump(Data, fp)
    print('streams updated!')
    return full_stream_info
