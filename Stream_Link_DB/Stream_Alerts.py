"""
This module handles the updating of the streams currently live. The bot
calls functions from this module at a set interval.
"""
import discord
# Database functions
from Stream_Link_DB.DB_Manipulation import fetchenabledservers, fetchserverinfo


# This gets called periodically in Main. It returns a list of embeds + channels
# That they need to get sent to. Count is the number of times it's been called.
def alert_generator(old_streams):
    # a list of messages, each being a dict with 'channel' and 'embed' to send
    messages = []
    old_stream_list = {}
    for serverid in fetchenabledservers():
        print('fetching: {}'.format(serverid))
        server_info = fetchserverinfo(serverid)
        # each element in live streams contains the info of the stream
        new_streams = server_info['live_streams']
        old_stream_list[serverid] = new_streams
        # this happens on the first time this gets called
        if old_streams is not None:
            olds = old_streams[serverid]
            # we want to alert streams that are in the new stream list only
            old_statuses = [strm['status'] for strm in olds]
            for stream in new_streams:
                if not(stream['status'] in old_statuses):
                    Embed = discord.Embed(description="", colour=0x9e42f4)
                    Embed.set_author(name=stream["display_name"],
                                     url=stream['URL'])
                    Embed.set_thumbnail(url=stream["logo"])
                    Embed.add_field(name='Game:', value=stream['game'])
                    Embed.add_field(name='Status:', value=stream['status'])
                    # creating a message dict, to append
                    msg = {'embed': Embed,
                           'channel': server_info['channel']}
                    messages.append(msg)
    return {'messages': messages, 'servers': old_stream_list}
