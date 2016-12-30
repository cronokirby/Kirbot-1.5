"""
These functions server to interact with the database that stores whaled
messages, and whether or not whaling is enabled in a server
"""
import json
import os
import random
# this changes the directory to the directory of the script
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)

Whale_DB = os.path.join(dname, 'Whale_DataBase.json')
with open(Whale_DB) as fp:
    Data = json.load(fp)


def registerserver(serverid):
    if not(serverid in Data['data']['registeredservers']):
        Dict = {'enabled': False, 'whaled_messages': []}
        Data['data']['servers'][serverid] = Dict
        Data['data']['registeredservers'].append(serverid)
        with open(Whale_DB, 'w') as fp:
            json.dump(Data, fp)
        return True
    else:
        return("server already registered")


# this function will remove a server that is already registered
def removeserver(serverid):
    if serverid in Data['data']['registeredservers']:
        Data['data']['registeredservers'].remove(serverid)
        Data['data']['servers'].pop(serverid, None)
        with open(Whale_DB, 'w') as fp:
            json.dump(Data, fp)
        return True
    else:
        return('server not registered')


def toggle(serverid, boolean):
    Data['data']['servers'][serverid]['enabled'] = boolean
    with open(Whale_DB, 'w') as fp:
        json.dump(Data, fp)


# the message has to already be formatted as an Embed
def store_message(serverid, embed_dict):
    Data['data']['servers'][serverid]['whaled_messages'].append(embed_dict)
    with open(Whale_DB, 'w') as fp:
        json.dump(Data, fp)


async def get_messages(serverid):
    return Data['data']['servers'][serverid]['whaled_messages']


# returns an embed dict
async def get_random_message(serverid):
    messages = await get_messages(serverid)
    random_index = random.randrange(0, len(messages))
    messages = await get_messages(serverid)
    return messages[random_index]


def is_registered(serverid):
    return serverid in Data['data']['registeredservers']

def is_enabled(serverid):
    if is_registered(serverid):
        return Data['data']['servers'][serverid]['enabled']
    else:
        return False
